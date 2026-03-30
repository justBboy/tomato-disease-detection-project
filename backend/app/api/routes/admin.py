from fastapi import APIRouter, Query, Request

from ...schemas.analytics import AnalyticsRecentResponse, AnalyticsSummaryResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    request: Request,
    days: int = Query(default=30, ge=1, le=365),
    trend_days: int = Query(default=14, ge=1, le=90),
) -> AnalyticsSummaryResponse:
    analytics_service = request.app.state.analytics_service
    summary = analytics_service.get_summary(days=days, trend_days=trend_days)
    return AnalyticsSummaryResponse(**summary)


@router.get("/analytics/recent", response_model=AnalyticsRecentResponse)
def analytics_recent(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
) -> AnalyticsRecentResponse:
    analytics_service = request.app.state.analytics_service
    recent = analytics_service.get_recent(limit=limit)
    return AnalyticsRecentResponse(**recent)
