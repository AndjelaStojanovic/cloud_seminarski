import os
import time

import joblib
import pandas as pd
import psycopg2
from psycopg2.extras import Json
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/model.joblib")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mlops")
DB_USER = os.getenv("DB_USER", "mlops")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mlops")

app = FastAPI(title="ML Model Predikcioni Servis")

# Model se učitava JEDNOM pri pokretanju servisa - ne trenira se u API kontejneru.
model = joblib.load(MODEL_PATH)


class CustomerData(BaseModel):
    tenure: float = Field(..., description="Broj meseci koliko je korisnik u kompaniji")
    MonthlyCharges: float = Field(..., description="Mesečni trošak korisnika")
    TotalCharges: float = Field(..., description="Ukupan trošak korisnika")
    SeniorCitizen: int = Field(..., description="0 = nije senior, 1 = senior")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def log_prediction(data: CustomerData, prediction: str, latency_ms: float) -> None:
    payload = data.model_dump()

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions_log
                (tenure, monthly_charges, total_charges, senior_citizen,
                 input_payload, prediction, latency_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.tenure,
                data.MonthlyCharges,
                data.TotalCharges,
                data.SeniorCitizen,
                Json(payload),
                prediction,
                latency_ms,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Greška prilikom upisa u bazu: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(data: CustomerData, background_tasks: BackgroundTasks):
    input_df = pd.DataFrame([data.model_dump()])

    start = time.perf_counter()
    prediction = model.predict(input_df)[0]
    latency_ms = (time.perf_counter() - start) * 1000

    prediction_label = "Yes" if int(prediction) == 1 else "No"

    background_tasks.add_task(log_prediction, data, prediction_label, latency_ms)

    return {
        "churn_prediction": prediction_label,
        "latency_ms": round(latency_ms, 3),
    }
