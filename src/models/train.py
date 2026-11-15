"""Treina e avalia os modelos de detecção de estresse no WESAD.

Tarefa: estresse vs. não estresse (baseline + diversão), como em Schmidt et al. (2018).
Validação: Leave-One-Subject-Out (LOSO). Cada participante é testado por um modelo
que nunca viu dados dele, o que simula usar a pulseira num aluno novo.

Modelos:
    maioria  classificador que sempre responde a classe mais frequente (referência mínima)
    lr       regressão logística (como Goodwin et al., 2019, e Imbiriba et al., 2023)
    lda      análise discriminante linear (melhor modelo de Siirtola, 2019)
    rf       Random Forest (melhor modelo de Schmidt et al., 2018, no pulso)
    xgb      XGBoost

Conjuntos de sensores (plano C): ver `src.data.preprocess.conjuntos`.

Calibração: por padrão, cada indicador vira a diferença em relação à média dos
primeiros 5 min de baseline da própria pessoa (`normalizar_por_baseline`), o que
simula uma calibração em repouso no início do dia. Essas janelas de calibração
ficam FORA da avaliação. Com --sem-normalizacao, usa os valores brutos; para
comparar de forma justa, as janelas de calibração também ficam fora.

Métricas (classe positiva = estresse):
    - agregadas: calculadas juntando as previsões de todos os participantes;
    - por participante: média e desvio padrão entre os 15 folds do LOSO, que
      mostram quanto o desempenho varia de pessoa para pessoa.
A acurácia sozinha engana (o classificador da maioria acerta ~70%), por isso o
foco é F1 macro, acurácia balanceada e AUROC.

Uso:
    python -m src.models.train                          # todos os modelos e conjuntos
    python -m src.models.train --features data/processed/features_wesad_w120_p60.csv
    python -m src.models.train --salvar rf baixo_custo  # salva o modelo final (todos os dados)
Saída: results/metrics/loso_<nome>.csv (resumo) e loso_<nome>_por_participante.csv;
       models/modelo_estresse.joblib (com --salvar)

Cronograma: dia 8
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.data.preprocess import conjuntos, normalizar_por_baseline

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "processed" / "features_wesad.csv"
METRICS_DIR = ROOT / "results" / "metrics"
MODELS_DIR = ROOT / "models"
SEED = 42


def modelos(pos_weight: float) -> dict:
    """Pipelines dos modelos. `pos_weight` = razão não estresse / estresse no treino."""
    imp = lambda: SimpleImputer(strategy="median")  # noqa: E731
    return {
        "maioria": make_pipeline(imp(), DummyClassifier(strategy="most_frequent")),
        "lr": make_pipeline(imp(), StandardScaler(),
                            LogisticRegression(class_weight="balanced", max_iter=2000)),
        "lda": make_pipeline(imp(), StandardScaler(), LinearDiscriminantAnalysis()),
        "rf": make_pipeline(imp(), RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, class_weight="balanced",
            random_state=SEED, n_jobs=-1)),
        "xgb": make_pipeline(imp(), XGBClassifier(
            n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, scale_pos_weight=pos_weight, eval_metric="logloss",
            random_state=SEED, n_jobs=-1)),
    }


def carregar(caminho: Path, normalizar: bool = True) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Janelas válidas com rótulo binário, normalizadas por participante (opcional)."""
    df = pd.read_csv(caminho)
    df = df[df.janela_valida].reset_index(drop=True)
    sets = conjuntos(df.columns)
    todas = sorted({c for cols in sets.values() for c in cols})
    calibrado = normalizar_por_baseline(df, todas)
    if normalizar:
        df = calibrado
    # o período de calibração não é avaliado (também no modo bruto, para comparar)
    df = df[~calibrado.calibracao.to_numpy()]
    df = df[df.estresse.notna()].reset_index(drop=True)
    df["estresse"] = df.estresse.astype(int)
    return df, sets


def _metricas(y: np.ndarray, pred: np.ndarray, prob: np.ndarray) -> dict:
    return {
        "acuracia": accuracy_score(y, pred),
        "acuracia_balanceada": balanced_accuracy_score(y, pred),
        "f1_macro": f1_score(y, pred, average="macro"),
        "f1_estresse": f1_score(y, pred, pos_label=1, zero_division=0),
        "auroc": roc_auc_score(y, prob) if len(np.unique(y)) == 2 else np.nan,
    }


