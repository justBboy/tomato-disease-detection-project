from pathlib import Path
from typing import List, Tuple

from PIL import Image
from torch.utils.data import DataLoader, Dataset

from .transforms import eval_transform, train_transform

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def _list_image_files(directory: Path) -> List[Path]:
    return sorted([p for p in directory.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS])


def _find_mask(mask_dir: Path, image_stem: str) -> Path:
    for ext in SUPPORTED_EXTENSIONS:
        candidate = mask_dir / f"{image_stem}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No mask found for image stem: {image_stem}")


class TomatoSegmentationDataset(Dataset):
    """Pairs tomato leaf image files with binary mask files."""

    def __init__(self, root_dir: str, split: str, image_size: int = 256, is_train: bool = False) -> None:
        split_dir = Path(root_dir) / split
        image_dir = split_dir / "images"
        mask_dir = split_dir / "masks"

        if not image_dir.exists() or not mask_dir.exists():
            raise FileNotFoundError(
                f"Expected split folder with 'images/' and 'masks/' at: {split_dir}"
            )

        image_paths = _list_image_files(image_dir)
        if not image_paths:
            raise ValueError(f"No images found in {image_dir}")

        self.samples: List[Tuple[Path, Path]] = []
        for image_path in image_paths:
            mask_path = _find_mask(mask_dir, image_path.stem)
            self.samples.append((image_path, mask_path))

        self.image_size = image_size
        self.is_train = is_train

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        image_path, mask_path = self.samples[index]
        image = Image.open(image_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.is_train:
            image_tensor, mask_tensor = train_transform(image=image, mask=mask, image_size=self.image_size)
        else:
            image_tensor, mask_tensor = eval_transform(image=image, mask=mask, image_size=self.image_size)
        return image_tensor, mask_tensor


def create_segmentation_dataloaders(
    root_dir: str,
    image_size: int,
    batch_size: int,
    num_workers: int = 2,
    train_split: str = "train",
    val_split: str = "val",
):
    root_path = Path(root_dir)
    if not (root_path / val_split).exists():
        fallback_split = "test"
        if (root_path / fallback_split).exists():
            val_split = fallback_split
        else:
            raise FileNotFoundError(
                f"Neither validation split '{val_split}' nor fallback split 'test' exists in {root_dir}."
            )

    train_dataset = TomatoSegmentationDataset(
        root_dir=root_dir,
        split=train_split,
        image_size=image_size,
        is_train=True,
    )
    val_dataset = TomatoSegmentationDataset(
        root_dir=root_dir,
        split=val_split,
        image_size=image_size,
        is_train=False,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=False,
    )
    return train_loader, val_loader


def create_single_split_loader(
    root_dir: str,
    split: str,
    image_size: int,
    batch_size: int,
    num_workers: int = 2,
):
    dataset = TomatoSegmentationDataset(root_dir=root_dir, split=split, image_size=image_size, is_train=False)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=False,
    )
    return loader
