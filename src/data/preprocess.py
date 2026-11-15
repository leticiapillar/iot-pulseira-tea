"""Pré-processamento dos sinais de pulso do WESAD: janelas e indicadores.

Etapas (decisões justificadas na seção 8 do notebook 01_exploracao_wesad):
1. Batimentos: picos do BVP (neurokit2) → intervalos entre batimentos (IBI).
   IBIs fora de 40–180 bpm são ruído. Para a HRV, também se descartam IBIs que
   variam mais de 20% em relação ao anterior (artefato de movimento).
2. EDA: filtro passa-baixa de 1 Hz; componente tônica e fásica (filtro
   passa-alta do neurokit2); picos de resposta (SCR) com proeminência ≥ 0,01 µS,
   limiar absoluto clássico, para a contagem ser comparável entre pessoas.
3. Janelas de 60 s com passo de 30 s, só com rótulo puro (sem misturar condições).
4. Indicadores agrupados pelo hardware necessário para medi-los (plano C):
     bc__   baixo custo: FC, temperatura e movimento (bc__fc_* = só sensor de pulso)
     gsr__  sensor de condutância da pele (EDA)
     hrv__  variabilidade da FC: calculada e salva, mas FORA dos conjuntos (ver abaixo)
   Os conjuntos do experimento central são definidos em `conjuntos`.

Por que a HRV ficou de fora (verificado em 15/11/2026): com os picos do BVP, o
RMSSD médio deu 137 ms no baseline e 228 ms no estresse, valores implausíveis e na
direção oposta à fisiologia (o estresse reduz a HRV). É ruído de movimento, pois
no TSST a pessoa fala e gesticula. Os IBIs calculados pela própria Empatica E4
(IBI.csv) cobrem em média menos de 10% do tempo de estresse (0% em vários
participantes): nem o equipamento de pesquisa mede a HRV pelo pulso nessa
condição. Usar o IBI.csv seria pior, porque a falta de dado viraria um indicador
de estresse (vazamento).
5. Qualidade: a janela é marcada como inválida se mais de 20% dos batimentos
   forem ruído ou se houver menos de 30 batimentos válidos.

A calibração por participante (diferença em relação aos primeiros 5 min de
baseline da própria pessoa) NÃO é aplicada no CSV: ela
fica em `normalizar_por_baseline`, para o treino decidir quando usá-la. Os valores salvos são brutos, nas unidades físicas.

Observação: os filtros são aplicados ao sinal inteiro de cada participante (não
causais). Num uso em tempo real, a filtragem teria de ser causal; isso não afeta
a avaliação LOSO, porque cada participante é processado de forma independente.

Uso:
    python -m src.data.preprocess                     # janelas de 60 s, passo 30 s
    python -m src.data.preprocess --janela 120 --passo 60
Saída: data/processed/features_wesad.csv (ou features_wesad_w120.csv etc.)

Cronograma: dia 7
"""
from __future__ import annotations

import argparse
from pathlib import Path

import neurokit2 as nk
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks

from src.data.wesad import LABELS, SUBJECTS, WRIST_FS, load_wrist

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "processed"

FC_MIN, FC_MAX = 40, 180            # bpm aceitáveis
IBI_VAR_MAX = 0.20                  # variação máxima entre IBIs consecutivos (HRV)
RUIDO_MAX = 0.20                    # fração máxima de batimentos ruidosos por janela
BATIMENTOS_MIN = 30                 # batimentos válidos mínimos por janela
SCR_PROEMINENCIA = 0.01             # µS
EDA_CORTE_HZ = 1.0

ESTRESSE = 2
NAO_ESTRESSE = (1, 3)               # baseline + diversão (como em Schmidt et al., 2018)

COLS_ID = ["subject", "t_inicio", "janela_s", "label", "condicao", "estresse", "janela_valida", "frac_ruido_fc"]


def conjuntos(colunas) -> dict[str, list[str]]:
    """Colunas de indicadores de cada conjunto de sensores do experimento central.

    so_fc            só um sensor óptico de pulso (como um relógio barato)
    baixo_custo      pulso + temperatura + acelerômetro (ESP32 com sensores comuns)
    baixo_custo_eda  o anterior + sensor de condutância da pele (GSR)
    """
    fc = [c for c in colunas if c.startswith("bc__fc_")]
    bc = [c for c in colunas if c.startswith("bc__")]
    gsr = [c for c in colunas if c.startswith("gsr__")]
    return {"so_fc": fc, "baixo_custo": bc, "baixo_custo_eda": bc + gsr}


