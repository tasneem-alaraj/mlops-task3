import json
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, status
from config.config import CONFIG, LOGS_DIR
from app.schemas import OrderPayload, PredictionResponse, BatchPredictionResponse
from src.predict import predictor
from src.logger import logger

app = FastAPI(
    title=CONFIG["app"]["name"],
    version=CONFIG["app"]["version"],
    description="Production API for predicting e-commerce delivery delays (Task 3)."
)

# Audit log file for drift analysis
PREDICTIONS_LOG_PATH = LOGS_DIR / "predictions_audit.jsonl"

# Runtime metrics
service_metrics = {
    "total_requests": 0,
    "predictions_count": 0,
    "predicted_late": 0,
    "predicted_on_time": 0,
    "total_latency_ms": 0.0
}

def log_prediction_event(raw_input: dict, output: dict):
    """Stores predictions for post-hoc evaluation and drift detection."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": raw_input,
        "prediction": output
    }
    with open(PREDICTIONS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy",
        "service": CONFIG["app"]["name"],
        "version": CONFIG["app"]["version"]
    }

@app.get("/info", tags=["Model Info"])
def model_info():
    return {
        "model_name": "HistGradientBoostingClassifier",
        "model_version": CONFIG["app"]["version"],
        "target": "is_late (0: On-Time, 1: Late)",
        "features_count": 35
    }

@app.get("/metrics", tags=["Monitoring"])
def get_metrics():
    """Exposes real-time monitoring and distribution stats."""
    avg_latency = (
        round(service_metrics["total_latency_ms"] / service_metrics["predictions_count"], 2)
        if service_metrics["predictions_count"] > 0 else 0.0
    )
    late_rate = (
        round((service_metrics["predicted_late"] / service_metrics["predictions_count"]) * 100, 2)
        if service_metrics["predictions_count"] > 0 else 0.0
    )
    return {
        "total_requests": service_metrics["total_requests"],
        "total_predictions": service_metrics["predictions_count"],
        "average_latency_ms": avg_latency,
        "prediction_distribution": {
            "predicted_late": service_metrics["predicted_late"],
            "predicted_on_time": service_metrics["predicted_on_time"],
            "late_percentage": late_rate
        }
    }

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK, tags=["Inference"])
def predict_single(order: OrderPayload):
    try:
        order_dict = order.model_dump()
        results = predictor.predict(order_dict)
        res = results[0]

        # Update metrics & write audit log
        service_metrics["total_requests"] += 1
        service_metrics["predictions_count"] += 1
        service_metrics["total_latency_ms"] += res["latency_ms"]
        if res["is_late"] == 1:
            service_metrics["predicted_late"] += 1
        else:
            service_metrics["predicted_on_time"] += 1

        log_prediction_event(order_dict, res)
        return res
    except Exception as e:
        logger.error(f"Inference failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )

@app.post("/predict/batch", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK, tags=["Inference"])
def predict_batch(orders: List[OrderPayload]):
    try:
        payloads = [order.model_dump() for order in orders]
        results = predictor.predict(payloads)

        service_metrics["total_requests"] += 1
        for inp, res in zip(payloads, results):
            service_metrics["predictions_count"] += 1
            service_metrics["total_latency_ms"] += res["latency_ms"]
            if res["is_late"] == 1:
                service_metrics["predicted_late"] += 1
            else:
                service_metrics["predicted_on_time"] += 1
            log_prediction_event(inp, res)

        return {
            "predictions": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Batch inference failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction error: {str(e)}"
        )