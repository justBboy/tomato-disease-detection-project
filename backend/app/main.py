import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import Settings, load_settings
from .services.analytics_service import AnalyticsService
from .services.classification_service import ClassificationService
from .services.heuristic_segmentation_service import HeuristicSegmentationService
from .services.segmentation_service import SegmentationService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title=settings.project_name,
        version=settings.api_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    def startup_event() -> None:
        _initialize_services(app=app, settings=settings)

    return app


def _initialize_services(app: FastAPI, settings: Settings) -> None:
    app.state.settings = settings
    app.state.analytics_service = AnalyticsService(store_path=settings.analytics_store_path)
    logger.info("Analytics store initialized at %s", settings.analytics_store_path)

    app.state.classification_service = ClassificationService(
        checkpoint_path=settings.classification_checkpoint,
        image_size=settings.classification_image_size,
        device=settings.device,
    )
    logger.info("Classification model loaded from %s", settings.classification_checkpoint)

    try:
        app.state.segmentation_service = SegmentationService(
            checkpoint_path=settings.segmentation_checkpoint,
            image_size=settings.segmentation_image_size,
            device=settings.device,
            threshold=settings.segmentation_threshold,
            disease_pixel_threshold=settings.disease_pixel_threshold,
        )
        logger.info("Segmentation model loaded from %s", settings.segmentation_checkpoint)
    except FileNotFoundError:
        app.state.segmentation_service = HeuristicSegmentationService(
            disease_pixel_threshold=settings.disease_pixel_threshold
        )
        logger.warning(
            "Segmentation checkpoint not found at %s. Using heuristic fallback segmentation service.",
            settings.segmentation_checkpoint,
        )


app = create_app()
