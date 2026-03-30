# Tomato Admin Dashboard (Next.js)

Simple, professional admin interface for analytics and insights.

## Features

- Total checks, weekly volume, healthy share, average severity
- Most common disease classes ("popular diseases")
- Daily trend chart (last 14 days)
- Source breakdown (classification / segmentation / full pipeline)
- Recent prediction activity table

## Backend Dependency

This dashboard expects the FastAPI backend to expose:

- `GET /api/v1/admin/analytics/summary`
- `GET /api/v1/admin/analytics/recent`

## Run

From `admin/`:

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env.local` before running if you need a custom backend URL.

Open: `http://localhost:3000`

## Environment

- `NEXT_PUBLIC_BACKEND_API_BASE_URL` (default: `http://127.0.0.1:8000/api/v1`)
