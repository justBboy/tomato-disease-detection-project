from pathlib import Path
from typing import List, Optional, Tuple

from torch.utils.data import DataLoader, Dataset
from torchvision.datasets import ImageFolder

from .transforms import get_eval_transforms, get_train_transforms


class TomatoClassificationDataset(Dataset):
    """ImageFolder wrapper for tomato disease classification."""

    def __init__(
        self,
        root_dir: str,
        split: str,
        image_size: int = 224,
        transform=None,
        is_train: bool = False,
    ) -> None:
        split_dir = Path(root_dir) / split
        if not split_dir.exists():
            raise FileNotFoundError(f"Dataset split not found: {split_dir}")

        if transform is None:
            transform = get_train_transforms(image_size) if is_train else get_eval_transforms(image_size)

        self.dataset = ImageFolder(split_dir.as_posix(), transform=transform)

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index: int):
        return self.dataset[index]

    @property
    def classes(self) -> List[str]:
        return self.dataset.classes


def create_classification_dataloaders(
    root_dir: str,
    image_size: int,
    batch_size: int,
    num_workers: int = 2,
    train_split: str = "train",
    val_split: str = "val",
) -> Tuple[DataLoader, DataLoader, List[str]]:
    root_path = Path(root_dir)
    if not (root_path / val_split).exists():
        fallback_split = "test"
        if (root_path / fallback_split).exists():
            val_split = fallback_split
        else:
            raise FileNotFoundError(
                f"Neither validation split '{val_split}' nor fallback split 'test' exists in {root_dir}."
            )

    train_dataset = TomatoClassificationDataset(
        root_dir=root_dir,
        split=train_split,
        image_size=image_size,
        is_train=True,
    )
    val_dataset = TomatoClassificationDataset(
        root_dir=root_dir,
        split=val_split,
        image_size=image_size,
        is_train=False,
    )

    pin_memory = False
    try:
        import torch

        pin_memory = torch.cuda.is_available()
    except Exception:
        pin_memory = False

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    return train_loader, val_loader, train_dataset.classes


def create_single_split_loader(
    root_dir: str,
    split: str,
    image_size: int,
    batch_size: int,
    num_workers: int = 2,
    transform=None,
) -> Tuple[DataLoader, Optional[List[str]]]:
    dataset = TomatoClassificationDataset(
        root_dir=root_dir,
        split=split,
        image_size=image_size,
        transform=transform,
        is_train=False,
    )
    pin_memory = False
    try:
        import torch

        pin_memory = torch.cuda.is_available()
    except Exception:
        pin_memory = False

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    return loader, dataset.classes
