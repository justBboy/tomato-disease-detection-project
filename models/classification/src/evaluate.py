import argparse
from typing import Dict, List

import torch
import torch.nn as nn

from .dataset_loader import create_single_split_loader
from .model import load_model_for_inference
from .utils import load_config


@torch.no_grad()
def evaluate_model(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: str,
    class_names: List[str],
) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    total = 0
    correct = 0

    class_correct = [0 for _ in class_names]
    class_total = [0 for _ in class_names]

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss = criterion(logits, labels)
        total_loss += loss.item() * labels.size(0)

        preds = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

        for label, pred in zip(labels, preds):
            label_idx = int(label.item())
            class_total[label_idx] += 1
            if int(pred.item()) == label_idx:
                class_correct[label_idx] += 1

    results = {
        "loss": total_loss / max(total, 1),
        "accuracy": correct / max(total, 1),
    }
    for i, class_name in enumerate(class_names):
        key = f"class_acc_{class_name}"
        results[key] = class_correct[i] / max(class_total[i], 1)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate tomato leaf classification model.")
    parser.add_argument(
        "--config",
        type=str,
        default="models/classification/configs/default.yaml",
        help="Path to YAML config.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="models/classification/checkpoints/best_model.pth",
        help="Path to trained checkpoint (.pth).",
    )
    parser.add_argument("--split", type=str, default=None, help="Split to evaluate: val or test.")
    parser.add_argument("--device", type=str, default=None, help="Override device: cpu or cuda.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    dataset_cfg = config["dataset"]
    training_cfg = config["training"]

    if args.device is not None:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    eval_split = args.split or dataset_cfg.get("val_split", "val")
    loader, class_names_from_data = create_single_split_loader(
        root_dir=dataset_cfg["root_dir"],
        split=eval_split,
        image_size=training_cfg["image_size"],
        batch_size=training_cfg["batch_size"],
        num_workers=training_cfg.get("num_workers", 2),
    )

    model, class_names_from_ckpt = load_model_for_inference(
        checkpoint_path=args.checkpoint,
        device=device,
        class_names=None,
    )
    class_names = class_names_from_ckpt or class_names_from_data or [str(i) for i in range(2)]

    criterion = nn.CrossEntropyLoss()
    metrics = evaluate_model(model=model, loader=loader, criterion=criterion, device=device, class_names=class_names)

    print(f"Evaluation split: {eval_split}")
    print(f"Loss: {metrics['loss']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    for class_name in class_names:
        print(f"{class_name} accuracy: {metrics[f'class_acc_{class_name}']:.4f}")


if __name__ == "__main__":
    main()
