import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(timestamp: datetime) -> str:
    return timestamp.isoformat().replace("+00:00", "Z")


def _parse_iso(timestamp: str) -> Optional[datetime]:
    candidate = (timestamp or "").strip()
    if not candidate:
        return None
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        return None


def _to_display_name(raw_class: str) -> str:
    cleaned = raw_class.replace("Tomato___", "").replace("_", " ").strip()
    if not cleaned:
        return "Unknown"

    normalized = " ".join(cleaned.split())
    titled = normalized.title()
    # Preserve common acronym capitalization for readability.
    titled = titled.replace("Tylcv", "TYLCV").replace("Tomv", "ToMV")
    return titled


def _is_healthy(raw_class: str) -> bool:
    return "healthy" in raw_class.lower()


class AnalyticsService:
    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        if not self.store_path.exists():
            self.store_path.write_text("", encoding="utf-8")

    def record_prediction(
        self,
        source: str,
        predicted_class: str,
        confidence: Optional[float],
        severity_percent: Optional[float],
    ) -> None:
        event = {
            "timestamp": _to_iso(_utc_now()),
            "source": source,
            "raw_class": predicted_class,
            "display_name": _to_display_name(predicted_class),
            "confidence": confidence,
            "severity_percent": severity_percent,
            "is_healthy": _is_healthy(predicted_class),
        }

        line = json.dumps(event, ensure_ascii=True)
        try:
            with self._lock:
                with self.store_path.open("a", encoding="utf-8") as file:
                    file.write(line + "\n")
        except OSError as error:
            logger.warning("Could not write analytics event: %s", error)

    def _read_events(self) -> List[Dict[str, Any]]:
        if not self.store_path.exists():
            return []

        rows: List[Dict[str, Any]] = []
        with self.store_path.open("r", encoding="utf-8") as file:
            for line in file:
                candidate = line.strip()
                if not candidate:
                    continue
                try:
                    row = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                row_timestamp = _parse_iso(str(row.get("timestamp", "")))
                if row_timestamp is None:
                    continue
                row["parsed_timestamp"] = row_timestamp
                rows.append(row)

        rows.sort(key=lambda row: row["parsed_timestamp"], reverse=True)
        return rows

    def get_recent(self, limit: int = 20) -> Dict[str, Any]:
        safe_limit = max(1, min(limit, 100))
        events = self._read_events()[:safe_limit]
        items = []
        for index, row in enumerate(events):
            items.append(
                {
                    "id": f"{row.get('timestamp', '')}_{index}",
                    "timestamp": row.get("timestamp"),
                    "source": row.get("source", "unknown"),
                    "raw_class": row.get("raw_class", "Unknown"),
                    "display_name": row.get("display_name", "Unknown"),
                    "confidence": row.get("confidence"),
                    "severity_percent": row.get("severity_percent"),
                    "is_healthy": bool(row.get("is_healthy", False)),
                }
            )
        return {"items": items}

    def get_summary(self, days: int = 30, trend_days: int = 14) -> Dict[str, Any]:
        safe_days = max(1, min(days, 365))
        safe_trend_days = max(1, min(trend_days, 90))
        events = self._read_events()
        now = _utc_now()
        window_start = now - timedelta(days=safe_days)
        last_7_start = now - timedelta(days=7)

        window_events = [row for row in events if row["parsed_timestamp"] >= window_start]
        last_7_events = [row for row in events if row["parsed_timestamp"] >= last_7_start]

        total_predictions = len(events)
        healthy_count = sum(1 for row in events if bool(row.get("is_healthy", False)))
        diseased_count = total_predictions - healthy_count

        confidence_values = [
            float(row["confidence"])
            for row in events
            if isinstance(row.get("confidence"), (int, float))
        ]
        severity_values = [
            float(row["severity_percent"])
            for row in events
            if isinstance(row.get("severity_percent"), (int, float))
        ]

        avg_confidence = round(sum(confidence_values) / len(confidence_values), 4) if confidence_values else None
        avg_severity_percent = round(sum(severity_values) / len(severity_values), 2) if severity_values else None

        diseased_rows = [row for row in events if not bool(row.get("is_healthy", False))]
        class_counts = Counter(row.get("raw_class", "Unknown") for row in diseased_rows)
        top_diseases = []
        top_total = sum(class_counts.values()) or 1
        for raw_class, count in class_counts.most_common(5):
            top_diseases.append(
                {
                    "raw_class": raw_class,
                    "display_name": _to_display_name(raw_class),
                    "count": count,
                    "share": round(count / top_total, 4),
                }
            )

        source_counts = Counter(str(row.get("source", "unknown")) for row in events)
        source_breakdown = []
        for source, count in source_counts.most_common():
            source_breakdown.append(
                {
                    "source": source,
                    "count": count,
                    "share": round(count / (total_predictions or 1), 4),
                }
            )

        trend_start = now.date() - timedelta(days=safe_trend_days - 1)
        trend_map: Dict[str, int] = defaultdict(int)
        for row in window_events:
            date_key = row["parsed_timestamp"].date().isoformat()
            trend_map[date_key] += 1

        trend_last_days = []
        for offset in range(safe_trend_days):
            date_key = (trend_start + timedelta(days=offset)).isoformat()
            trend_last_days.append({"date": date_key, "count": trend_map.get(date_key, 0)})

        recent = self.get_recent(limit=10)
        most_recent = events[0].get("timestamp") if events else None
        critical_cases_last_7_days = sum(
            1
            for row in last_7_events
            if isinstance(row.get("severity_percent"), (int, float)) and float(row["severity_percent"]) >= 30.0
        )

        return {
            "total_predictions": total_predictions,
            "predictions_in_window": len(window_events),
            "predictions_last_7_days": len(last_7_events),
            "healthy_count": healthy_count,
            "diseased_count": diseased_count,
            "avg_confidence": avg_confidence,
            "avg_severity_percent": avg_severity_percent,
            "critical_cases_last_7_days": critical_cases_last_7_days,
            "top_diseases": top_diseases,
            "source_breakdown": source_breakdown,
            "trend_last_days": trend_last_days,
            "most_recent_prediction_at": most_recent,
            "recent_items": recent["items"],
        }
