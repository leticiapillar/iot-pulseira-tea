"""Pulseira virtual: reproduz os sinais de pulso do WESAD como se fosse
a pulseira ESP32, publicando um pacote por segundo no broker MQTT.

Tópico: escola/sala1/aluno/<id>/sinais (QoS 0)
Formato da mensagem: Seção 2.3 do relatório (docs/relatorio/02_arquitetura_metodologia.md)

A sessão começa no repouso (os 5 primeiros minutos servem de calibração). O
campo "rotulo" existe só na pulseira virtual (condição do protocolo do WESAD,
para o painel mostrar a verdade); o serviço de inferência não o usa.

Uso:
    python -m src.iot.virtual_wristband                       # aluno01 (S10), 10x mais rápido
    python -m src.iot.virtual_wristband --aluno aluno02 --velocidade 30
    python -m src.iot.virtual_wristband --curta               # calibração e depois pula para
                                                              # 4 min antes do estresse (vídeo)

Cronograma: dia 13
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from src.data.wesad import LABELS, WRIST_FS, load_wrist
from src.iot.config import ALUNOS_DEMO, cliente_mqtt, topico_sinais
from src.models.predict import inicio_sessao

CALIBRACAO_S = 300
ANTES_DO_ESTRESSE_S = 240


def roteiro(d: dict, curta: bool) -> list[int]:
    """Segundos da sessão (desde t=0 do registro) que serão enviados, em ordem."""
    ini = int(inicio_sessao(d))
    fim = int(d["TEMP"].t.iloc[-1])
    if not curta:
        return list(range(ini, fim))
    rot = d["TEMP"].label.to_numpy()
    t_est = int(d["TEMP"].t.to_numpy()[np.argmax(rot == 2)])
    fim_est = int(d["TEMP"].t.to_numpy()[len(rot) - 1 - np.argmax(rot[::-1] == 2)])
    calib = list(range(ini, ini + CALIBRACAO_S + 60))
    return calib + list(range(max(calib[-1] + 1, t_est - ANTES_DO_ESTRESSE_S), min(fim, fim_est + 300)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Pulseira virtual (WESAD → MQTT)")
    ap.add_argument("--aluno", default="aluno01", choices=sorted(ALUNOS_DEMO))
    ap.add_argument("--velocidade", type=float, default=float(os.getenv("REPLAY_SPEED", "10")),
                    help="vezes mais rápido que o tempo real")
    ap.add_argument("--curta", action="store_true",
                    help="depois da calibração, pula para 4 min antes do estresse")
    args = ap.parse_args()

    participante = ALUNOS_DEMO[args.aluno]
    print(f"Carregando {participante} do WESAD como {args.aluno}...")
    d = load_wrist(participante)
    segundos = roteiro(d, args.curta)
    cliente = cliente_mqtt(f"pulseira-{args.aluno}")
    cliente.loop_start()
    topico = topico_sinais(args.aluno)
    print(f"Publicando {len(segundos)} pacotes em {topico} ({args.velocidade:g}x; "
          f"~{len(segundos) / args.velocidade / 60:.1f} min). Ctrl+C para parar.")

    # relógio da pulseira = tempo da sessão do WESAD: quando o roteiro pula um trecho, o tempo
    # também pula, e o serviço de inferência trata como "pulseira sem sinal" (não mistura trechos)
    t_relogio = time.time() - segundos[0]
    inicio = time.monotonic()
    try:
        for k, s in enumerate(segundos):
            msg = {"aluno": args.aluno, "seq": k, "t": round(t_relogio + s, 3)}
            for nome, fs in WRIST_FS.items():
                df = d[nome].iloc[s * fs:(s + 1) * fs]
                if nome == "ACC":
                    msg["acc"] = np.round(df[["x", "y", "z"]].to_numpy(), 4).tolist()
                else:
                    msg[nome.lower()] = np.round(df[nome.lower()].to_numpy(dtype=float), 4).tolist()
            if k and s != segundos[k - 1] + 1:
                print(f"  (pulando {s - segundos[k - 1] - 1} s da sessão, até perto do estresse)")
            msg["rotulo"] = LABELS.get(int(d["TEMP"].label.iloc[s * WRIST_FS["TEMP"]]), "transicao")
            cliente.publish(topico, json.dumps(msg), qos=0)
            if k % 60 == 0:
                print(f"  {(s - segundos[0]) // 60:3d} min de sessão | condição do WESAD: {msg['rotulo']}")
            espera = inicio + (k + 1) / args.velocidade - time.monotonic()
            if espera > 0:
                time.sleep(espera)
    except KeyboardInterrupt:
        print("interrompido")
    finally:
        cliente.loop_stop()
        cliente.disconnect()


if __name__ == "__main__":
    main()
