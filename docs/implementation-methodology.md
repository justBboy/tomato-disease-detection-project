# Implementation Methodology and Technical Concepts

## 1. Purpose of This Document

This document explains how the project was implemented across:

- AI/ML model development
- FastAPI backend integration
- Mobile frontend (React Native + Expo)
- Admin frontend (Next.js analytics dashboard)

It focuses on **how implementation was done**, **concepts used**, and **tools/technologies applied**.

---

## 2. Monorepo Structure

```text
Tomato-Disease-Detection-Project/
  models/       -> AI model training and inference modules
  backend/      -> FastAPI APIs and model-serving services
  mobile/       -> React Native (Expo) end-user application
  admin/        -> Next.js admin analytics dashboard
  data/         -> datasets + analytics event storage
  docs/         -> project and technical documentation
```

---

## 3. AI/ML Layer: Models and Concepts

## 3.1 Classification Model

Location: `models/classification/src/`

### Core concept used

- **Transfer Learning** with `ResNet18` (PyTorch `torchvision.models.resnet18`)
- Replace final `fc` layer to match tomato classes
- Optional backbone freezing for faster small-dataset training

### Why this method

- ResNet18 is lightweight and reliable for student-scale datasets
- Transfer learning improves accuracy and training speed vs. training from scratch

### Data pipeline

- Dataset loader uses `ImageFolder` split folders (`train/`, `val/`, optional `test/`)
- Train transforms:
  - resize
  - horizontal flip
  - small rotation
  - ImageNet normalization
- Eval/inference transforms:
  - resize
  - normalization only

### Optimization

- Loss: `CrossEntropyLoss`
- Optimizer: `Adam`
- Metrics: train/val loss, train/val accuracy
- Saved checkpoints:
  - `best_model.pth`
  - `last_model.pth`
- Checkpoint includes `class_names` for backend-friendly inference mapping

---

## 3.2 Segmentation Model

Location: `models/segmentation/src/`

### Core concept used

- **U-Net semantic segmentation**
- Encoder-decoder with skip connections
- Binary output mask (infected vs non-infected pixels)

### Why this method

- U-Net is effective for pixel-level segmentation with limited datasets
- Good tradeoff between quality and computational cost

### Data pipeline

- Paired image-mask dataset:
  - `images/` and `masks/` per split
  - same filename stem for image and mask
- Mask processing:
  - grayscale to binary tensor
  - nearest-neighbor resize for mask integrity

### Optimization

- Loss function:
  - `BCEWithLogitsLoss` + Dice Loss (weighted combination)
- Metrics:
  - Dice coefficient
  - IoU (Intersection over Union)
- Saved checkpoints:
  - `best_model.pth`
  - `last_model.pth`

### Severity concept

- `infection_ratio = infected_pixels / total_leaf_pixels`
- `severity_percent = infection_ratio * 100`

This enables quantitative disease severity estimation.

---

## 3.3 Inference Packaging Concept

Both classification and segmentation modules expose:

- `load_model_for_inference(...)`

This was intentionally designed so backend services can load models uniformly without duplicating training logic.

---

## 4. FastAPI Backend Layer

Location: `backend/app/`

## 4.1 Backend architecture pattern used

- Router-based API modules
- Service layer for model inference
- Schema layer (Pydantic) for response contracts
- Central config loader for path/device settings

## 4.2 Startup initialization flow

At startup:

1. Load environment/config settings
2. Initialize analytics service
3. Load classification model service
4. Try to load segmentation model service
5. If segmentation checkpoint is missing, use heuristic fallback segmentation service

This keeps API available even if segmentation training is incomplete.

## 4.3 API endpoints

- `GET /api/v1/health`
- `POST /api/v1/classification/predict`
- `POST /api/v1/segmentation/predict`
- `POST /api/v1/predict/full`
- `GET /api/v1/admin/analytics/summary`
- `GET /api/v1/admin/analytics/recent`

## 4.4 Backend concepts used

