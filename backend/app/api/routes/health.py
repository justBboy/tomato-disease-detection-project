from fastapi import APIRouter, Request

from ...schemas.predictions import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        api_version=settings.api_version,
        device=settings.device,
    )
