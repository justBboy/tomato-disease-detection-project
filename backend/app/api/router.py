from fastapi import APIRouter

from .routes.admin import router as admin_router
from .routes.classification import router as classification_router
from .routes.health import router as health_router
from .routes.pipeline import router as pipeline_router
from .routes.segmentation import router as segmentation_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(health_router)
api_router.include_router(classification_router)
api_router.include_router(segmentation_router)
api_router.include_router(pipeline_router)
