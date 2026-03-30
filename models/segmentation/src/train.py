import argparse
from pathlib import Path
from typing import Dict, Tuple

import torch
import torch.nn as nn
from torch.optim import Adam

from .dataset_loader import create_segmentation_dataloaders
from .model import create_model
from .utils import load_config, save_checkpoint, set_seed


def dice_loss(logits: torch.Tensor, targets: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    probs = torch.sigmoid(logits)
    intersection = (probs * targets).sum(dim=(1, 2, 3))
    cardinality = probs.sum(dim=(1, 2, 3)) + targets.sum(dim=(1, 2, 3))
    dice_score = (2.0 * intersection + eps) / (cardinality + eps)
    return 1.0 - dice_score.mean()


def batch_dice_iou(logits: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5) -> Tuple[float, float]:
    probs = torch.sigmoid(logits)
    preds = (probs > threshold).float()

    intersection = (preds * targets).sum(dim=(1, 2, 3))
    union = preds.sum(dim=(1, 2, 3)) + targets.sum(dim=(1, 2, 3)) - intersection
    dice = (2.0 * intersection + 1e-6) / (preds.sum(dim=(1, 2, 3)) + targets.sum(dim=(1, 2, 3)) + 1e-6)
    iou = (intersection + 1e-6) / (union + 1e-6)
    return float(dice.mean().item()), float(iou.mean().item())


def train_one_epoch(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    bce_loss: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    bce_weight: float,
    dice_weight: float,
    threshold: float,
) -> Dict[str, float]:
    model.train()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    steps = 0

    for images, masks in loader:
        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()
        logits = model(images)

        bce = bce_loss(logits, masks)
        dice = dice_loss(logits, masks)
        loss = bce_weight * bce + dice_weight * dice

        loss.backward()
        optimizer.step()

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


@torch.no_grad()
def evaluate(
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
    parser = argparse.ArgumentParser(description="Train tomato leaf segmentation model.")
    parser.add_argument(
        "--config",
        type=str,
        default="models/segmentation/configs/default.yaml",
        help="Path to YAML config.",
    )
    parser.add_argument("--device", type=str, default=None, help="Override device: cpu or cuda.")
    return parser.parse_args()


def train(config: Dict, device: str) -> None:
    dataset_cfg = config["dataset"]
    model_cfg = config["model"]
    training_cfg = config["training"]

    train_loader, val_loader = create_segmentation_dataloaders(
        root_dir=dataset_cfg["root_dir"],
        image_size=training_cfg["image_size"],
        batch_size=training_cfg["batch_size"],
        num_workers=training_cfg.get("num_workers", 2),
        train_split=dataset_cfg.get("train_split", "train"),
        val_split=dataset_cfg.get("val_split", "val"),
    )

    model = create_model(
        in_channels=model_cfg.get("in_channels", 3),
        out_channels=model_cfg.get("out_channels", 1),
        base_channels=model_cfg.get("base_channels", 32),
    ).to(device)

    bce_loss = nn.BCEWithLogitsLoss()
    optimizer = Adam(
        model.parameters(),
        lr=training_cfg["learning_rate"],
        weight_decay=training_cfg.get("weight_decay", 0.0),
    )

    bce_weight = training_cfg.get("bce_weight", 1.0)
    dice_weight = training_cfg.get("dice_weight", 1.0)
    threshold = training_cfg.get("threshold", 0.5)

    save_dir = Path(training_cfg["save_dir"])
    save_dir.mkdir(parents=True, exist_ok=True)

    best_val_dice = 0.0
    epochs = training_cfg["epochs"]

    print(f"Training on device: {device}")
    for epoch in range(1, epochs + 1):
        train_metrics = train_one_epoch(
            model=model,
            loader=train_loader,
            bce_loss=bce_loss,
            optimizer=optimizer,
            device=device,
            bce_weight=bce_weight,
            dice_weight=dice_weight,
            threshold=threshold,
        )
        val_metrics = evaluate(
            model=model,
            loader=val_loader,
            bce_loss=bce_loss,
            device=device,
            bce_weight=bce_weight,
            dice_weight=dice_weight,
            threshold=threshold,
        )

        print(
            f"Epoch {epoch:02d}/{epochs} | "
            f"train_loss={train_metrics['loss']:.4f} train_dice={train_metrics['dice']:.4f} train_iou={train_metrics['iou']:.4f} | "
            f"val_loss={val_metrics['loss']:.4f} val_dice={val_metrics['dice']:.4f} val_iou={val_metrics['iou']:.4f}"
        )

        metrics = {
            "train_loss": train_metrics["loss"],
            "train_dice": train_metrics["dice"],
            "train_iou": train_metrics["iou"],
            "val_loss": val_metrics["loss"],
            "val_dice": val_metrics["dice"],
            "val_iou": val_metrics["iou"],
        }

        save_checkpoint(
            path=(save_dir / "last_model.pth").as_posix(),
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            metrics=metrics,
            model_config=model_cfg,
        )

        if val_metrics["dice"] >= best_val_dice:
            best_val_dice = val_metrics["dice"]
            save_checkpoint(
                path=(save_dir / "best_model.pth").as_posix(),
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                metrics=metrics,
                model_config=model_cfg,
            )

    print(f"Best validation dice: {best_val_dice:.4f}")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    set_seed(config.get("training", {}).get("seed", 42))

    if args.device is not None:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    train(config=config, device=device)


if __name__ == "__main__":
    main()
