from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Any, Dict
from pydantic import BaseModel
from services.predict_service import predict_from_dict, health as model_health
from database import get_db
import json
from sqlalchemy.orm import Session
from db.models.models import PredictionLog

router = APIRouter(prefix="/predict", tags=["Prediction"])


class PredictRequest(BaseModel):
    # Schema is permissive: any keys will be forwarded to Ollama, but include common fields
    manufacturer_name: str | None = None
    car_model: str | None = None
    year_produced: int | None = None
    odometer_value: float | None = None
    engine_capacity: float | None = None
    transmission: str | None = None
    engine_fuel: str | None = None
    color: str | None = None
    drivetrain: str | None = None


@router.get("/health")
def health():
    return model_health()


@router.post("/")
def predict(req: PredictRequest, request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    payload = req.dict()
    try:
        result = predict_from_dict(payload)
        # log prediction
        try:
            pl = PredictionLog(payload=json.dumps(payload),
                               response=json.dumps(result))
            db.add(pl)
            db.commit()
        except Exception:
            # logging failure should not break response
            pass
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
