from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ...schemas.predictions import (
    ClassificationPredictionResponse,
    FullPredictionResponse,
    SegmentationPredictionResponse,
)

router = APIRouter(tags=["pipeline"])


@router.post("/predict/full", response_model=FullPredictionResponse)
async def predict_full_pipeline(
    request: Request,
    file: UploadFile = File(...),
) -> FullPredictionResponse:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    classification_service = request.app.state.classification_service
    classification_result = classification_service.predict_from_bytes(image_bytes=image_bytes)
    classification_response = ClassificationPredictionResponse(**classification_result)

    segmentation_service = request.app.state.segmentation_service
    if segmentation_service is None:
        analytics_service = request.app.state.analytics_service
        analytics_service.record_prediction(
            source="full",
            predicted_class=classification_result["predicted_class"],
            confidence=classification_result.get("confidence"),
            severity_percent=None,
        )
        return FullPredictionResponse(classification=classification_response, segmentation=None)

    segmentation_result = segmentation_service.predict_from_bytes(image_bytes=image_bytes)
    segmentation_response = SegmentationPredictionResponse(**segmentation_result)

    analytics_service = request.app.state.analytics_service
    analytics_service.record_prediction(
        source="full",
        predicted_class=classification_result["predicted_class"],
        confidence=classification_result.get("confidence"),
        severity_percent=segmentation_result.get("severity_percent"),
    )

    return FullPredictionResponse(
        classification=classification_response,
        segmentation=segmentation_response,
    )
