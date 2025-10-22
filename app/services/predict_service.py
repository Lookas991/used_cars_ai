import joblib
import numpy as np
import os
import pandas as pd
from app.services.exchange_service import get_usd_to_eur_rate

MODEL_PATH = os.path.join(os.path.dirname(
    __file__), "..", "models", "model.pkl")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"⚠️ Warning: Model file not found or invalid: {e}")

# Columns must exactly match training data
MODEL_COLUMNS = [
    "manufacturer_name", "car_model", "model_name", "transmission", "color",
    "odometer_value", "year_produced", "engine_fuel", "engine_has_gas",
    "engine_type", "engine_capacity", "body_type", "has_warranty",
    "state", "drivetrain", "is_exchangeable", "location_region",
    "number_of_photos", "up_counter", "duration_listed"
]


def predict_from_dict(data: dict) -> float:
    if model is None:
        raise RuntimeError("Model not loaded.")

    try:
        # Convert dict to DataFrame (must have same structure as training)
        df = pd.DataFrame([data])

        # Align columns (missing fields -> NaN)
        for col in MODEL_COLUMNS:
            if col not in df.columns:
                df[col] = np.nan

        df = df[MODEL_COLUMNS]

        prediction_usd = float(model.predict(df)[0])

        rate = get_usd_to_eur_rate()
        prediction_eur = prediction_usd * rate

        return round(prediction_eur, 2)
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")


def health() -> dict:
    return {"model_loaded": model is not None}
