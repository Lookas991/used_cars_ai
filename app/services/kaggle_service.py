import os
from kaggle.api.kaggle_api_extended import KaggleApi
from datetime import datetime
from sqlalchemy.orm import Session
from db.models.models import DatasetLog

DATA_DIR = os.path.join("notebooks", "data")
OLLAMA_BLOBS = os.path.join("ollama_data", "models", "blobs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OLLAMA_BLOBS, exist_ok=True)


def _folder_for_ref(dataset_ref: str) -> str:
    safe = dataset_ref.replace("/", "_")
    return os.path.join(DATA_DIR, safe)


def run_kaggle_fetcher(db: Session) -> list[str]:
    api = KaggleApi()
    api.authenticate()
    found = api.dataset_list(
        search="used car", sort_by="hottest", max_size=10)
    downloaded = []
    for d in found:
        ref = d.ref  # "owner/dataset-name"
        folder = _folder_for_ref(ref)
        if os.path.exists(folder):
            # check DB log
            existing = db.query(DatasetLog).filter(
                DatasetLog.ref == ref).first()
            if existing:
                continue
        os.makedirs(folder, exist_ok=True)
        # download into its own folder to avoid mix
        api.dataset_download_files(ref, path=folder, unzip=True)
        # attempt to copy CSVs into ollama blobs area for ingestion
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(".csv"):
                    src = os.path.join(root, f)
                    dst = os.path.join(OLLAMA_BLOBS, f)
                    try:
                        # avoid overwrite unique filenames: add timestamp if exists
                        if os.path.exists(dst):
                            base, ext = os.path.splitext(f)
                            dst = os.path.join(
                                OLLAMA_BLOBS, f"{base}_{int(datetime.utcnow().timestamp())}{ext}")
                        import shutil
                        shutil.copy2(src, dst)
                    except Exception:
                        pass
        # log in DB
        log = DatasetLog(ref=ref, title=d.title, path=folder)
        db.add(log)
        db.commit()
        downloaded.append(folder)
    return downloaded


def run_kaggle_fetcher_wrapper(db: Session):
    # synchronous wrapper for previous function
    return run_kaggle_fetcher(db)
