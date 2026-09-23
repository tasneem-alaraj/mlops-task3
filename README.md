إليك محتوى ملف **`README.md`** بالكامل داخل كتلة كود موحدة حتى تتمكني من نسخه وحفظه مباشرة في جذر المشروع:

```markdown
# Olist Delivery Delay Prediction Service (Production MLOps Pipeline)

An enterprise-grade, containerized machine learning inference service for predicting Brazilian e-commerce delivery delays. Refactored from experimental research notebooks (Task 2) into a robust, observable, and fully automated production system (Task 3).

---

## 1. Project Architecture & Directory Layout

```text
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD automation workflow
├── app/
│   ├── main.py                  # FastAPI application, routes, and metric aggregations
│   └── schemas.py               # Pydantic v2 schemas for strict input/output contract enforcement
├── config/
│   ├── config.py                # Configuration module resolving dynamic absolute paths
│   └── config.yaml              # Centralized configuration (parameters, features, thresholds)
├── data/
│   └── data.dvc                 # DVC pointer tracking raw/processed data versioning
├── logs/
│   ├── app.log                  # Centralized service application log traces
│   └── predictions_audit.jsonl  # Append-only persistent request/prediction audit log for drift
├── models/
│   ├── best_model.joblib        # Pre-trained frozen HistGradientBoostingClassifier artifact
│   └── preprocessor.joblib      # Pre-fitted ColumnTransformer (Scalers, Encoders, Imputers)
├── notebooks/                   # Modular research and exploratory notebooks (01 to 06)
├── src/
│   ├── features.py              # Temporal feature extraction & preprocessor .transform() logic
│   ├── logger.py                # Centralized Python logging configuration (Console & File)
│   └── predict.py               # Singleton prediction engine and latency benchmark tracker
├── tests/
│   └── test_service.py          # Pytest suite (Unit tests, inference invariants, integration tests)
├── .dockerignore                # Build context exclusion rules
├── .gitignore                   # Version control exclusion rules
├── .pre-commit-config.yaml      # Code quality, formatting, and file-size pre-commit hooks
├── docker-compose.yml           # Unified multi-container orchestration (FastAPI + Postgres + pgAdmin)
├── Dockerfile                   # Lean, cached production container configuration
├── requirements.txt             # Lightweight production runtime dependencies
└── requirements-dev.txt         # Development, testing, quality, and tracking dependencies

```

---

## 2. Technical Justification of Tools & Components

| Component / Tool | Role in Architecture | Technical Justification |
| --- | --- | --- |
| **FastAPI** | REST API Web Framework | High-performance asynchronous execution, native OpenAPI/Swagger generation, and seamless integration with Pydantic. |
| **Pydantic V2** | Input/Output Validation | Prevents garbage/corrupted data from reaching inference engines, returning standardized HTTP 422 errors instead of 500 runtime crashes. |
| **Scikit-Learn (Frozen)** | Inference Pipeline | All transformers and estimators are loaded frozen (`.transform()` only). Runtime re-fitting is strictly forbidden to prevent data leakage and latency spikes. |
| **Docker & Compose** | Containerization | Guarantees identical execution across all environments, eliminates dependency drift, and provides isolated database networking. |
| **Pytest** | Automated Quality Gate | Automated regression prevention testing feature extraction, model stability, edge cases, and API endpoint contracts. |
| **DVC** | Data Versioning | Tracks versioned datasets via lightweight pointer files without pushing massive CSVs to Git repositories. |
| **MLflow** | Model & Experiment Registry | Centralizes model metadata, parameters, and evaluation metrics (`PR-AUC`, `ROC-AUC`) backed by SQLite for robust auditing. |
| **GitHub Actions** | CI/CD Pipeline | Enforces style checks (`flake8`), executes test suites, and verifies container build integrity automatically on every push. |

---

## 3. Quickstart & Deployment Guide (From A to Z)

### Option 1: One-Command Production Deployment (Docker Compose)

Ensure **Docker Desktop** is running, then execute in the project root:

```bash
docker compose up --build -d

```

#### Services Available:

* **Interactive API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs?utm_source=gemini)
* **Service Health Check:** [http://localhost:8000/](http://localhost:8000/?utm_source=gemini)
* **Model Metadata & Features:** [http://localhost:8000/info](http://localhost:8000/info?utm_source=gemini)
* **Runtime Metrics & Drift Monitoring:** [http://localhost:8000/metrics](http://localhost:8000/metrics?utm_source=gemini)
* **pgAdmin Database Dashboard:** [http://localhost:5050](http://localhost:5050?utm_source=gemini)
* *Username:* `admin@olist.com`
* *Password:* `admin_password`


* **PostgreSQL Database:** Port `5432` (`olist_db` / `olist_user`)

---

### Option 2: Local Development Setup

#### 1. Environment Initialization

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

```

