"""Detecção de estresse em tempo real a partir dos sinais brutos da pulseira.

Usado pelo serviço de inferência (src/iot/inference_service.py). Reaproveita as
mesmas funções do pré-processamento do treino (src/data/preprocess.py), para que
os indicadores calculados na demo sejam os mesmos que o modelo viu no treino.

Diferença em relação ao treino: no treino os filtros foram aplicados à sessão
inteira (não causal). Aqui só se usa o passado: cada janela de 60 s é processada
com uma margem de 15 s de sinal ANTERIOR, para reduzir o efeito de borda dos
filtros. `comparar_com_offline` mede a diferença entre as duas versões.

Verificado em 17/11/2026 (S10 e S15, modelo da demo sem S8, S10 e S15): os
indicadores de EDA, temperatura e movimento saem iguais aos do treino
(correlação ≥ 0,99). Os de FC diferem (correlação 0,5 a 0,98), porque o detector
de batimentos do neurokit2 ajusta seus limiares ao trecho recebido (a sessão
inteira no treino, ~75 s aqui); aumentar a margem para 30 ou 120 s não mudou
isso. A probabilidade média continua separando bem as condições (estresse 0,87
e 0,93; repouso 0,11 e 0,15).

Calibração: igual ao treino. Os indicadores das janelas válidas que terminam nos
primeiros 5 min formam o nível de base da pessoa, que é subtraído das janelas seguintes.

Uso (verificação, sem MQTT):
    python -m src.models.predict S10     # compara indicadores e probabilidades online vs. treino

Cronograma: dia 13
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.data.preprocess import CALIBRACAO_S, batimentos, eda_decomposta, indicadores_janela
from src.data.wesad import WRIST_FS

ROOT = Path(__file__).resolve().parents[2]
MODELO_PADRAO = ROOT / "models" / "modelo_estresse.joblib"
JANELA_S = 60
PASSO_S = 30
MARGEM_S = 15          # sinal anterior à janela usado só para estabilizar os filtros
CALIB_MIN_JANELAS = 3  # janelas válidas mínimas para fechar a calibração


def indicadores_online(sinais: dict[str, np.ndarray], t_inicio_buffer: float, t_fim: float,
                       janela: float = JANELA_S) -> dict:
    """Indicadores da janela [t_fim - janela, t_fim) a partir do buffer de sinais brutos.

    `sinais`: {"bvp": (n,), "eda": (n,), "temp": (n,), "acc": (n, 3)}, todos começando em
    `t_inicio_buffer` (segundos), nas taxas da Empatica E4.
    """
    def serie(nome: str, valores: np.ndarray) -> pd.DataFrame:
        fs = WRIST_FS[nome.upper()]
        return pd.DataFrame({"t": t_inicio_buffer + np.arange(len(valores)) / fs, nome: valores})

    bvp = serie("bvp", np.asarray(sinais["bvp"], dtype=float))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bat = batimentos(bvp)
    bat["t"] += t_inicio_buffer  # batimentos() devolve o tempo relativo ao início do sinal
    eda = eda_decomposta(serie("eda", np.asarray(sinais["eda"], dtype=float)))
    eda["t"] = t_inicio_buffer + np.arange(len(eda)) / WRIST_FS["EDA"]
    temp = serie("temp", np.asarray(sinais["temp"], dtype=float))
    a = np.asarray(sinais["acc"], dtype=float).reshape(-1, 3)
    acc = pd.DataFrame({"t": t_inicio_buffer + np.arange(len(a)) / WRIST_FS["ACC"],
                        "mag": np.sqrt((a ** 2).sum(axis=1))})
    return indicadores_janela(t_fim - janela, t_fim, bat, eda, temp, acc)


class Detector:
    """Calibra pela própria pessoa e devolve a probabilidade de estresse de cada janela."""

    def __init__(self, caminho_modelo: Path | str = MODELO_PADRAO):
        pacote = joblib.load(caminho_modelo)
        self.modelo = pacote["modelo"]
        self.indicadores: list[str] = pacote["indicadores"]
        self.normalizado = pacote["normalizado_por_baseline"]
        self.excluidos = pacote.get("participantes_excluidos", [])
        self._calib: list[np.ndarray] = []
        self.base: np.ndarray | None = None

    @property
    def calibrado(self) -> bool:
        return self.base is not None or not self.normalizado

    def adicionar_calibracao(self, feats: dict) -> None:
        if feats["janela_valida"]:
            self._calib.append(np.array([feats[c] for c in self.indicadores], dtype=float))

    def fechar_calibracao(self) -> bool:
        """Fecha a calibração se houver janelas válidas suficientes."""
        if len(self._calib) < CALIB_MIN_JANELAS:
            return False
        self.base = np.nanmean(np.vstack(self._calib), axis=0)
        return True

    def prever(self, feats: dict) -> float | None:
        """Probabilidade de estresse, ou None se a janela tiver sinal ruim."""
        if not feats["janela_valida"]:
            return None
        x = np.array([feats[c] for c in self.indicadores], dtype=float)
        if self.normalizado:
            x = x - self.base
        return float(self.modelo.predict_proba(x.reshape(1, -1))[0, 1])


# --------------------------------------------------------------------------- verificação
def inicio_sessao(d: dict[str, pd.DataFrame]) -> float:
    """Início do repouso alinhado à grade de 30 s do treino (primeira janela pura do baseline)."""
    t = d["TEMP"].t.to_numpy()
    t_base = t[np.argmax(d["TEMP"].label.to_numpy() == 1)]
    return float(np.ceil(t_base / PASSO_S) * PASSO_S)


def comparar_com_offline(subject: str, caminho_modelo: Path | str = MODELO_PADRAO) -> pd.DataFrame:
    """Reproduz a sessão como a pulseira faria e compara com os indicadores do treino."""
    from src.data.wesad import load_wrist
    from src.models.train import FEATURES

    d = load_wrist(subject)
    fs = {k: WRIST_FS[k] for k in WRIST_FS}
    inicio = inicio_sessao(d)
    off = pd.read_csv(FEATURES)
    off = off[off.subject == subject].set_index("t_inicio")

    det = Detector(caminho_modelo)
    linhas = []
    fim_total = d["TEMP"].t.iloc[-1]
    t_fim = inicio + JANELA_S
    while t_fim <= fim_total:
        t0b = max(inicio, t_fim - JANELA_S - MARGEM_S)
        sinais = {k.lower(): (d[k][["x", "y", "z"]].to_numpy() if k == "ACC" else d[k][k.lower()].to_numpy())
                  [int(round(t0b * fs[k])):int(round(t_fim * fs[k]))] for k in fs}
        f = indicadores_online(sinais, t0b, t_fim)
        calibrando = t_fim - inicio <= CALIBRACAO_S
        prob = None
        if calibrando:
            det.adicionar_calibracao(f)
        else:
            if not det.calibrado:
                det.fechar_calibracao()
            prob = det.prever(f)
        t_ini = round(t_fim - JANELA_S, 6)
        linha = {"t_inicio": t_ini, "calibrando": calibrando, "prob": prob,
                 "valida_online": f["janela_valida"], **{f"on__{c}": f[c] for c in det.indicadores}}
        if t_ini in off.index:
            o = off.loc[t_ini]
            linha.update({"condicao": o.condicao, "valida_offline": o.janela_valida,
                          **{f"off__{c}": o[c] for c in det.indicadores}})
        linhas.append(linha)
        t_fim += PASSO_S
    return pd.DataFrame(linhas)


def main() -> None:
    subject = sys.argv[1] if len(sys.argv) > 1 else "S10"
    modelo = sys.argv[2] if len(sys.argv) > 2 else MODELO_PADRAO
    r = comparar_com_offline(subject, modelo)
    r = r[r.condicao.notna()]
    print(f"{subject}: {len(r)} janelas com correspondente no treino")
    print(f"validade igual em {100 * (r.valida_online == r.valida_offline).mean():.1f}% das janelas")
    for c in Detector(modelo).indicadores:
        a, b = r[f"on__{c}"].astype(float), r[f"off__{c}"].astype(float)
        print(f"  {c:22s} correlação online x treino {a.corr(b):.3f}")
    ok = r[r.prob.notna() & r.condicao.isin(["baseline", "diversao", "estresse"])]
    print("\nprobabilidade média por condição (online):")
    print(ok.groupby("condicao").prob.agg(["mean", "count"]).round(3))


if __name__ == "__main__":
    main()
