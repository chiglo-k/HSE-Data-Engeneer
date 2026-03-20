import time
import logging
import json
import os
from datetime import datetime
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

#Логирование
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_record, ensure_ascii=False)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("ml_service")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

#Prometheus метрики
REQUEST_COUNT = Counter(
    "ml_service_requests_total", "Total predict requests", ["status"]
)
REQUEST_LATENCY = Histogram(
    "ml_service_request_latency_seconds", "Predict request latency"
)

MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0")

#База данных
def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "mlservice_db"),
        user=os.getenv("POSTGRES_USER", "mlservice"),
        password=os.getenv("POSTGRES_PASSWORD", "mlservice_secret"),
    )

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id          SERIAL PRIMARY KEY,
                input_data  JSONB    NOT NULL,
                prediction  FLOAT    NOT NULL,
                latency_ms  FLOAT    NOT NULL,
                model_ver   TEXT     NOT NULL,
                created_at  TIMESTAMP DEFAULT NOW()
            )
        """)
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def log_prediction(input_data: dict, prediction: float, latency_ms: float):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO predictions (input_data, prediction, latency_ms, model_ver) "
                "VALUES (%s, %s, %s, %s)",
                (json.dumps(input_data), prediction, latency_ms, MODEL_VERSION),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB log error: {e}")

#Модель
def fake_model(features: list[float]) -> float:
    weights = np.array([0.3, 0.5, -0.2, 0.1])
    x = np.array(features[:4]) if len(features) >= 4 else np.pad(features, (0, 4 - len(features)))
    return float(np.dot(weights, x))

#FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ML Service", version=MODEL_VERSION, lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[float]


class PredictResponse(BaseModel):
    prediction: float
    model_version: str
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not request.features:
        REQUEST_COUNT.labels(status="error").inc()
        raise HTTPException(status_code=422, detail="features list is empty")

    t0 = time.perf_counter()
    prediction = fake_model(request.features)
    latency_ms = (time.perf_counter() - t0) * 1000

    logger.info(json.dumps({
        "event": "predict",
        "input": request.features,
        "output": prediction,
        "latency_ms": round(latency_ms, 3),
        "model_version": MODEL_VERSION,
    }))

    REQUEST_COUNT.labels(status="ok").inc()
    REQUEST_LATENCY.observe(latency_ms / 1000)
    log_prediction({"features": request.features}, prediction, latency_ms)

    return PredictResponse(
        prediction=prediction,
        model_version=MODEL_VERSION,
        latency_ms=round(latency_ms, 3),
    )


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