- Input validation (`UploadFile` + content type checks)
- In-memory inference flow (bytes -> PIL -> tensor -> model)
- CORS enabled for mobile/admin cross-origin access
- Heuristic fallback strategy for segmentation robustness
- Device resolution (`auto -> cuda if available else cpu`)

---

## 5. Analytics Implementation (Backend + Admin)

## 5.1 Event logging method

Prediction events are appended to:

- `data/analytics/predictions.jsonl`

Fields include:

- timestamp
- source endpoint (`classification`, `segmentation`, `full`)
- predicted class
- confidence
- severity percent
- healthy/diseased flag

## 5.2 Aggregation concepts

Analytics service computes:

- total predictions
- last 7-day activity
- healthy vs diseased counts
- average confidence
- average severity
- critical cases (severity >= 30%)
- top disease classes
- trend data by date
- recent activity list

---

## 6. Mobile Frontend (React Native + Expo)

Location: `mobile/src/app/`

## 6.1 UX design approach used

- User-first language (minimal AI jargon)
- Simple action flow:
  1. Add photo
  2. Check leaf health
  3. Read practical guidance

Tabs:

- `Scan`
- `History`
- `Care Guide`

## 6.2 Mobile technical features

- Camera capture and gallery upload (`expo-image-picker`)
- Local history persistence (`AsyncStorage`)
- Plain-language disease explanation mapping
- Wikipedia enrichment for detected diseases
- Segmentation mask display

## 6.3 Frontend integration pattern

- API-first architecture
- Strongly typed response interfaces in `services/api.ts`
- Results transformed into user-readable summaries before rendering

---

## 7. Admin Frontend (Next.js)

Location: `admin/`

## 7.1 Purpose

Provide project-level insights and disease trend monitoring without authentication (per current project scope).

## 7.2 UI/UX approach

- Simple but professional dashboard
- KPI cards, trend bars, ranked disease list, source breakdown, and recent table
- Periodic auto-refresh for near-real-time view

## 7.3 Data integration

Admin reads analytics from backend:

- `/api/v1/admin/analytics/summary`

Configurable backend base URL via:

- `NEXT_PUBLIC_BACKEND_API_BASE_URL`

---

## 8. End-to-End Operational Flow

1. User captures/uploads tomato leaf image in mobile app
2. Mobile calls backend `/predict/full`
3. Backend runs classification + segmentation inference
4. Backend returns:
   - disease class
   - confidence
   - segmentation mask
   - severity estimate
5. Mobile shows user-friendly summary and management tips
6. Backend logs prediction event to analytics store
7. Admin dashboard reads aggregated analytics and displays trends/popularity

---

## 9. Key Concepts Applied Across the System

- Transfer Learning (ResNet18)
- Semantic Segmentation (U-Net)
- Multi-loss optimization (BCE + Dice)
- API-first system design
- Service-oriented backend structure
- Fault-tolerant inference (heuristic fallback)
- Data-driven monitoring (event logging + aggregated analytics)
- User-centered presentation (plain-language results)

---

## 10. Tools and Technologies Used

## AI / Modeling

- Python
- PyTorch
- Torchvision
- PIL
- NumPy

## Backend

- FastAPI
- Uvicorn
- Pydantic
- python-multipart

## Mobile

- React Native
- Expo SDK 55
- Expo Router
- AsyncStorage
- React Query

## Admin

- Next.js (App Router)
- TypeScript
- CSS Modules

---

## 11. Current Scope vs Extension Opportunities

Current implementation is intentionally minimal and scalable.

Potential extensions:

- role-based admin access/auth
- richer time-range filters on analytics
- model version tracking in analytics events
- background task queue for heavy inference
- cloud storage for prediction artifacts
- continuous training / MLOps pipeline

---

## 12. Summary

The implementation combines:

- practical deep learning methods (ResNet18 + U-Net),
- a clean FastAPI inference service,
- a user-friendly mobile experience,
- and a professional analytics dashboard.

The architecture prioritizes **clarity, maintainability, and demonstrability** for a student project while preserving room for future scale.
