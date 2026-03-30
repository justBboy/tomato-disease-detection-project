from typing import Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    api_version: str
    device: str


class ClassificationPredictionResponse(BaseModel):
    predicted_class: str
    confidence: float = Field(ge=0.0, le=1.0)
    class_probabilities: Dict[str, float]


class SegmentationPredictionResponse(BaseModel):
    predicted_class: str
    confidence: float = Field(ge=0.0, le=1.0)
    infection_ratio: float = Field(ge=0.0, le=1.0)
    severity_percent: float = Field(ge=0.0, le=100.0)
    segmentation_mask_base64: str


class FullPredictionResponse(BaseModel):
    classification: ClassificationPredictionResponse
    segmentation: Optional[SegmentationPredictionResponse] = None
