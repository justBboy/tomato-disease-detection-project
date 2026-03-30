import argparse
import json
from typing import Dict, List, Optional

import torch
from PIL import Image

from .model import load_model_for_inference
from .transforms import get_inference_transforms


@torch.no_grad()
def predict_image(
    model: torch.nn.Module,
    image_path: str,
    image_size: int,
    device: str,
    class_names: Optional[List[str]] = None,
) -> Dict[str, float]:
    transform = get_inference_transforms(image_size=image_size)
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    logits = model(tensor)
    probabilities = torch.softmax(logits, dim=1)[0]
    confidence, predicted_idx = torch.max(probabilities, dim=0)

    idx = int(predicted_idx.item())
    predicted_class = class_names[idx] if class_names else str(idx)

    return {
        "class": predicted_class,
        "confidence": float(confidence.item()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run single-image classification inference.")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to .pth checkpoint.")
    parser.add_argument("--image", type=str, required=True, help="Path to image file.")
    parser.add_argument("--image-size", type=int, default=224, help="Resize image to this size.")
    parser.add_argument("--device", type=str, default=None, help="cpu or cuda.")
    parser.add_argument(
        "--class-names",
        type=str,
        default=None,
        help="Optional comma-separated class names if checkpoint does not include them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    class_names = args.class_names.split(",") if args.class_names else None
    model, loaded_class_names = load_model_for_inference(
        checkpoint_path=args.checkpoint,
        device=device,
        class_names=class_names,
    )

    output = predict_image(
        model=model,
        image_path=args.image,
        image_size=args.image_size,
        device=device,
        class_names=loaded_class_names or class_names,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
