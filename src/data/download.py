"""Baixa e verifica os datasets em data/raw/.

- WESAD: download manual (site oficial da Uni Siegen); este script verifica os arquivos.
- wearable-and-stress: baixado automaticamente do Hugging Face e salvo em CSV.
- IEEE DataPort (TEA): download manual; este script verifica se a pasta tem arquivos.

Uso: python -m src.data.download
Cronograma: dia 1
"""
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

WESAD_DIR = RAW_DIR / "WESAD"
# S1 e S12 foram descartados pelos autores (falha de sensor): restam 15 participantes.
WESAD_SUBJECTS = [f"S{i}" for i in range(2, 18) if i != 12]
WESAD_URL = "https://ubi29.informatik.uni-siegen.de/usi/data_wesad.html"

HF_DATASET = "evannh/wearable-and-stress"
HF_DIR = RAW_DIR / "hf_wearable_stress"

TEA_DIR = RAW_DIR / "ieee_tea"
TEA_URL = (
    "https://ieee-dataport.org/documents/"
    "dataset-heart-rate-predictor-challenging-behaviours-among-children-autism-wearable"
)


def check_wesad() -> bool:
    """Confere se cada participante tem o .pkl sincronizado e os dados brutos da E4."""
    if not WESAD_DIR.is_dir():
        print(f"[WESAD] pasta não encontrada: {WESAD_DIR}")
        print(f"        baixe manualmente em {WESAD_URL} e extraia em {RAW_DIR}")
        return False

    missing = []
    for subject in WESAD_SUBJECTS:
        for name in (f"{subject}.pkl", f"{subject}_E4_Data.zip"):
            if not (WESAD_DIR / subject / name).is_file():
                missing.append(f"{subject}/{name}")

    if missing:
        print(f"[WESAD] faltando {len(missing)} arquivo(s): {', '.join(missing)}")
        return False
    print(f"[WESAD] ok: {len(WESAD_SUBJECTS)} participantes em {WESAD_DIR}")
    return True


def download_hf() -> bool:
    """Baixa o wearable-and-stress e salva um CSV por split."""
    existing = sorted(HF_DIR.glob("*.csv"))
    if existing:
        print(f"[HF] ok: já baixado ({', '.join(p.name for p in existing)})")
        return True

    try:
        from datasets import load_dataset
    except ImportError:
        print("[HF] biblioteca `datasets` não instalada: pip install -r requirements.txt")
        return False

    print(f"[HF] baixando {HF_DATASET}...")
    try:
        dataset = load_dataset(HF_DATASET)
    except Exception as exc:  # rede, dataset removido etc.
        print(f"[HF] erro no download: {exc}")
        return False

    HF_DIR.mkdir(parents=True, exist_ok=True)
    for split, data in dataset.items():
        path = HF_DIR / f"{split}.csv"
        data.to_csv(path, index=False)
        print(f"[HF] {split}: {data.num_rows} linhas -> {path}")
    return True


def check_tea() -> bool:
    """Confere se há arquivos do dataset de TEA (download manual no IEEE DataPort)."""
    files = [p for p in TEA_DIR.rglob("*") if p.is_file() and p.name != ".gitkeep"]
    if not files:
        print(f"[TEA] nenhum arquivo em {TEA_DIR}")
        print(f"      baixe manualmente em {TEA_URL}")
        return False
    print(f"[TEA] ok: {len(files)} arquivo(s) em {TEA_DIR}")
    return True


def main() -> None:
    results = {"WESAD": check_wesad(), "HF": download_hf(), "TEA": check_tea()}
    print()
    print("Resumo:", ", ".join(f"{k} {'ok' if v else 'pendente'}" for k, v in results.items()))


if __name__ == "__main__":
    main()
