import pytest
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from src.features import extract_features
from src.predict import predictor

client = TestClient(app)

@pytest.fixture
def sample_raw_order():
    return {
        "total_price": 150.0,
        "total_freight": 25.0,
        "total_items_count": 1,
        "total_payment_value": 175.0,
        "payment_installments_max": 2,
        "customer_state": "SP",
        "order_purchase_timestamp": "2018-05-10 10:00:00",
        "order_estimated_delivery_date": "2018-05-25 00:00:00"
    }

# --- 1. Unit Tests (Feature Extraction) ---
def test_feature_extraction(sample_raw_order):
    df = pd.DataFrame([sample_raw_order])
    feat_df = extract_features(df)
    
    assert "purchase_dayofweek" in feat_df.columns
    assert "purchase_hour" in feat_df.columns
    assert "estimated_delivery_duration_days" in feat_df.columns
    assert feat_df["purchase_hour"].iloc[0] == 10
    assert feat_df["estimated_delivery_duration_days"].iloc[0] > 0

# --- 2. Model & Inference Tests ---
def test_predictor_single_output(sample_raw_order):
    res = predictor.predict(sample_raw_order)
    assert len(res) == 1
    assert res[0]["is_late"] in [0, 1]
    assert 0.0 <= res[0]["late_probability"] <= 1.0
    assert "model_version" in res[0]
    assert res[0]["latency_ms"] > 0

# --- 3. Integration Tests (API Endpoints) ---
def test_api_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert "model_version" in response.json()
    assert response.json()["features_count"] == 35

def test_api_predict_success(sample_raw_order):
    response = client.post("/predict", json=sample_raw_order)
    assert response.status_code == 200
    data = response.json()
    assert data["is_late"] in [0, 1]
    assert 0.0 <= data["late_probability"] <= 1.0

def test_api_predict_batch(sample_raw_order):
    batch = [sample_raw_order, sample_raw_order]
    response = client.post("/predict/batch", json=batch)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["predictions"]) == 2

def test_api_predict_invalid_payload():
    # Intentionally missing required fields and passing invalid state code to test 422
    bad_payload = {
        "total_price": -10.0,
        "customer_state": "INVALID_STATE"
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422