# --------------------------------------------------------------------------- sinais
def batimentos(bvp: pd.DataFrame, fs: int = WRIST_FS["BVP"]) -> pd.DataFrame:
    """Um registro por batimento: instante (s), IBI (s) e flags de qualidade."""
    limpo = nk.ppg_clean(bvp["bvp"].to_numpy(dtype=float), sampling_rate=fs)
    picos = nk.ppg_findpeaks(limpo, sampling_rate=fs)["PPG_Peaks"]
    ibi = np.diff(picos) / fs
    fc = 60 / ibi
    valido = (fc >= FC_MIN) & (fc <= FC_MAX)
    var = np.r_[np.nan, np.abs(np.diff(ibi)) / ibi[:-1]]
    return pd.DataFrame({
        "t": picos[1:] / fs,
        "ibi": ibi,
        "valido": valido,
        # para HRV: válido, anterior válido e variação ≤ 20%
        "valido_hrv": valido & np.r_[False, valido[:-1]] & (var <= IBI_VAR_MAX),
    })


def eda_decomposta(eda: pd.DataFrame, fs: int = WRIST_FS["EDA"]) -> pd.DataFrame:
    """EDA filtrada, componentes tônica e fásica e marcação dos picos (SCR)."""
    b, a = butter(4, EDA_CORTE_HZ, btype="low", fs=fs)
    filtrada = filtfilt(b, a, eda["eda"].to_numpy(dtype=float))
    comp = nk.eda_phasic(filtrada, sampling_rate=fs, method="highpass")
    fasica = comp["EDA_Phasic"].to_numpy()
    picos, props = find_peaks(fasica, prominence=SCR_PROEMINENCIA, distance=fs)
    pico = np.zeros(len(fasica), dtype=bool)
    pico[picos] = True
    amp = np.zeros(len(fasica))
    amp[picos] = props["prominences"]
    return pd.DataFrame({"t": eda["t"].to_numpy(), "eda": filtrada,
                         "tonica": comp["EDA_Tonic"].to_numpy(), "fasica": fasica,
                         "pico": pico, "amp": amp})


def _inclinacao(t: np.ndarray, y: np.ndarray) -> float:
    """Inclinação da reta ajustada, em unidades por minuto."""
    if len(y) < 3:
        return np.nan
    return float(np.polyfit(t / 60, y, 1)[0])


# --------------------------------------------------------------------------- janelas
def janelas_puras(label: pd.DataFrame, fs: int, janela: float, passo: float) -> list[tuple[float, int]]:
    """Inícios (s) das janelas cujo rótulo é único e está em LABELS."""
    lab = label["label"].to_numpy()
    n_jan, n_passo = int(janela * fs), int(passo * fs)
    out = []
    for ini in range(0, len(lab) - n_jan + 1, n_passo):
        trecho = lab[ini:ini + n_jan]
        if trecho[0] in LABELS and (trecho == trecho[0]).all():
            out.append((ini / fs, int(trecho[0])))
    return out


def indicadores_janela(t0: float, t1: float, bat: pd.DataFrame, eda: pd.DataFrame,
                       temp: pd.DataFrame, acc: pd.DataFrame) -> dict:
    b = bat[(bat.t >= t0) & (bat.t < t1)]
    bv = b[b.valido]
    bh = b[b.valido_hrv]
    fc = 60 / bv.ibi.to_numpy()
    e = eda[(eda.t >= t0) & (eda.t < t1)]
    tp = temp[(temp.t >= t0) & (temp.t < t1)]
    ac = acc[(acc.t >= t0) & (acc.t < t1)]
    ibi_ms = bh.ibi.to_numpy() * 1000
    d_ibi = np.diff(ibi_ms)
    frac_ruido = 1 - len(bv) / len(b) if len(b) else 1.0
    dur_min = (t1 - t0) / 60

    return {
        "frac_ruido_fc": frac_ruido,
        "janela_valida": bool(frac_ruido <= RUIDO_MAX and len(bv) >= BATIMENTOS_MIN),
        # ---- baixo custo: FC, temperatura e movimento
        "bc__fc_media": fc.mean() if len(fc) else np.nan,
        "bc__fc_mediana": np.median(fc) if len(fc) else np.nan,
        "bc__fc_dp": fc.std() if len(fc) else np.nan,
        "bc__fc_min": fc.min() if len(fc) else np.nan,
        "bc__fc_max": fc.max() if len(fc) else np.nan,
        "bc__temp_media": tp.temp.mean(),
        "bc__temp_dp": tp.temp.std(),
        "bc__temp_inclinacao": _inclinacao(tp.t.to_numpy(), tp.temp.to_numpy()),
        "bc__acc_media": ac.mag.mean(),
        "bc__acc_dp": ac.mag.std(),
        "bc__acc_p95": ac.mag.quantile(0.95),
        # ---- sensor de condutância da pele (GSR)
        "gsr__eda_media": e.eda.mean(),
        "gsr__eda_dp": e.eda.std(),
        "gsr__eda_inclinacao": _inclinacao(e.t.to_numpy(), e.eda.to_numpy()),
        "gsr__scl_media": e.tonica.mean(),
        "gsr__scr_por_min": e.pico.sum() / dur_min,
        "gsr__scr_amp_media": e.amp[e.pico].mean() if e.pico.any() else 0.0,
        "gsr__fasica_dp": e.fasica.std(),
        # ---- HRV (domínio do tempo; 60 s é curto demais para LF/HF confiável)
        "hrv__ibi_media_ms": ibi_ms.mean() if len(ibi_ms) else np.nan,
        "hrv__sdnn_ms": ibi_ms.std() if len(ibi_ms) > 1 else np.nan,
        "hrv__rmssd_ms": np.sqrt(np.mean(d_ibi ** 2)) if len(d_ibi) else np.nan,
        "hrv__pnn50": 100 * np.mean(np.abs(d_ibi) > 50) if len(d_ibi) else np.nan,
    }


