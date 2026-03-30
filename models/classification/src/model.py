from typing import List, Optional, Tuple

import torch
import torch.nn as nn
from torchvision import models


def create_model(num_classes: int, pretrained: bool = True, freeze_backbone: bool = False) -> nn.Module:
    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    model = models.resnet18(weights=weights)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    for param in model.fc.parameters():
        param.requires_grad = True

    return model


def load_model_for_inference(
    checkpoint_path: str,
    device: str = "cpu",
    class_names: Optional[List[str]] = None,
    num_classes: Optional[int] = None,
) -> Tuple[nn.Module, Optional[List[str]]]:
    checkpoint = torch.load(checkpoint_path, map_location=device)
    stored_classes = checkpoint.get("class_names")
    if class_names is None and stored_classes is not None:
        class_names = stored_classes

    if class_names is not None:
        num_classes = len(class_names)
    elif num_classes is None:
        num_classes = checkpoint["model_state_dict"]["fc.weight"].shape[0]

    model = create_model(num_classes=num_classes, pretrained=False, freeze_backbone=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, class_names
