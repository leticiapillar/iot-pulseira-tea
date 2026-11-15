"""Indicadores de inclusão escolar a partir dos microdados do Censo Escolar 2025 (Inep).

Gera os números citados na Seção 1.2 do relatório (Contextualização):
percentual de turmas com aluno da educação especial, presença de profissional
de apoio, sala de recursos, psicólogo e formação dos docentes.

Os microdados são agregados por escola e NÃO separam o TEA: "educação especial"
inclui deficiência, TEA e altas habilidades/superdotação.

Dados: baixar os microdados do Censo Escolar 2025 no portal do Inep e extrair em
docs/referencias/microdados_censo_escolar_2025_v2/ (pasta ignorada pelo git).

Uso: python -m src.data.contexto_censo_escolar [pasta_dados]
Saída: tabela no terminal e results/metrics/contexto_censo_escolar_2025.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DADOS = ROOT / "docs" / "referencias" / "microdados_censo_escolar_2025_v2" / "dados"
SAIDA = ROOT / "results" / "metrics" / "contexto_censo_escolar_2025.csv"

NAO_INFORMADO = 88888  # código do Inep para valor não informado em colunas QT_PROF_*

# Dependência administrativa: 1 federal, 2 estadual, 3 municipal, 4 privada
PUBLICA = [1, 2, 3]
PRIVADA = [4]


def _ler(pasta: Path, arquivo: str, colunas: list[str]) -> pd.DataFrame:
    return pd.read_csv(pasta / arquivo, sep=";", encoding="latin1", usecols=colunas, low_memory=False)


def carregar(pasta: Path = DADOS) -> pd.DataFrame:
    """Uma linha por escola em atividade, com as colunas usadas nos indicadores."""
    escola = _ler(pasta, "Tabela_Escola_2025_V2.csv",
                  ["CO_ENTIDADE", "SG_UF", "TP_SITUACAO_FUNCIONAMENTO", "TP_DEPENDENCIA",
                   "IN_SALA_ATENDIMENTO_ESPECIAL", "TP_AEE", "QT_PROF_PSICOLOGO"])
    matricula = _ler(pasta, "Tabela_Matricula_2025_V2.csv",
                     ["CO_ENTIDADE", "QT_MAT_BAS", "QT_MAT_ESP", "QT_MAT_ESP_CC"])
    docente = _ler(pasta, "Tabela_Docente_2025_V2.csv",
                   ["CO_ENTIDADE", "QT_DOC_BAS", "QT_DOC_BAS_APOIO_PCD", "QT_DOC_BAS_ESPEC_ED_ESPECIAL"])
    turma = _ler(pasta, "Tabela_Turma_2025_V2.csv", ["CO_ENTIDADE", "QT_TUR_BAS", "QT_TUR_ESP_CC"])

    df = (escola.merge(matricula, on="CO_ENTIDADE", how="left")
                .merge(docente, on="CO_ENTIDADE", how="left")
                .merge(turma, on="CO_ENTIDADE", how="left"))
    df = df[df.TP_SITUACAO_FUNCIONAMENTO == 1]  # em atividade
    df.loc[df.QT_PROF_PSICOLOGO == NAO_INFORMADO, "QT_PROF_PSICOLOGO"] = pd.NA
    return df[df.QT_MAT_BAS > 0]  # escolas com matrícula na educação básica


def indicadores(df: pd.DataFrame) -> dict:
    # "inc" = escolas com ao menos um aluno da educação especial em classe comum
    inc = df[df.QT_MAT_ESP_CC > 0]
    return {
        "escolas com matrícula": len(df),
        "matrículas educação básica": int(df.QT_MAT_BAS.sum()),
        "matrículas educação especial": int(df.QT_MAT_ESP.sum()),
        "% educação especial na básica": 100 * df.QT_MAT_ESP.sum() / df.QT_MAT_BAS.sum(),
        "% educação especial em classe comum": 100 * df.QT_MAT_ESP_CC.sum() / df.QT_MAT_ESP.sum(),
        "% escolas com aluno da ed. especial em classe comum": 100 * len(inc) / len(df),
        "% turmas com aluno da ed. especial em classe comum": 100 * df.QT_TUR_ESP_CC.sum() / df.QT_TUR_BAS.sum(),
        "[inc] % com sala de recursos (AEE)": 100 * (inc.IN_SALA_ATENDIMENTO_ESPECIAL == 1).mean(),
        "[inc] % que oferecem AEE": 100 * (inc.TP_AEE > 0).mean(),
        "[inc] % com psicólogo escolar": 100 * (inc.QT_PROF_PSICOLOGO.dropna() > 0).mean(),
        "[inc] % com profissional de apoio escolar": 100 * (inc.QT_DOC_BAS_APOIO_PCD > 0).mean(),
        "[inc] alunos da ed. especial em classe comum por profissional de apoio":
            inc.QT_MAT_ESP_CC.sum() / inc.QT_DOC_BAS_APOIO_PCD.sum(),
        # vínculos docente-escola: quem leciona em duas escolas conta duas vezes
        "[inc] % docentes com formação continuada em ed. especial":
            100 * inc.QT_DOC_BAS_ESPEC_ED_ESPECIAL.sum() / inc.QT_DOC_BAS.sum(),
    }


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else DADOS
    df = carregar(pasta)
    tabela = pd.DataFrame({
        "Brasil": indicadores(df),
        "RS": indicadores(df[df.SG_UF == "RS"]),
        "Brasil pública": indicadores(df[df.TP_DEPENDENCIA.isin(PUBLICA)]),
        "Brasil privada": indicadores(df[df.TP_DEPENDENCIA.isin(PRIVADA)]),
    }).round(1)
    pd.set_option("display.width", 200)
    print(tabela.to_string())
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA)
    print(f"\nsalvo em {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
