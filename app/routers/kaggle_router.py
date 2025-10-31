from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.kaggle_service import run_kaggle_fetcher

router = APIRouter(prefix="/kaggle", tags=["Kaggle"])


@router.post("/fetch")
def fetch_now(db: Session = Depends(get_db)):
    try:
        downloaded = run_kaggle_fetcher(db)
        return {"downloaded": downloaded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
