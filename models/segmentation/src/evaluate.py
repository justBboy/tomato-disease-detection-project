import argparse
from typing import Dict

import torch
import torch.nn as nn

from .dataset_loader import create_single_split_loader
from .model import load_model_for_inference
from .train import batch_dice_iou, dice_loss
from .utils import load_config


@torch.no_grad()
def evaluate_model(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    bce_loss: nn.Module,
    device: str,
    bce_weight: float,
    dice_weight: float,
    threshold: float,
) -> Dict[str, float]:
    model.eval()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    steps = 0

    for images, masks in loader:
        images = images.to(device)
        masks = masks.to(device)

        logits = model(images)
        bce = bce_loss(logits, masks)
        dice = dice_loss(logits, masks)
        loss = bce_weight * bce + dice_weight * dice

        dice_score, iou_score = batch_dice_iou(logits, masks, threshold=threshold)
        running_loss += float(loss.item())
        running_dice += dice_score
        running_iou += iou_score
        steps += 1

    return {
        "loss": running_loss / max(steps, 1),
        "dice": running_dice / max(steps, 1),
        "iou": running_iou / max(steps, 1),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate tomato leaf segmentation model.")
    parser.add_argument(
        "--config",
        type=str,
        default="models/segmentation/configs/default.yaml",
        help="Path to YAML config.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="models/segmentation/checkpoints/best_model.pth",
        help="Path to trained checkpoint (.pth).",
    )
    parser.add_argument("--split", type=str, default=None, help="Split to evaluate: val or test.")
    parser.add_argument("--device", type=str, default=None, help="Override device: cpu or cuda.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    dataset_cfg = config["dataset"]
    model_cfg = config["model"]
    training_cfg = config["training"]

    if args.device is not None:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    eval_split = args.split or dataset_cfg.get("val_split", "val")
    loader = create_single_split_loader(
        root_dir=dataset_cfg["root_dir"],
        split=eval_split,
        image_size=training_cfg["image_size"],
        batch_size=training_cfg["batch_size"],
        num_workers=training_cfg.get("num_workers", 2),
    )

    model, _ = load_model_for_inference(
        checkpoint_path=args.checkpoint,
        device=device,
        in_channels=model_cfg.get("in_channels", 3),
        out_channels=model_cfg.get("out_channels", 1),
        base_channels=model_cfg.get("base_channels", 32),
    )

    metrics = evaluate_model(
        model=model,
        loader=loader,
        bce_loss=nn.BCEWithLogitsLoss(),
        device=device,
        bce_weight=training_cfg.get("bce_weight", 1.0),
        dice_weight=training_cfg.get("dice_weight", 1.0),
        threshold=training_cfg.get("threshold", 0.5),
    )

    print(f"Evaluation split: {eval_split}")
    print(f"Loss: {metrics['loss']:.4f}")
    print(f"Dice: {metrics['dice']:.4f}")
    print(f"IoU: {metrics['iou']:.4f}")


if __name__ == "__main__":
    main()
