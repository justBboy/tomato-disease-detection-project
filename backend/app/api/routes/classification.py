from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ...schemas.predictions import ClassificationPredictionResponse

router = APIRouter(prefix="/classification", tags=["classification"])


@router.post("/predict", response_model=ClassificationPredictionResponse)
async def predict_classification(
    request: Request,
    file: UploadFile = File(...),
) -> ClassificationPredictionResponse:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    service = request.app.state.classification_service
    result = service.predict_from_bytes(image_bytes=image_bytes)

    analytics_service = request.app.state.analytics_service
    analytics_service.record_prediction(
        source="classification",
        predicted_class=result["predicted_class"],
        confidence=result.get("confidence"),
        severity_percent=None,
    )

    return ClassificationPredictionResponse(**result)
