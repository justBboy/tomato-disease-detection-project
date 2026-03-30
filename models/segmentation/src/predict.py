import argparse
import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import torch
from PIL import Image

from .model import load_model_for_inference
from .transforms import inference_transform


@torch.no_grad()
def predict_image(
    model: torch.nn.Module,
    image_path: str,
    image_size: int,
    device: str,
    threshold: float = 0.5,
    disease_pixel_threshold: float = 0.01,
) -> Dict[str, object]:
    image = Image.open(image_path).convert("RGB")
    tensor = inference_transform(image=image, image_size=image_size).unsqueeze(0).to(device)

    logits = model(tensor)
    prob_map = torch.sigmoid(logits)[0, 0]
    binary_mask = (prob_map > threshold).float()

    infection_ratio = float(binary_mask.mean().item())
    predicted_class = "diseased" if infection_ratio >= disease_pixel_threshold else "healthy"

    if predicted_class == "diseased" and binary_mask.sum() > 0:
        confidence = float(prob_map[binary_mask.bool()].mean().item())
    else:
        confidence = float((1.0 - prob_map).mean().item())

    return {
        "class": predicted_class,
        "confidence": confidence,
        "infection_ratio": infection_ratio,
        "mask": (binary_mask.cpu().numpy() * 255.0).astype(np.uint8),
    }


def save_mask(mask_array: np.ndarray, output_path: str) -> None:
    output = Image.fromarray(mask_array)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run single-image segmentation inference.")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to .pth checkpoint.")
    parser.add_argument("--image", type=str, required=True, help="Path to image file.")
    parser.add_argument("--image-size", type=int, default=256, help="Resize image to this size.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Mask threshold.")
    parser.add_argument(
        "--disease-pixel-threshold",
        type=float,
        default=0.01,
        help="Threshold on infected pixel ratio to label image as diseased.",
    )
    parser.add_argument("--output-mask", type=str, default=None, help="Path to save predicted mask image.")
    parser.add_argument("--device", type=str, default=None, help="cpu or cuda.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    model, _ = load_model_for_inference(checkpoint_path=args.checkpoint, device=device)
    result = predict_image(
        model=model,
        image_path=args.image,
        image_size=args.image_size,
        device=device,
        threshold=args.threshold,
        disease_pixel_threshold=args.disease_pixel_threshold,
    )

    output_mask_path: Optional[str] = args.output_mask
    if output_mask_path is None:
        image_path = Path(args.image)
        output_mask_path = (image_path.parent / f"{image_path.stem}_pred_mask.png").as_posix()

    save_mask(result["mask"], output_mask_path)

    printable_result = {
        "class": result["class"],
        "confidence": result["confidence"],
        "infection_ratio": result["infection_ratio"],
        "segmentation_mask_path": output_mask_path,
    }
    print(json.dumps(printable_result, indent=2))


if __name__ == "__main__":
    main()
