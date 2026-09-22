from typing import List
from pydantic import BaseModel, Field

class OrderPayload(BaseModel):
    total_price: float = Field(..., gt=0, description="Total items price in BRL", json_schema_extra={"example": 150.0})
    total_freight: float = Field(..., ge=0, description="Total freight charge in BRL", json_schema_extra={"example": 25.0})
    total_items_count: int = Field(..., gt=0, description="Number of items in the order", json_schema_extra={"example": 1})
    total_payment_value: float = Field(..., gt=0, description="Total payment value", json_schema_extra={"example": 175.0})
    payment_installments_max: int = Field(..., ge=1, description="Max installments chosen", json_schema_extra={"example": 2})
    customer_state: str = Field(..., min_length=2, max_length=2, description="2-letter Brazilian state code", json_schema_extra={"example": "SP"})
    order_purchase_timestamp: str = Field(..., description="Purchase timestamp", json_schema_extra={"example": "2018-05-10 10:00:00"})
    order_estimated_delivery_date: str = Field(..., description="Estimated delivery date", json_schema_extra={"example": "2018-05-25 00:00:00"})

class PredictionResponse(BaseModel):
    is_late: int = Field(..., description="1 if delayed, 0 if on time")
    late_probability: float = Field(..., description="Predicted probability of being late")
    model_version: str = Field(..., description="Deployed model version")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    count: int