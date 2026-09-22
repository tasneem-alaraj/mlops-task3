import pandas as pd
import numpy as np
from src.logger import logger

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts raw temporal and engineered features matching Notebook 5."""
    data = df.copy()

    logger.info("Extracting temporal features from raw payload...")
    purchase_dt = pd.to_datetime(data["order_purchase_timestamp"], format="mixed")
    estimated_dt = pd.to_datetime(data["order_estimated_delivery_date"], format="mixed")

    data["purchase_dayofweek"] = purchase_dt.dt.dayofweek
    data["purchase_hour"] = purchase_dt.dt.hour
    data["estimated_delivery_duration_days"] = (
        (estimated_dt - purchase_dt).dt.total_seconds() / (24 * 3600)
    )

    return data

def preprocess_features(df: pd.DataFrame, preprocessor) -> np.ndarray:
    """Transforms raw order data using the pre-fitted transformer object."""
    data_with_features = extract_features(df)
    logger.info("Applying pre-fitted ColumnTransformer transformations...")
    transformed_matrix = preprocessor.transform(data_with_features)
    return transformed_matrix