# FastAPI Backend

Minimal FastAPI inference backend for tomato classification and segmentation models.

## Install

From project root:

```bash
conda run -n tomato-ai python -m pip install -r backend/requirements.txt
```

## Run

From project root (recommended):

```bash
conda run -n tomato-ai python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the helper script:

```powershell
powershell -ExecutionPolicy Bypass -File backend/scripts/start_network.ps1
```

From `backend/` folder:

```bash
conda run -n tomato-ai python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Important:

- Use module notation `package.module:app`, not file paths.
- Correct: `python -m uvicorn app.main:app`
- Incorrect: `python -m uvicorn app/main.py:app`

## Same Wi-Fi Device Access

- Use your machine LAN IP from the phone, for example: `http://192.168.1.100:8000/api/v1`
- Keep phone and PC on the same Wi-Fi network.
- Allow Python/Uvicorn through Windows Firewall if prompted.

## Troubleshooting

If you see Device Guard blocking `uvicorn.exe`:

```text
'...\\Scripts\\uvicorn.exe' was blocked by your organization's Device Guard policy
```

Use module mode instead of the `uvicorn.exe` launcher:

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or without activating the environment:

```bash
conda run -n tomato-ai python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

If phone can reach `localhost` only, you likely have a stale local-only server:

1. Check listener:
```powershell
netstat -ano | findstr :8000
```
2. If it shows `127.0.0.1:8000`, stop that PID and restart with `--host 0.0.0.0`.
3. If still blocked from phone, add firewall allow rule (run PowerShell as Administrator):
```powershell
New-NetFirewallRule -DisplayName "Tomato API 8000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -Profile Private
```
4. Verify from phone browser first:
`http://<YOUR_PC_LAN_IP>:8000/api/v1/health`

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/classification/predict` (multipart image upload)
- `POST /api/v1/segmentation/predict` (multipart image upload)
- `POST /api/v1/predict/full` (classification + segmentation in one call)
- `GET /api/v1/admin/analytics/summary`
- `GET /api/v1/admin/analytics/recent`

## Notes

- Classification requires `models/classification/checkpoints/best_model.pth`.
- If `models/segmentation/checkpoints/best_model.pth` is missing, the API automatically uses a heuristic fallback for segmentation (no 503).
- Prediction events are logged to `data/analytics/predictions.jsonl` (override with `ANALYTICS_STORE_PATH`).