def processar_participante(subject: str, janela: float = 60, passo: float = 30) -> pd.DataFrame:
    d = load_wrist(subject)
    bat = batimentos(d["BVP"])
    eda = eda_decomposta(d["EDA"])
    linhas = []
    for t0, lab in janelas_puras(d["TEMP"], WRIST_FS["TEMP"], janela, passo):
        feats = indicadores_janela(t0, t0 + janela, bat, eda, d["TEMP"], d["ACC"])
        linhas.append({
            "subject": subject, "t_inicio": t0, "janela_s": janela, "label": lab, "condicao": LABELS[lab],
            "estresse": 1 if lab == ESTRESSE else (0 if lab in NAO_ESTRESSE else np.nan),
            **feats,
        })
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------- normalização
CALIBRACAO_S = 300  # minutos iniciais de baseline usados para calibrar (5 min)


def normalizar_por_baseline(df: pd.DataFrame, colunas: list[str],
                            calibracao_s: float = CALIBRACAO_S, modo: str = "centro") -> pd.DataFrame:
    """Calibra cada indicador pelo início do baseline da mesma pessoa.

    Simula a calibração na escola: os primeiros `calibracao_s` segundos de
    repouso definem o nível de base da pessoa, e só o que vem DEPOIS é
    avaliado. As janelas que começam dentro do período de calibração recebem
    `calibracao=True` e devem ficar fora da avaliação; caso contrário, o
    baseline seria normalizado com as próprias janelas e pareceria "perfeito".

    modo="centro" (padrão): subtrai a média da calibração (diferença em relação
        ao repouso, na unidade original).
    modo="z": também divide pelo desvio padrão da calibração. Foi testado em
        15/11/2026 e piorou os conjuntos de baixo custo (F1 macro de ~0,83 para
        ~0,78): com 5 min, o desvio padrão é instável e infla os valores.

    Usa só dados do próprio participante, então pode ser aplicada antes da
    divisão LOSO sem vazar informação entre pessoas.
    """
    out = df.copy()
    out["calibracao"] = False
    for _, g in df.groupby("subject"):
        base = g[g.label == 1]
        ini = base.t_inicio.min()
        calib = base[base.t_inicio + base.janela_s <= ini + calibracao_s]
        valores = g[colunas] - calib[colunas].mean()
        if modo == "z":
            valores = valores / calib[colunas].std().replace(0, np.nan)
        out.loc[g.index, colunas] = valores
        out.loc[base.index[base.t_inicio < ini + calibracao_s], "calibracao"] = True
    return out


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--janela", type=float, default=60, help="duração da janela (s)")
    ap.add_argument("--passo", type=float, default=30, help="passo entre janelas (s)")
    args = ap.parse_args()

    partes = []
    for s in SUBJECTS:
        df = processar_participante(s, args.janela, args.passo)
        partes.append(df)
        print(f"{s:>4}: {len(df):3d} janelas | inválidas {(~df.janela_valida).sum():2d} | "
              f"estresse {int((df.estresse == 1).sum()):2d} | não estresse {int((df.estresse == 0).sum()):3d}")
    feats = pd.concat(partes, ignore_index=True)

    sufixo = "" if (args.janela, args.passo) == (60, 30) else f"_w{int(args.janela)}_p{int(args.passo)}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saida = OUT_DIR / f"features_wesad{sufixo}.csv"
    feats.to_csv(saida, index=False)

    bin_ = feats[feats.estresse.notna()]
    print(f"\n{len(feats)} janelas ({len(bin_)} na tarefa binária, "
          f"{100 * bin_.estresse.mean():.1f}% estresse) | inválidas: {(~feats.janela_valida).sum()}")
    for nome, cols in conjuntos(feats.columns).items():
        print(f"  {nome:16s} {len(cols):2d} indicadores")
    print(f"salvo em {saida.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
