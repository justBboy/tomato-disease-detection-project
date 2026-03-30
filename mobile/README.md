# Tomato Mobile (Expo SDK 55, TypeScript)

This mobile app was created with:

```bash
npx create-expo-app@latest mobile --template default@sdk-55
```

It provides a professional, user-friendly mobile interface for your project with:

- Bottom-tab navigation: `Scan`, `History`, `Care Guide`
- Leaf capture (camera scan) and gallery upload
- One-tap leaf health check flow (no backend setup in-app)
- Disease explanation view (readable condition names and practical next steps)
- Wikipedia lookup for detected disease with article preview + link
- Local history of recent checks (stored on-device)

## Run

From `mobile/`:

```bash
npm install
npm start
```

## Backend URL

The app tries to auto-detect your machine IP from Expo host metadata.
You can also set URL in-app, or force it with env:

```bash
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.100:8000/api/v1
```

- Android emulator: `http://10.0.2.2:8000/api/v1`
- iOS simulator: `http://localhost:8000/api/v1`
- Physical device: `http://<YOUR_PC_LAN_IP>:8000/api/v1`

For physical-device testing, ensure backend runs on `0.0.0.0` and phone + PC are on the same Wi-Fi.

## Endpoints Used

- `GET /api/v1/health`
- `POST /api/v1/classification/predict`
- `POST /api/v1/segmentation/predict`
- `POST /api/v1/predict/full`

## UX Flow

1. Open `Scan`, capture or upload a leaf image.
2. Tap `Check Leaf Health`.
3. Review plain-language condition summary, causes, management, and Wikipedia notes.
4. Open `History` to review prior scans.
5. Open `Care Guide` for disease causes and management references.
