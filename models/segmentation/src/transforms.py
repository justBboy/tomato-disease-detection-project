import random
from typing import Tuple

import numpy as np
import torch
from PIL import Image
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as F

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def _mask_to_tensor(mask: Image.Image) -> torch.Tensor:
    mask_np = np.array(mask, dtype=np.float32)
    if mask_np.ndim == 3:
        mask_np = mask_np[:, :, 0]
    mask_np = mask_np / 255.0
    mask_tensor = torch.from_numpy(mask_np).unsqueeze(0)
    return (mask_tensor > 0.5).float()


def train_transform(image: Image.Image, mask: Image.Image, image_size: int) -> Tuple[torch.Tensor, torch.Tensor]:
    image = F.resize(image, [image_size, image_size], interpolation=InterpolationMode.BILINEAR)
    mask = F.resize(mask, [image_size, image_size], interpolation=InterpolationMode.NEAREST)

    if random.random() < 0.5:
        image = F.hflip(image)
        mask = F.hflip(mask)
    if random.random() < 0.5:
        image = F.vflip(image)
        mask = F.vflip(mask)

    image_tensor = F.to_tensor(image)
    image_tensor = F.normalize(image_tensor, mean=IMAGENET_MEAN, std=IMAGENET_STD)
    mask_tensor = _mask_to_tensor(mask)
    return image_tensor, mask_tensor


def eval_transform(image: Image.Image, mask: Image.Image, image_size: int) -> Tuple[torch.Tensor, torch.Tensor]:
    image = F.resize(image, [image_size, image_size], interpolation=InterpolationMode.BILINEAR)
    mask = F.resize(mask, [image_size, image_size], interpolation=InterpolationMode.NEAREST)

    image_tensor = F.to_tensor(image)
    image_tensor = F.normalize(image_tensor, mean=IMAGENET_MEAN, std=IMAGENET_STD)
    mask_tensor = _mask_to_tensor(mask)
    return image_tensor, mask_tensor


def inference_transform(image: Image.Image, image_size: int) -> torch.Tensor:
    image = F.resize(image, [image_size, image_size], interpolation=InterpolationMode.BILINEAR)
    image_tensor = F.to_tensor(image)
    image_tensor = F.normalize(image_tensor, mean=IMAGENET_MEAN, std=IMAGENET_STD)
    return image_tensor
