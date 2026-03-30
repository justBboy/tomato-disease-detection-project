import AsyncStorage from "@react-native-async-storage/async-storage";

import type { AnalysisHistoryItem, PredictionTask } from "@/types/history";

const HISTORY_STORAGE_KEY = "tomato_ai.history.v2";
export const MAX_HISTORY_ITEMS = 40;

function isValidHistoryItem(entry: unknown): entry is AnalysisHistoryItem {
  if (typeof entry !== "object" || entry == null) {
    return false;
  }
  const candidate = entry as Partial<AnalysisHistoryItem>;
  return (
    typeof candidate.id === "string" &&
    typeof candidate.timestamp === "string" &&
    typeof candidate.sourceUri === "string" &&
    typeof candidate.rawClass === "string" &&
    typeof candidate.displayName === "string" &&
    (candidate.task === "classification" || candidate.task === "segmentation" || candidate.task === "full")
  );
}

export async function loadHistory(): Promise<AnalysisHistoryItem[]> {
  try {
    const raw = await AsyncStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter(isValidHistoryItem).slice(0, MAX_HISTORY_ITEMS);
  } catch {
    return [];
  }
}

async function saveHistory(entries: AnalysisHistoryItem[]): Promise<void> {
  await AsyncStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_HISTORY_ITEMS)));
}

export async function appendHistoryEntry(
  task: PredictionTask,
  sourceUri: string,
  rawClass: string,
  displayName: string,
  confidence: number | null,
  severityPercent: number | null
): Promise<AnalysisHistoryItem[]> {
  const existing = await loadHistory();
  const nextEntry: AnalysisHistoryItem = {
    id: `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    timestamp: new Date().toISOString(),
    sourceUri,
    task,
    rawClass,
    displayName,
    confidence,
    severityPercent,
  };

  const updated = [nextEntry, ...existing].slice(0, MAX_HISTORY_ITEMS);
  await saveHistory(updated);
  return updated;
}

export async function clearHistoryStorage(): Promise<void> {
  await AsyncStorage.removeItem(HISTORY_STORAGE_KEY);
}
