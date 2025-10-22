# Used Car Price Prediction API

This project is a **FastAPI backend** for predicting used car prices using machine learning and optional Ollama LLM integration. It supports prediction in **EUR** using live exchange rates from Frankfurter API.

## Project Structure

/used-cars
├── app/ # FastAPI code
│ ├── routers/ # API endpoints
│ ├── services/ # ML & utility services
│ ├── db/ # DB-related code (if any)
│ └── models/ # ML model (ignored in git)
├── fastapi/ # Optional separate FastAPI folder
├── notebooks/ # Jupyter notebooks
│ └── data/ # CSV datasets (ignored in git)
├── ollama_data/ # LLM model data (ignored in git)
└── pg_data/ # Local Postgres data (ignored in git)

## Setup

1. **Clone the repo**

```bash
git clone <repo-url>
cd used-cars
```

2. **Create virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. **Install dependencies\***

```bash
pip install -r requirements.txt
```

4. **Run fastapi**
   uvicorn app.main:app --reload

**Usage**

POST /predict/
Send car features JSON to get predicted price in EUR.

Example JSON:
{
"manufacturer_name": "BMW",
"model_name": "X5",
"car_model": "X5", if missing add it
"transmission": "automatic",
"color": "black",
"odometer_value": 120000,
"year_produced": 2017,
"engine_fuel": "diesel",
"engine_has_gas": false,
"engine_type": "inline",
"engine_capacity": 3.0,
"body_type": "SUV",
"has_warranty": false,
"state": "used",
"drivetrain": "4x4",
"is_exchangeable": false,
"location_region": "Germany",
"number_of_photos": 8,
"up_counter": 3,
"duration_listed": 25,
"feature_0": 1,
"feature_1": 0,
"feature_2": 0,
"feature_3": 0,
"feature_4": 1,
"feature_5": 0,
"feature_6": 0,
"feature_7": 0,
"feature_8": 1,
"feature_9": 0
}
