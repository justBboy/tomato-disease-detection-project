# Tomato Model Development

This directory contains lightweight, modular PyTorch starter pipelines for:

- `classification`: tomato leaf health + disease class prediction
- `segmentation`: pixel-level infected-region segmentation

The code is intentionally simple and designed for easy integration with a FastAPI backend.

## Folder Structure

```text
models/
  README.md
  requirements.txt
  classification/
    configs/
      default.yaml
    checkpoints/
      .gitkeep
    src/
      __init__.py
      dataset_loader.py
      transforms.py
      model.py
      utils.py
      train.py
      evaluate.py
      predict.py
  segmentation/
    configs/
      default.yaml
    checkpoints/
      .gitkeep
    src/
      __init__.py
      dataset_loader.py
      transforms.py
      model.py
      utils.py
      train.py
      evaluate.py
      predict.py
```

## Dataset Layout

### Classification

```text
data/classification/
  train/
    healthy/
      img_001.jpg
    early_blight/
      img_101.jpg
    late_blight/
      img_201.jpg
  val/
    healthy/
    early_blight/
    late_blight/
  test/
    healthy/
    early_blight/
    late_blight/
```

### Segmentation

```text
data/segmentation/
  train/
    images/
      img_001.jpg
    masks/
      img_001.png
  val/
    images/
    masks/
  test/
    images/
    masks/
```

Image and mask filenames should share the same stem (for example `img_001.jpg` and `img_001.png`).

## Recommended Training Strategy

- Classification:
  - Image size: `224`
  - Batch size: `16`
  - Epochs: `10-20`
  - Optimizer: `Adam`
  - Loss: `CrossEntropyLoss`
  - Model: `ResNet18` (transfer learning)
- Segmentation:
  - Image size: `256`
  - Batch size: `8`
  - Epochs: `20-40`
  - Optimizer: `Adam`
  - Loss: `BCEWithLogits + Dice`
  - Model: `U-Net` (lightweight base channels)

## Setup

From project root:

```bash
pip install -r models/requirements.txt
```

## Run Training

```bash
python -m models.classification.src.train --config models/classification/configs/default.yaml
python -m models.segmentation.src.train --config models/segmentation/configs/default.yaml
```

## Prepare PlantVillage Dataset

If your raw tomato classes are under `models/plantvillage`, create the expected split structure:

```bash
python -m models.classification.src.prepare_dataset --source-root models/plantvillage --output-root data/classification --mode move --clean-output
```

For a fast sanity run:

```bash
python -m models.classification.src.train --config models/classification/configs/quick_train.yaml
```

## Run Evaluation

```bash
python -m models.classification.src.evaluate --config models/classification/configs/default.yaml --checkpoint models/classification/checkpoints/best_model.pth
python -m models.segmentation.src.evaluate --config models/segmentation/configs/default.yaml --checkpoint models/segmentation/checkpoints/best_model.pth
```

## Run Prediction

```bash
python -m models.classification.src.predict --checkpoint models/classification/checkpoints/best_model.pth --image path/to/leaf.jpg
python -m models.segmentation.src.predict --checkpoint models/segmentation/checkpoints/best_model.pth --image path/to/leaf.jpg --output-mask outputs/mask.png
```

## FastAPI-Friendly Weight Loading

Each checkpoint is saved as `.pth` and contains at least:

- `model_state_dict`
- `epoch`
- `metrics`
- `class_names` (classification)

Both `model.py` files expose `load_model_for_inference(...)` for clean backend integration.
