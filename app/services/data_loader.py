# lightweight dataset inspector/cleaner used before copying to Ollama blobs
import os
import pandas as pd

DATA_DIR = os.path.join("notebooks", "data")
OLLAMA_BLOBS = os.path.join("ollama_data", "models", "blobs")
os.makedirs(OLLAMA_BLOBS, exist_ok=True)

RENAME_MAP = {"model_name": "car_model"}


def discover_csvs():
    out = []
    for root, _, files in os.walk(DATA_DIR):
        for f in files:
            if f.lower().endswith(".csv"):
                out.append(os.path.join(root, f))
    return out


def clean_and_copy_all():
    files = discover_csvs()
    for f in files:
        try:
            df = pd.read_csv(f)
            # rename columns
            df = df.rename(columns=RENAME_MAP)
            # drop rows without price_usd if present
            if "price_usd" in df.columns:
                df = df.dropna(subset=["price_usd"])
            # export to unique filename for Ollama ingestion
            base = os.path.basename(f)
            dst = os.path.join(OLLAMA_BLOBS, base)
            df.to_csv(dst, index=False)
        except Exception as e:
            print("data_loader skip", f, e)
