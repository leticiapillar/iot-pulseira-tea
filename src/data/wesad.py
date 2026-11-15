"""Leitura dos sinais de pulso (Empatica E4) do WESAD.

O arquivo SX.pkl de cada participante traz os sinais do peito (RespiBAN, 700 Hz),
os sinais do pulso (E4) e um rótulo por amostra a 700 Hz. Aqui usamos só o pulso,
que é o que uma pulseira escolar teria, e alinhamos o rótulo à taxa de cada sinal.

Uso:
    from src.data.wesad import load_wrist
    sig = load_wrist("S2")        # dict: {"BVP": DataFrame, "EDA": ..., "TEMP": ..., "ACC": ...}
"""
from __future__ import annotations

import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WESAD_DIR = ROOT / "data" / "raw" / "WESAD"
CACHE_DIR = ROOT / "data" / "processed" / "wesad_wrist"

# S1 e S12 foram descartados pelos autores (falha de sensor).
SUBJECTS = [f"S{i}" for i in range(2, 18) if i != 12]

LABEL_FS = 700  # Hz, taxa do RespiBAN, à qual os rótulos estão sincronizados
WRIST_FS = {"BVP": 64, "EDA": 4, "TEMP": 4, "ACC": 32}  # Hz

# Protocolo do WESAD (readme oficial): 0 = transição, 5/6/7 = ignorar.
LABELS = {1: "baseline", 2: "estresse", 3: "diversao", 4: "meditacao"}

# Unidades do E4: BVP sem unidade física, EDA em µS, TEMP em °C, ACC em 1/64 g.
ACC_SCALE = 1 / 64


def _align_labels(labels_700hz: np.ndarray, n_samples: int, fs: int) -> np.ndarray:
    """Pega o rótulo do instante de cada amostra do sinal de taxa `fs`."""
    idx = np.round(np.arange(n_samples) * LABEL_FS / fs).astype(int)
    idx = np.clip(idx, 0, len(labels_700hz) - 1)
    return labels_700hz[idx]


def _from_pickle(subject: str) -> dict[str, pd.DataFrame]:
    path = WESAD_DIR / subject / f"{subject}.pkl"
    with open(path, "rb") as f:
        raw = pickle.load(f, encoding="latin1")

    wrist = raw["signal"]["wrist"]
    labels = np.asarray(raw["label"]).ravel()
    out = {}
    for name, fs in WRIST_FS.items():
        data = np.asarray(wrist[name], dtype=np.float32)
        cols = ["x", "y", "z"] if name == "ACC" else [name.lower()]
        df = pd.DataFrame(data, columns=cols)
        if name == "ACC":
            df[cols] *= ACC_SCALE
            df["mag"] = np.sqrt((df[cols] ** 2).sum(axis=1))
        df.insert(0, "t", np.arange(len(df), dtype=np.float64) / fs)
        df["label"] = _align_labels(labels, len(df), fs).astype(np.int8)
        out[name] = df
    return out


def load_wrist(subject: str, use_cache: bool = True) -> dict[str, pd.DataFrame]:
    """Sinais de pulso de um participante, com tempo (s) e rótulo alinhado.

    Na primeira leitura o .pkl (cerca de 1 GB, quase todo do peito) é aberto e
    só o pulso é salvo em cache em data/processed/wesad_wrist/ (alguns MB).
    """
    cache = CACHE_DIR / f"{subject}.pkl"
    if use_cache and cache.is_file():
        return pd.read_pickle(cache)
    out = _from_pickle(subject)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(out, cache)
    return out


def subject_info(subject: str) -> dict:
    """Idade, gênero, mão dominante e observações do SX_readme.txt."""
    text = (WESAD_DIR / subject / f"{subject}_readme.txt").read_text(encoding="latin1")

    def field(name: str) -> str | None:
        m = re.search(rf"{name}:\s*(.+)", text)
        return m.group(1).strip() if m else None

    notes = text.split("### Additional notes ###")[-1].strip()
    return {
        "subject": subject,
        "idade": int(field("Age")) if field("Age") else None,
        "genero": field("Gender"),
        "mao_dominante": field("Dominant hand"),
        "observacoes": notes or None,
    }
