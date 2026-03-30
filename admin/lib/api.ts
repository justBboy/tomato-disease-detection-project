export type DiseaseCountItem = {
  raw_class: string;
  display_name: string;
  count: number;
  share: number;
};

export type SourceCountItem = {
  source: string;
  count: number;
  share: number;
};

export type TrendPoint = {
  date: string;
  count: number;
};

export type RecentPredictionItem = {
  id: string;
  timestamp: string;
  source: string;
  raw_class: string;
  display_name: string;
  confidence: number | null;
  severity_percent: number | null;
  is_healthy: boolean;
};

export type AnalyticsSummaryResponse = {
  total_predictions: number;
  predictions_in_window: number;
  predictions_last_7_days: number;
  healthy_count: number;
  diseased_count: number;
  avg_confidence: number | null;
  avg_severity_percent: number | null;
  critical_cases_last_7_days: number;
  top_diseases: DiseaseCountItem[];
  source_breakdown: SourceCountItem[];
  trend_last_days: TrendPoint[];
  most_recent_prediction_at: string | null;
  recent_items: RecentPredictionItem[];
};

const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL?.trim() || "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BACKEND_BASE_URL}${path}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    const details = await response.text().catch(() => "");
    throw new Error(`Analytics API failed (${response.status}): ${details || response.statusText}`);
  }
  return (await response.json()) as T;
}

export async function fetchAnalyticsSummary(days = 30, trendDays = 14): Promise<AnalyticsSummaryResponse> {
  return fetchJson<AnalyticsSummaryResponse>(`/admin/analytics/summary?days=${days}&trend_days=${trendDays}`);
}
