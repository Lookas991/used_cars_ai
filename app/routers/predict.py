# app/routers/predict.py
from app.services.exchange_service import get_usd_to_eur_rate
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.services.predict_service import predict_from_dict, health as model_health


router = APIRouter(prefix="/predict", tags=["Prediction"])


class PredictionRequest(BaseModel):
    year_produced: int
    odometer_value: float
    engine_capacity: float
    engine_fuel: str
    transmission: str
    body_type: str
    drivetrain: str
    color: str
    manufacturer_name: str
    car_model: str


@router.get("/health")
async def healthcheck() -> Dict[str, str]:
    return model_health()


@router.post("/")
async def predict_price(req: PredictionRequest):
    try:
        pred_usd = predict_from_dict(req.dict())
        rate = get_usd_to_eur_rate()
        price_eur = round(pred_usd * rate, 2)
        return {
            "predicted_price_usd": float(pred_usd),
            "predicted_price_eur": float(price_eur),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {str(e)}")
