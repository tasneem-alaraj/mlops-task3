import time
from typing import Dict, Any, List, Union
import joblib
import pandas as pd
from config.config import MODEL_PATH, PREPROCESSOR_PATH, CONFIG
from src.features import preprocess_features
from src.logger import logger

class DeliveryPredictor:
    def __init__(self):
        self.model_path = MODEL_PATH
        self.preprocessor_path = PREPROCESSOR_PATH
        self.model_version = CONFIG["app"]["version"]
        self.model = None
        self.preprocessor = None
        self._load_artifacts()

    def _load_artifacts(self):
        logger.info(f"Loading preprocessor from {self.preprocessor_path}...")
        self.preprocessor = joblib.load(self.preprocessor_path)

        logger.info(f"Loading trained model from {self.model_path}...")
        self.model = joblib.load(self.model_path)
        logger.info("Inference artifacts loaded successfully.")

    def predict(self, raw_input: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        start_time = time.time()
        
        if isinstance(raw_input, dict):
            df = pd.DataFrame([raw_input])
        else:
            df = pd.DataFrame(raw_input)

        logger.info(f"Received inference request for {len(df)} record(s).")

        X_processed = preprocess_features(df, self.preprocessor)

        probabilities = self.model.predict_proba(X_processed)[:, 1]
        predictions = self.model.predict(X_processed)

        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Inference completed in {latency} ms.")

        results = []
        for pred, prob in zip(predictions, probabilities):
            results.append({
                "is_late": int(pred),
                "late_probability": round(float(prob), 4),
                "model_version": self.model_version,
                "latency_ms": latency
            })
            
        logger.info(f"Prediction result: {results}")
        return results

predictor = DeliveryPredictor()