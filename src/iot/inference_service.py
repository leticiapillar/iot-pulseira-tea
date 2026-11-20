"""Serviço de inferência: assina escola/sala1/aluno/+/sinais, mantém um buffer
de 60 s por aluno, calibra nos primeiros 5 min, calcula os 18 indicadores a
cada 30 s, roda o modelo e publica em escola/sala1/aluno/<id>/agitacao (retida)
e, pela regra de 2 janelas seguidas >= 0,5, em escola/sala1/alertas (QoS 1).
Contrato das mensagens: Seção 2.3 do relatório.

Privacidade: os sinais brutos ficam só em memória (últimos 75 s). Em disco, o
serviço guarda apenas as probabilidades e os alertas (data/demo/), que o painel
usa como histórico.

Uso:
    python -m src.iot.inference_service
    python -m src.iot.inference_service --modelo models/modelo_estresse.joblib

Cronograma: dia 13
"""
from __future__ import annotations

import argparse
import csv
import json
import threading
from collections import deque
from datetime import datetime
from pathlib import Path

import numpy as np

from src.iot.config import MODELO, ROOT, TOPICO_ALERTAS, cliente_mqtt, topico_agitacao, topico_sinais
from src.models.predict import CALIBRACAO_S, JANELA_S, MARGEM_S, PASSO_S, Detector, indicadores_online

LIMIAR = 0.5
JANELAS_SEGUIDAS = 2
LACUNA_MAX_S = 5          # pacotes perdidos tolerados antes de reiniciar o buffer
HIST_DIR = ROOT / "data" / "demo"


def nivel(prob: float | None) -> str | None:
    if prob is None:
        return None
    return "baixo" if prob < LIMIAR else ("moderado" if prob < 0.8 else "alto")


def _arred(x, casas: int) -> float | None:
    return None if x is None or not np.isfinite(x) else round(float(x), casas)


class Aluno:
    """Estado de uma pulseira: buffer de sinais, calibração e regra de alerta."""

    def __init__(self, aluno: str, caminho_modelo: Path):
        self.aluno = aluno
        self.caminho_modelo = caminho_modelo
        self._reiniciar()

    def _reiniciar(self) -> None:
        """Nova sessão: esvazia o buffer e refaz a calibração."""
        self.detector = Detector(self.caminho_modelo)
        self.buffer: deque[dict] = deque(maxlen=JANELA_S + MARGEM_S)
        self.t_inicio: float | None = None
        self.proxima_decisao: float | None = None
        self.ultimo_seq: int | None = None
        self.ultimo_t: float | None = None
        self.acima = self.abaixo = 0
        self.em_episodio = False

    def receber(self, msg: dict) -> list[tuple[str, dict, int, bool]]:
        """Guarda o pacote; devolve as mensagens a publicar (tópico, conteúdo, qos, retida)."""
        seq, t = msg["seq"], float(msg["t"])
        if self.ultimo_seq is None or seq == 0 or seq < self.ultimo_seq:
            self._reiniciar()                                  # nova sessão: recalibra
            self.t_inicio = t
            self.proxima_decisao = t + JANELA_S
        elif t - self.ultimo_t > 1 + LACUNA_MAX_S:
            # pulseira sem sinal (pacotes perdidos ou desligada): não mistura trechos na janela
            print(f"[{self.aluno}] {t - self.ultimo_t - 1:.0f} s sem sinal: reiniciando o buffer "
                  "(a calibração é mantida)")
            self.buffer.clear()
            self.proxima_decisao = t + JANELA_S
        self.ultimo_t = t
        self.ultimo_seq = seq
        self.buffer.append(msg)

        saida = []
        while t + 1 >= self.proxima_decisao:
            saida += self._decidir(self.proxima_decisao)
            self.proxima_decisao += PASSO_S
        return saida

    def _decidir(self, t_fim: float) -> list[tuple[str, dict, int, bool]]:
        pacotes = [p for p in self.buffer if t_fim - JANELA_S - MARGEM_S <= p["t"] < t_fim]
        if not pacotes:
            return []
        sinais = {k: np.concatenate([np.asarray(p[k], dtype=float) for p in pacotes])
                  for k in ("bvp", "eda", "temp", "acc")}
        f = indicadores_online(sinais, float(pacotes[0]["t"]), t_fim)
        rotulo = pacotes[-1].get("rotulo")
        prob = None
        if t_fim - self.t_inicio <= CALIBRACAO_S:
            self.detector.adicionar_calibracao(f)
            estado = "calibrando"
        elif not self.detector.calibrado and not self.detector.fechar_calibracao():
            estado = "calibrando"                              # poucas janelas boas: estende
            self.detector.adicionar_calibracao(f)
        else:
            prob = self.detector.prever(f)
            estado = "monitorando" if prob is not None else "sinal_ruim"

        saida = []
        agit = {"aluno": self.aluno, "t": t_fim, "sessao": self.t_inicio, "estado": estado,
                "prob": None if prob is None else round(prob, 3), "nivel": nivel(prob),
                "janela_valida": bool(f["janela_valida"]),
                # resumo da janela para o painel (indicadores, não sinais brutos)
                "fc": _arred(f.get("bc__fc_media"), 0), "eda": _arred(f.get("gsr__eda_media"), 2),
                "temp": _arred(f.get("bc__temp_media"), 1)}
        if rotulo is not None:
            agit["rotulo"] = rotulo                            # só na demo (pulseira virtual)
        saida.append((topico_agitacao(self.aluno), agit, 0, True))

        if prob is not None:
            self.acima, self.abaixo = (self.acima + 1, 0) if prob >= LIMIAR else (0, self.abaixo + 1)
            tipo = None
            if not self.em_episodio and self.acima >= JANELAS_SEGUIDAS:
                self.em_episodio, tipo = True, "inicio"
            elif self.em_episodio and self.abaixo >= JANELAS_SEGUIDAS:
                self.em_episodio, tipo = False, "fim"
            if tipo:
                alerta = {"aluno": self.aluno, "t": t_fim, "sessao": self.t_inicio, "tipo": tipo,
                          "prob": round(prob, 3),
                          "nivel": nivel(prob)}
                if rotulo is not None:
                    alerta["rotulo"] = rotulo
                saida.append((TOPICO_ALERTAS, alerta, 1, False))

        hora = datetime.fromtimestamp(t_fim).strftime("%H:%M:%S")
        p_txt = "  -  " if prob is None else f"{prob:.2f}"
        extra = f" | WESAD: {rotulo}" if rotulo else ""
        aviso = f"  >>> ALERTA {saida[-1][1]['tipo'].upper()}" if saida[-1][0] == TOPICO_ALERTAS else ""
        print(f"[{self.aluno}] {hora} {estado:11s} P(estresse) {p_txt}{extra}{aviso}")
        return saida


