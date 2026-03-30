from io import BytesIO
from pathlib import Path
import sys
from typing import Dict, List

import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.classification.src.model import load_model_for_inference
from models.classification.src.transforms import get_inference_transforms


class ClassificationService:
    def __init__(self, checkpoint_path: Path, image_size: int, device: str) -> None:
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Classification checkpoint not found: {checkpoint_path}")

        self.device = device
        self.image_size = image_size
        self.model, self.class_names = load_model_for_inference(
            checkpoint_path=checkpoint_path.as_posix(),
            device=device,
        )
        self.transform = get_inference_transforms(image_size=image_size)

    @torch.no_grad()
    def predict_from_bytes(self, image_bytes: bytes) -> Dict:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        logits = self.model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]
        confidence, predicted_idx = torch.max(probabilities, dim=0)

        idx = int(predicted_idx.item())
        class_names = self._resolve_class_names(probabilities.size(0))
        predicted_class = class_names[idx]
        class_probabilities = {
            class_names[i]: float(probabilities[i].item()) for i in range(probabilities.size(0))
        }

        return {
            "predicted_class": predicted_class,
            "confidence": float(confidence.item()),
            "class_probabilities": class_probabilities,
        }

    def _resolve_class_names(self, num_classes: int) -> List[str]:
        if self.class_names is None:
            return [f"class_{i}" for i in range(num_classes)]
        if len(self.class_names) != num_classes:
            return [f"class_{i}" for i in range(num_classes)]
        return self.class_names
