import argparse
from pathlib import Path
from typing import Dict, Tuple

import torch
import torch.nn as nn
from torch.optim import Adam

from .dataset_loader import create_classification_dataloaders
from .model import create_model
from .utils import load_config, save_checkpoint, set_seed


def train_one_epoch(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
) -> Tuple[float, float]:
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        predictions = logits.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / max(total, 1)
    epoch_acc = correct / max(total, 1)
    return epoch_loss, epoch_acc


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: str,
) -> Tuple[float, float]:
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)
        predictions = logits.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / max(total, 1)
    epoch_acc = correct / max(total, 1)
    return epoch_loss, epoch_acc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train tomato leaf classification model.")
    parser.add_argument(
        "--config",
        type=str,
        default="models/classification/configs/default.yaml",
        help="Path to YAML config.",
    )
    parser.add_argument("--device", type=str, default=None, help="Override device: cpu or cuda.")
    return parser.parse_args()


def train(config: Dict, device: str) -> None:
    dataset_cfg = config["dataset"]
    training_cfg = config["training"]

    train_loader, val_loader, class_names = create_classification_dataloaders(
        root_dir=dataset_cfg["root_dir"],
        image_size=training_cfg["image_size"],
        batch_size=training_cfg["batch_size"],
        num_workers=training_cfg.get("num_workers", 2),
        train_split=dataset_cfg.get("train_split", "train"),
        val_split=dataset_cfg.get("val_split", "val"),
    )

    model = create_model(
        num_classes=len(class_names),
        pretrained=training_cfg.get("pretrained", True),
        freeze_backbone=training_cfg.get("freeze_backbone", False),
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(
        model.parameters(),
        lr=training_cfg["learning_rate"],
        weight_decay=training_cfg.get("weight_decay", 0.0),
    )

    save_dir = Path(training_cfg["save_dir"])
    save_dir.mkdir(parents=True, exist_ok=True)

    best_val_acc = 0.0
    epochs = training_cfg["epochs"]

    print(f"Training on device: {device}")
    print(f"Classes: {class_names}")

    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        print(
            f"Epoch {epoch:02d}/{epochs} | "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )

        metrics = {
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
        }

        save_checkpoint(
            path=(save_dir / "last_model.pth").as_posix(),
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            metrics=metrics,
            class_names=class_names,
        )

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            save_checkpoint(
                path=(save_dir / "best_model.pth").as_posix(),
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                metrics=metrics,
                class_names=class_names,
            )

    print(f"Best validation accuracy: {best_val_acc:.4f}")


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