class Historico:
    """Guarda em CSV só as saídas do modelo (nunca os sinais brutos)."""

    CAMPOS = {"agitacao": ["aluno", "sessao", "t", "estado", "prob", "nivel", "janela_valida",
                           "fc", "eda", "temp", "rotulo"],
              "alertas": ["aluno", "sessao", "t", "tipo", "prob", "nivel", "rotulo"]}

    def __init__(self, pasta: Path = HIST_DIR):
        pasta.mkdir(parents=True, exist_ok=True)
        self.arquivos = {k: pasta / f"{k}.csv" for k in self.CAMPOS}
        self.lock = threading.Lock()
        for tipo, arq in self.arquivos.items():  # arquivo de uma versão anterior: guarda à parte
            if arq.exists():
                with arq.open() as f:
                    cabecalho = f.readline().strip().split(",")
                if cabecalho != self.CAMPOS[tipo]:
                    arq.rename(arq.with_name(f"{tipo}_{int(arq.stat().st_mtime)}_antigo.csv"))

    def gravar(self, tipo: str, msg: dict) -> None:
        arq = self.arquivos[tipo]
        with self.lock:
            novo = not arq.exists()
            with arq.open("a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=self.CAMPOS[tipo], extrasaction="ignore")
                if novo:
                    w.writeheader()
                w.writerow(msg)


def main() -> None:
    ap = argparse.ArgumentParser(description="Serviço de inferência (MQTT → modelo → alertas)")
    ap.add_argument("--modelo", type=Path, default=MODELO)
    args = ap.parse_args()

    det = Detector(args.modelo)
    print(f"Modelo: {args.modelo.relative_to(ROOT) if args.modelo.is_relative_to(ROOT) else args.modelo}")
    if det.excluidos:
        print(f"  (treinado sem {', '.join(det.excluidos)}: os alunos da demo são pessoas que o modelo nunca viu)")

    alunos: dict[str, Aluno] = {}
    historico = Historico()
    cliente = cliente_mqtt("servico-inferencia")

    def ao_receber(c, _userdata, m):
        try:
            msg = json.loads(m.payload)
            aluno = msg["aluno"]
            if aluno not in alunos:
                alunos[aluno] = Aluno(aluno, args.modelo)
                print(f"[{aluno}] nova pulseira: calibrando nos primeiros {CALIBRACAO_S // 60} min (repouso)")
            for topico, conteudo, qos, retida in alunos[aluno].receber(msg):
                c.publish(topico, json.dumps(conteudo), qos=qos, retain=retida)
                historico.gravar("alertas" if topico == TOPICO_ALERTAS else "agitacao", conteudo)
        except Exception as e:  # um pacote ruim não pode derrubar o serviço
            print(f"erro ao processar mensagem de {m.topic}: {e!r}")

    def ao_conectar(c, _userdata, _flags, _rc, _props=None):
        c.subscribe(topico_sinais("+"), qos=0)  # assina de novo a cada reconexão

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber
    print(f"Assinando {topico_sinais('+')}. Ctrl+C para parar.")
    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("encerrado")


if __name__ == "__main__":
    main()
