export type PredictionTask = "classification" | "segmentation" | "full";

export type AnalysisHistoryItem = {
  id: string;
  timestamp: string;
  sourceUri: string;
  task: PredictionTask;
  rawClass: string;
  displayName: string;
  confidence: number | null;
  severityPercent: number | null;
};
