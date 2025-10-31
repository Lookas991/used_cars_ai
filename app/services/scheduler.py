import asyncio
from database import SessionLocal
from services.kaggle_service import run_kaggle_fetcher
from sqlalchemy.orm import Session

SLEEP_SECONDS = 24 * 3600  # daily


async def scheduler():
    while True:
        try:
            db: Session = SessionLocal()
            try:
                print("[scheduler] running kaggle fetcher")
                run_kaggle_fetcher(db)
            finally:
                db.close()
        except Exception as e:
            print("[scheduler] error:", e)
        await asyncio.sleep(SLEEP_SECONDS)
