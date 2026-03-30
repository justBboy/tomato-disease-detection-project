from io import BytesIO
from typing import Dict

import numpy as np
from PIL import Image


class HeuristicSegmentationService:
    """Fallback segmentation when no trained checkpoint is available."""

    def __init__(self, disease_pixel_threshold: float = 0.01) -> None:
        self.disease_pixel_threshold = disease_pixel_threshold

    def predict_from_bytes(self, image_bytes: bytes) -> Dict:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        arr = np.asarray(image, dtype=np.float32) / 255.0
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]

        leaf_mask = (r + g + b) > 0.15
        if not np.any(leaf_mask):
            infection_ratio = 0.0
            predicted_class = "healthy"
            confidence = 0.5
            mask = np.zeros((arr.shape[0], arr.shape[1]), dtype=np.uint8)
        else:
            yellowish = (r > 0.42) & (g > 0.35) & (b < 0.35)
            brownish = (r > g * 0.9) & (g > b * 1.05) & (r > 0.2)
            dark_spots = (r < 0.28) & (g < 0.28) & (b < 0.28)

            infected = leaf_mask & (yellowish | brownish | dark_spots)
            infected_pixels = np.count_nonzero(infected)
            leaf_pixels = np.count_nonzero(leaf_mask)
            infection_ratio = float(infected_pixels / max(leaf_pixels, 1))

            predicted_class = "diseased" if infection_ratio >= self.disease_pixel_threshold else "healthy"
            confidence = float(min(0.95, max(0.5, infection_ratio * 3.0 + 0.5)))
            mask = (infected.astype(np.uint8) * 255)

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "infection_ratio": infection_ratio,
            "severity_percent": infection_ratio * 100.0,
            "segmentation_mask_base64": self._mask_to_base64(mask),
        }

    @staticmethod
    def _mask_to_base64(mask: np.ndarray) -> str:
        buffer = BytesIO()
        Image.fromarray(mask, mode="L").save(buffer, format="PNG")
        import base64

        return base64.b64encode(buffer.getvalue()).decode("utf-8")
