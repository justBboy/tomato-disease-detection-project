from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ...schemas.predictions import SegmentationPredictionResponse

router = APIRouter(prefix="/segmentation", tags=["segmentation"])


@router.post("/predict", response_model=SegmentationPredictionResponse)
async def predict_segmentation(
    request: Request,
    file: UploadFile = File(...),
) -> SegmentationPredictionResponse:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    service = request.app.state.segmentation_service
    result = service.predict_from_bytes(image_bytes=image_bytes)

    analytics_service = request.app.state.analytics_service
    analytics_service.record_prediction(
        source="segmentation",
        predicted_class=result["predicted_class"],
        confidence=result.get("confidence"),
        severity_percent=result.get("severity_percent"),
    )

    return SegmentationPredictionResponse(**result)
