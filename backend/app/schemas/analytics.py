from typing import List, Optional

from pydantic import BaseModel, Field


class DiseaseCountItem(BaseModel):
    raw_class: str
    display_name: str
    count: int = Field(ge=0)
    share: float = Field(ge=0.0, le=1.0)


class SourceCountItem(BaseModel):
    source: str
    count: int = Field(ge=0)
    share: float = Field(ge=0.0, le=1.0)


class TrendPoint(BaseModel):
    date: str
    count: int = Field(ge=0)


class RecentPredictionItem(BaseModel):
    id: str
    timestamp: str
    source: str
    raw_class: str
    display_name: str
    confidence: Optional[float] = None
    severity_percent: Optional[float] = None
    is_healthy: bool


class AnalyticsRecentResponse(BaseModel):
    items: List[RecentPredictionItem]


class AnalyticsSummaryResponse(BaseModel):
    total_predictions: int = Field(ge=0)
    predictions_in_window: int = Field(ge=0)
    predictions_last_7_days: int = Field(ge=0)
    healthy_count: int = Field(ge=0)
    diseased_count: int = Field(ge=0)
    avg_confidence: Optional[float] = None
    avg_severity_percent: Optional[float] = None
    critical_cases_last_7_days: int = Field(ge=0)
    top_diseases: List[DiseaseCountItem]
    source_breakdown: List[SourceCountItem]
    trend_last_days: List[TrendPoint]
    most_recent_prediction_at: Optional[str] = None
    recent_items: List[RecentPredictionItem]
