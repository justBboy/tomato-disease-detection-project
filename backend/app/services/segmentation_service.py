import base64
from io import BytesIO
from pathlib import Path
import sys
from typing import Dict

import numpy as np
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.segmentation.src.model import load_model_for_inference
from models.segmentation.src.transforms import inference_transform


class SegmentationService:
    def __init__(
        self,
        checkpoint_path: Path,
        image_size: int,
        device: str,
        threshold: float = 0.5,
        disease_pixel_threshold: float = 0.01,
    ) -> None:
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Segmentation checkpoint not found: {checkpoint_path}")

        self.device = device
        self.image_size = image_size
        self.threshold = threshold
        self.disease_pixel_threshold = disease_pixel_threshold

        self.model, _ = load_model_for_inference(
            checkpoint_path=checkpoint_path.as_posix(),
            device=device,
        )

    @torch.no_grad()
    def predict_from_bytes(self, image_bytes: bytes) -> Dict:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        original_size = image.size

        tensor = inference_transform(image=image, image_size=self.image_size).unsqueeze(0).to(self.device)
        logits = self.model(tensor)
        prob_map = torch.sigmoid(logits)[0, 0]
        binary_mask = (prob_map > self.threshold)

        infection_ratio = float(binary_mask.float().mean().item())
        predicted_class = "diseased" if infection_ratio >= self.disease_pixel_threshold else "healthy"
        severity_percent = infection_ratio * 100.0

        if predicted_class == "diseased" and bool(binary_mask.any()):
            confidence = float(prob_map[binary_mask].mean().item())
        else:
            confidence = float((1.0 - prob_map).mean().item())

        mask_array = (binary_mask.float().cpu().numpy() * 255.0).astype(np.uint8)
        mask_image = Image.fromarray(mask_array, mode="L").resize(original_size, Image.NEAREST)
        mask_b64 = self._image_to_base64(mask_image)

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "infection_ratio": infection_ratio,
            "severity_percent": severity_percent,
            "segmentation_mask_base64": mask_b64,
        }

    @staticmethod
    def _image_to_base64(mask_image: Image.Image) -> str:
        buffer = BytesIO()
        mask_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
