# notebooks/train_model.py
from pathlib import Path
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR / "data" / "used_cars.csv"
OUT_MODEL_DIR = Path(__file__).resolve().parents[1] / "app" / "models"
OUT_MODEL_PATH = OUT_MODEL_DIR / "model.pkl"


def abort(msg: str):
    print("ERROR:", msg)
    sys.exit(1)


print("Working directory:", Path.cwd())
print("Script directory:", SCRIPT_DIR)
print("Expected CSV path:", DATA_PATH)
if not DATA_PATH.exists():
    abort(
        f"CSV file not found at expected path: {DATA_PATH}\nList the directory to inspect: {list((SCRIPT_DIR / 'data').glob('*'))}")

try:
    df_head = pd.read_csv(DATA_PATH, nrows=5)
    print("CSV sample loaded. Columns:", list(df_head.columns))
except Exception as e:
    abort(f"Failed reading CSV sample: {e}")

try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    abort(f"Failed reading full CSV: {e}")

# Rename to avoid pydantic reserved name
if "model_name" in df.columns and "car_model" not in df.columns:
    df = df.rename(columns={"model_name": "car_model"})

if "price_usd" not in df.columns:
    abort("Target column 'price_usd' not found in CSV")

df = df.dropna(subset=["price_usd"])

required_cols = [
    "year_produced", "odometer_value", "engine_capacity",
    "engine_fuel", "transmission", "body_type", "drivetrain",
    "color", "manufacturer_name", "car_model"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    abort(f"Missing required columns in dataset: {missing}")

X = df[required_cols]
y = df["price_usd"]

categorical = ["engine_fuel", "transmission", "body_type", "drivetrain",
               "color", "manufacturer_name", "car_model"]
numeric = ["year_produced", "odometer_value", "engine_capacity"]

# Build OneHotEncoder with compatibility for sklearn versions.
# Goal: encoder produces dense output (RandomForest requires dense).
try:
    # older sklearn used `sparse`
    ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
except TypeError:
    # newer sklearn uses `sparse_output`
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", ohe, categorical),
        ("num", "passthrough", numeric)
    ]
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

print("Splitting data and training model...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

OUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, OUT_MODEL_PATH)
print("Model saved to:", OUT_MODEL_PATH)

score = pipeline.score(X_test, y_test)
print(f"R^2 score: {score:.3f}")