def loso(df: pd.DataFrame, cols: list[str], nome_modelo: str) -> tuple[dict, pd.DataFrame, np.ndarray]:
    """Avaliação LOSO de um modelo num conjunto de indicadores."""
    X, y, g = df[cols].to_numpy(), df.estresse.to_numpy(), df.subject.to_numpy()
    prob = np.zeros(len(y))
    por_part = []
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        pos_weight = (y[tr] == 0).sum() / max((y[tr] == 1).sum(), 1)
        modelo = modelos(pos_weight)[nome_modelo]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            modelo.fit(X[tr], y[tr])
        prob[te] = modelo.predict_proba(X[te])[:, 1]
        pred_te = (prob[te] >= 0.5).astype(int)
        por_part.append({"subject": g[te][0], **_metricas(y[te], pred_te, prob[te])})
    pred = (prob >= 0.5).astype(int)
    return _metricas(y, pred, prob), pd.DataFrame(por_part), prob


def avaliar_tudo(df: pd.DataFrame, sets: dict[str, list[str]],
                 nomes_modelos: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    resumo, por_part, previsoes = [], [], df[["subject", "t_inicio", "condicao", "estresse"]].copy()
    for conj, cols in sets.items():
        for m in nomes_modelos:
            agg, pp, prob = loso(df, cols, m)
            pp.insert(0, "modelo", m)
            pp.insert(0, "conjunto", conj)
            por_part.append(pp)
            previsoes[f"prob__{conj}__{m}"] = prob
            linha = {"conjunto": conj, "modelo": m, "n_indicadores": len(cols), **agg}
            for k in ("f1_macro", "acuracia_balanceada", "auroc"):
                linha[f"{k}_media_part"] = pp[k].mean()
                linha[f"{k}_dp_part"] = pp[k].std()
            resumo.append(linha)
            print(f"  {conj:16s} {m:8s} F1 macro {agg['f1_macro']:.3f} | "
                  f"acur. bal. {agg['acuracia_balanceada']:.3f} | AUROC {agg['auroc']:.3f} | "
                  f"acurácia {agg['acuracia']:.3f}")
    return pd.DataFrame(resumo), pd.concat(por_part, ignore_index=True), previsoes


def salvar_modelo(df: pd.DataFrame, sets: dict, nome_modelo: str, conjunto: str, normalizado: bool) -> Path:
    """Treina com todos os participantes e salva o pipeline para a demo IoT."""
    cols = sets[conjunto]
    y = df.estresse.to_numpy()
    modelo = modelos((y == 0).sum() / (y == 1).sum())[nome_modelo]
    modelo.fit(df[cols].to_numpy(), y)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    caminho = MODELS_DIR / "modelo_estresse.joblib"
    joblib.dump({"modelo": modelo, "indicadores": cols, "conjunto": conjunto,
                 "nome_modelo": nome_modelo, "normalizado_por_baseline": normalizado}, caminho)
    return caminho


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--features", type=Path, default=FEATURES)
    ap.add_argument("--sem-normalizacao", action="store_true")
    ap.add_argument("--modelos", nargs="+", default=["maioria", "lr", "lda", "rf", "xgb"])
    ap.add_argument("--salvar", nargs=2, metavar=("MODELO", "CONJUNTO"),
                    help="treina com todos os dados e salva em models/")
    args = ap.parse_args()

    normalizar = not args.sem_normalizacao
    df, sets = carregar(args.features, normalizar)
    print(f"{args.features.name}: {len(df)} janelas, {df.subject.nunique()} participantes, "
          f"{100 * df.estresse.mean():.1f}% estresse | calibração por baseline: {normalizar}")

    if args.salvar:
        caminho = salvar_modelo(df, sets, *args.salvar, normalizar)
        print(f"modelo salvo em {caminho.relative_to(ROOT)}")
        return

    resumo, por_part, previsoes = avaliar_tudo(df, sets, args.modelos)
    nome = args.features.stem.replace("features_", "") + ("" if normalizar else "_bruto")
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(METRICS_DIR / f"loso_{nome}.csv", index=False)
    por_part.to_csv(METRICS_DIR / f"loso_{nome}_por_participante.csv", index=False)
    previsoes.to_csv(METRICS_DIR / f"loso_{nome}_previsoes.csv", index=False)
    print(f"\nsalvo em results/metrics/loso_{nome}*.csv")


if __name__ == "__main__":
    main()
