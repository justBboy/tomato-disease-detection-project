export function formatConfidence(value: number | null): string {
  if (value == null) {
    return "N/A";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export function formatSeverity(value: number | null): string {
  if (value == null) {
    return "N/A";
  }
  return `${value.toFixed(1)}%`;
}

export function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}
