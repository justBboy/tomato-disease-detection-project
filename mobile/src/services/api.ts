import type { ImagePickerAsset } from "expo-image-picker";

export interface HealthResponse {
  status: string;
  api_version: string;
  device: string;
}

export interface ClassificationResponse {
  predicted_class: string;
  confidence: number;
  class_probabilities: Record<string, number>;
}

export interface SegmentationResponse {
  predicted_class: string;
  confidence: number;
  infection_ratio: number;
  severity_percent: number;
  segmentation_mask_base64: string;
}

export interface FullPredictionResponse {
  classification: ClassificationResponse;
  segmentation: SegmentationResponse | null;
}

function buildFormData(imageAsset: ImagePickerAsset): FormData {
  const formData = new FormData();
  const file = {
    uri: imageAsset.uri,
    name: imageAsset.fileName || `leaf_${Date.now()}.jpg`,
    type: imageAsset.mimeType || "image/jpeg",
  };
  formData.append("file", file as any);
  return formData;
}

async function postImage<T>(baseUrl: string, path: string, imageAsset: ImagePickerAsset): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
    },
    body: buildFormData(imageAsset),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = (data as { detail?: string })?.detail || "Request failed.";
    throw new Error(`${response.status}: ${detail}`);
  }
  return data as T;
}

export async function checkHealth(baseUrl: string): Promise<HealthResponse> {
  const response = await fetch(`${baseUrl}/health`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = (data as { detail?: string })?.detail || "Health check failed.";
    throw new Error(`${response.status}: ${detail}`);
  }
  return data as HealthResponse;
}

export async function predictClassification(
  baseUrl: string,
  imageAsset: ImagePickerAsset
): Promise<ClassificationResponse> {
  return postImage<ClassificationResponse>(baseUrl, "/classification/predict", imageAsset);
}

export async function predictSegmentation(
  baseUrl: string,
  imageAsset: ImagePickerAsset
): Promise<SegmentationResponse> {
  return postImage<SegmentationResponse>(baseUrl, "/segmentation/predict", imageAsset);
}

export async function predictFull(baseUrl: string, imageAsset: ImagePickerAsset): Promise<FullPredictionResponse> {
  return postImage<FullPredictionResponse>(baseUrl, "/predict/full", imageAsset);
}
