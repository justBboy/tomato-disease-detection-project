import os
from dataclasses import dataclass
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _resolve_device(device_value: str) -> str:
    if device_value != "auto":
        return device_value
    return "cuda" if torch.cuda.is_available() else "cpu"


@dataclass(frozen=True)
class Settings:
    project_name: str
    api_version: str
    device: str
    classification_checkpoint: Path
    segmentation_checkpoint: Path
    analytics_store_path: Path
    classification_image_size: int
    segmentation_image_size: int
    segmentation_threshold: float
    disease_pixel_threshold: float


def load_settings() -> Settings:
    return Settings(
        project_name=os.getenv("PROJECT_NAME", "Tomato Disease Detection API"),
        api_version=os.getenv("API_VERSION", "1.0.0"),
        device=_resolve_device(os.getenv("TORCH_DEVICE", "auto")),
        classification_checkpoint=_resolve_path(
            os.getenv("CLASSIFICATION_CHECKPOINT", "models/classification/checkpoints/best_model.pth")
        ),
        segmentation_checkpoint=_resolve_path(
            os.getenv("SEGMENTATION_CHECKPOINT", "models/segmentation/checkpoints/best_model.pth")
        ),
        analytics_store_path=_resolve_path(
            os.getenv("ANALYTICS_STORE_PATH", "data/analytics/predictions.jsonl")
        ),
        classification_image_size=int(os.getenv("CLASSIFICATION_IMAGE_SIZE", "224")),
        segmentation_image_size=int(os.getenv("SEGMENTATION_IMAGE_SIZE", "256")),
        segmentation_threshold=float(os.getenv("SEGMENTATION_THRESHOLD", "0.5")),
        disease_pixel_threshold=float(os.getenv("DISEASE_PIXEL_THRESHOLD", "0.01")),
    )