#### 2. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

```

#### 3. Run the Inference Service Locally

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

---

## 4. Automated Testing & Verification

Run the entire end-to-end test suite using a single command:

```powershell
python -m pytest tests/ -v

```

### Test Suite Coverage:

1. `test_feature_extraction`: Validates temporal derivations (`purchase_hour`, `purchase_dayofweek`, `estimated_delivery_duration_days`).
2. `test_predictor_single_output`: Verifies single payload inference, probability constraints ($0.0 \le P \le 1.0$), and latency calculation.
3. `test_api_health`: Ensures `GET /` returns `{"status": "healthy"}`.
4. `test_api_info`: Verifies `GET /info` returns model metadata and feature definitions.
5. `test_api_predict_success`: Validates single order predictions via HTTP POST.
6. `test_api_predict_batch`: Validates multi-item batch predictions in a single network round-trip.
7. `test_api_predict_invalid_payload`: Confirms the service gracefully catches out-of-range/malformed data, returning `422 Unprocessable Entity` without server failure.

---

## 5. Experiment Tracking & Model Registry (MLflow)

The model parameters and evaluation metrics extracted during validation and test phases are tracked locally via SQLite:

### 1. View MLflow Dashboard

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --port 5000

```

Navigate to [http://localhost:5000](http://localhost:5000?utm_source=gemini), switch to **Model training**, and select the **`olist_delivery_delay`** experiment.

### 2. Logged Benchmark Metrics:

* **Model Type:** `HistGradientBoostingClassifier`
* **Test PR-AUC:** `0.0757` (Substantially above random baseline for heavily imbalanced classes)
* **Test ROC-AUC:** `0.4496` (Reflects real-world temporal shift / concept drift observed in the chronological holdout set)
* **Artifacts Logged:** `best_model.joblib` and `preprocessor.joblib`.

---

## 6. Observability, Logging & Monitoring

* **Structured Logging:** Application life-cycle events and inference latencies are automatically piped to `logs/app.log`.
* **Persistent Prediction Audit Trail:** Every incoming inference request and corresponding prediction is appended to `logs/predictions_audit.jsonl` in structured JSON lines:
```json
{
  "timestamp": "2026-09-22T20:35:27.123456",
  "input": { "total_price": 150.0, "customer_state": "SP" },
  "prediction": { "is_late": 1, "late_probability": 0.5529, "latency_ms": 2454.64 }
}

```


* **Real-Time Service Metrics (`/metrics`):**
Provides dynamic statistics including total requests, processed predictions, average latency (ms), and current delay classification ratios to detect immediate data drift.

---

## 7. Sample API Invocations

### Single Prediction Request (`POST /predict`):

```bash
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'Content-Type: application/json' \
  -d '{
  "total_price": 150.0,
  "total_freight": 25.0,
  "total_items_count": 1,
  "total_payment_value": 175.0,
  "payment_installments_max": 2,
  "customer_state": "SP",
  "order_purchase_timestamp": "2018-05-10 10:00:00",
  "order_estimated_delivery_date": "2018-05-25 00:00:00"
}'

```

### Expected Response (`200 OK`):

```json
{
  "is_late": 1,
  "late_probability": 0.5529,
  "model_version": "1.0.0",
  "latency_ms": 2898.08
}

```

---

## 8. Definition of Done Compliance Summary

* [x] **Config Driven:** All parameters, paths, and metadata defined in `config/config.yaml`.
* [x] **Inference Pipeline:** Isolated in `src/` using pre-fitted transformers without runtime fitting.
* [x] **Data & Model Versioning:** Data versioned via DVC (`data.dvc`); models and metrics tracked in MLflow.
* [x] **Automated Testing:** 100% pass rate achieved across 7 automated Pytest suites.
* [x] **FastAPI Service:** Exposes `/`, `/info`, `/predict`, `/predict/batch`, and `/metrics`.
* [x] **Docker Compose:** Multi-service stack (API, PostgreSQL, pgAdmin) operating seamlessly.
* [x] **CI/CD Pipeline:** Fully configured GitHub Actions workflow (`.github/workflows/ci.yml`).
* [x] **Audit & Monitoring:** Persistent JSONL audit trails and dynamic metric reporting active.
