import argparse
import random
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def sanitize_class_name(raw_name: str) -> str:
    cleaned = raw_name
    if "___" in cleaned:
        cleaned = cleaned.split("___", 1)[1]
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", cleaned).strip("_").lower()
    return cleaned


def list_class_dirs(root: Path) -> List[Path]:
    return sorted(
        [
            d
            for d in root.iterdir()
            if d.is_dir() and not d.name.startswith(".") and d.name.lower() != "plantvillage"
        ]
    )


def resolve_source_root(source_root: Path) -> Path:
    nested = source_root / "plantvillage"
    if nested.exists() and nested.is_dir():
        nested_classes = list_class_dirs(nested)
        if nested_classes:
            return nested
    return source_root


def collect_images(class_dir: Path) -> List[Path]:
    return sorted([p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS])


def split_paths(paths: List[Path], train_ratio: float, val_ratio: float, seed: int) -> Tuple[List[Path], List[Path], List[Path]]:
    rng = random.Random(seed)
    shuffled = paths[:]
    rng.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    train_set = shuffled[:train_end]
    val_set = shuffled[train_end:val_end]
    test_set = shuffled[val_end:]
    return train_set, val_set, test_set


def move_or_copy(files: List[Path], destination: Path, mode: str) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in files:
        target_path = destination / file_path.name
        if mode == "move":
            shutil.move(file_path.as_posix(), target_path.as_posix())
        else:
            shutil.copy2(file_path.as_posix(), target_path.as_posix())
    return len(files)


def prepare_dataset(
    source_root: Path,
    output_root: Path,
    mode: str,
    train_ratio: float,
    val_ratio: float,
    seed: int,
    clean_output: bool,
) -> Dict[str, Dict[str, int]]:
    source_root = resolve_source_root(source_root)
    if not source_root.exists():
        raise FileNotFoundError(f"Source dataset path not found: {source_root}")

    class_dirs = list_class_dirs(source_root)
    if not class_dirs:
        raise ValueError(f"No class folders found in source dataset: {source_root}")

    if clean_output and output_root.exists():
        shutil.rmtree(output_root.as_posix())
    output_root.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Dict[str, int]] = {}

    for class_dir in class_dirs:
        class_name = sanitize_class_name(class_dir.name)
        image_paths = collect_images(class_dir)
        if not image_paths:
            continue

        train_set, val_set, test_set = split_paths(
            paths=image_paths,
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            seed=seed,
        )

        train_count = move_or_copy(train_set, output_root / "train" / class_name, mode=mode)
        val_count = move_or_copy(val_set, output_root / "val" / class_name, mode=mode)
        test_count = move_or_copy(test_set, output_root / "test" / class_name, mode=mode)

        summary[class_name] = {
            "total": len(image_paths),
            "train": train_count,
            "val": val_count,
            "test": test_count,
        }

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare PlantVillage tomato dataset for ImageFolder training.")
    parser.add_argument(
        "--source-root",
        type=str,
        default="models/plantvillage",
        help="Source folder that contains tomato class folders.",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default="data/classification",
        help="Output folder for split dataset.",
    )
    parser.add_argument("--mode", type=str, choices=["move", "copy"], default="move", help="Move or copy files.")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Training split ratio.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic splitting.")
    parser.add_argument(
        "--clean-output",
        action="store_true",
        help="Delete existing output folder before writing new split.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    test_ratio = 1.0 - args.train_ratio - args.val_ratio
    if test_ratio <= 0:
        raise ValueError("train_ratio + val_ratio must be < 1.0 so that test split is positive.")

    summary = prepare_dataset(
        source_root=Path(args.source_root),
        output_root=Path(args.output_root),
        mode=args.mode,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
        clean_output=args.clean_output,
    )

    if not summary:
        raise ValueError("No images were processed. Check source dataset structure.")

    print(f"Prepared dataset at: {Path(args.output_root).as_posix()}")
    for class_name, stats in summary.items():
        print(
            f"{class_name}: total={stats['total']} train={stats['train']} "
            f"val={stats['val']} test={stats['test']}"
        )


if __name__ == "__main__":
    main()
