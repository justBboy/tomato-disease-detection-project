"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchAnalyticsSummary, type AnalyticsSummaryResponse } from "@/lib/api";

import styles from "./page.module.css";

function formatPercent(value: number | null, digits = 1): string {
  if (value == null) {
    return "N/A";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

function formatNumber(value: number | null): string {
  if (value == null) {
    return "N/A";
  }
  return Intl.NumberFormat().format(value);
}

function formatDateTime(value: string | null): string {
  if (!value) {
    return "N/A";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString();
}

export default function Home() {
  const [summary, setSummary] = useState<AnalyticsSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setLoading(true);
    try {
      const next = await fetchAnalyticsSummary(30, 14);
      setSummary(next);
      setError("");
      setLastUpdatedAt(new Date().toISOString());
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Failed to load analytics data from backend.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSummary();
    const intervalId = window.setInterval(() => {
      void loadSummary();
    }, 60_000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [loadSummary]);

  const healthyShare = useMemo(() => {
    if (!summary || summary.total_predictions === 0) {
      return null;
    }
    return summary.healthy_count / summary.total_predictions;
  }, [summary]);

  const topDisease = summary?.top_diseases[0] ?? null;

  const peakDay = useMemo(() => {
    if (!summary || summary.trend_last_days.length === 0) {
      return null;
    }
    return summary.trend_last_days.reduce((best, current) => {
      if (!best || current.count > best.count) {
        return current;
      }
      return best;
    }, summary.trend_last_days[0]);
  }, [summary]);

  return (
    <div className={styles.page}>
      <header className={styles.hero}>
        <div>
          <p className={styles.kicker}>Tomato Disease Detection Project</p>
          <h1 className={styles.title}>Admin Analytics Dashboard</h1>
          <p className={styles.subtitle}>
            Monitor disease trends, most frequent conditions, and recent checks from prediction activity.
          </p>
        </div>
        <button className={styles.refreshButton} onClick={() => void loadSummary()} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh Data"}
        </button>
      </header>

      <section className={styles.metaRow}>
        <span>Last updated: {formatDateTime(lastUpdatedAt)}</span>
        <span>Most recent prediction: {formatDateTime(summary?.most_recent_prediction_at ?? null)}</span>
      </section>

      {error ? <div className={styles.errorBox}>{error}</div> : null}

      <section className={styles.kpiGrid}>
        <article className={styles.kpiCard}>
          <h3>Total Checks</h3>
          <p>{formatNumber(summary?.total_predictions ?? null)}</p>
          <small>All-time predictions logged by backend</small>
        </article>
        <article className={styles.kpiCard}>
          <h3>Checks (Last 7 Days)</h3>
          <p>{formatNumber(summary?.predictions_last_7_days ?? null)}</p>
          <small>Recent activity volume</small>
        </article>
        <article className={styles.kpiCard}>
          <h3>Healthy Share</h3>
          <p>{formatPercent(healthyShare)}</p>
          <small>Healthy detections out of total checks</small>
        </article>
        <article className={styles.kpiCard}>
          <h3>Average Severity</h3>
          <p>
            {summary?.avg_severity_percent != null ? `${summary.avg_severity_percent.toFixed(1)}%` : "N/A"}
          </p>
          <small>Average severity across available segmentation outputs</small>
        </article>
      </section>

      <section className={styles.contentGrid}>
        <article className={styles.panel}>
          <h2>Most Common Diseases</h2>
          <p className={styles.panelHint}>Top disease classes by count.</p>
          {summary?.top_diseases?.length ? (
            <ul className={styles.list}>
              {summary.top_diseases.map((item) => (
                <li key={item.raw_class} className={styles.listItem}>
                  <div className={styles.listTop}>
                    <span>{item.display_name}</span>
                    <strong>{item.count}</strong>
                  </div>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{ width: `${Math.max(4, item.share * 100)}%` }} />
                  </div>
                  <small>{formatPercent(item.share)}</small>
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles.emptyText}>No disease data yet. Run predictions to populate this panel.</p>
          )}
        </article>

        <article className={styles.panel}>
          <h2>Prediction Trend (14 Days)</h2>
          <p className={styles.panelHint}>Daily prediction counts for recent trend monitoring.</p>
          {summary?.trend_last_days?.length ? (
            <div className={styles.trendBars}>
              {summary.trend_last_days.map((point) => {
                const maxCount = Math.max(...summary.trend_last_days.map((entry) => entry.count), 1);
                const barHeight = `${Math.max(8, (point.count / maxCount) * 100)}%`;
                return (
                  <div key={point.date} className={styles.trendColumn}>
                    <div className={styles.trendValue}>{point.count}</div>
                    <div className={styles.trendBarWrap}>
                      <div className={styles.trendBar} style={{ height: barHeight }} />
                    </div>
                    <div className={styles.trendLabel}>{point.date.slice(5)}</div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className={styles.emptyText}>No trend data yet.</p>
          )}
        </article>
      </section>

      <section className={styles.contentGrid}>
        <article className={styles.panel}>
          <h2>Source Breakdown</h2>
          <p className={styles.panelHint}>Which endpoints are contributing most of the prediction traffic.</p>
          {summary?.source_breakdown?.length ? (
            <ul className={styles.list}>
              {summary.source_breakdown.map((item) => (
                <li key={item.source} className={styles.sourceItem}>
                  <span className={styles.sourceName}>{item.source}</span>
                  <span>{item.count}</span>
                  <span>{formatPercent(item.share)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles.emptyText}>No source metrics available yet.</p>
          )}
        </article>

        <article className={styles.panel}>
          <h2>Insights</h2>
          <p className={styles.panelHint}>Quick interpretation of current dataset.</p>
          <ul className={styles.insightList}>
            <li>
              Top disease class:
              <strong>{topDisease ? ` ${topDisease.display_name} (${topDisease.count})` : " N/A"}</strong>
            </li>
            <li>
              Critical cases in last 7 days (severity {"\u003e="} 30%):
              <strong>{` ${formatNumber(summary?.critical_cases_last_7_days ?? null)}`}</strong>
            </li>
            <li>
              Average confidence:
              <strong>{` ${summary?.avg_confidence != null ? formatPercent(summary.avg_confidence) : "N/A"}`}</strong>
            </li>
            <li>
              Peak day in current trend window:
              <strong>{peakDay ? ` ${peakDay.date} (${peakDay.count})` : " N/A"}</strong>
            </li>
          </ul>
        </article>
      </section>

      <section className={styles.panel}>
        <h2>Recent Prediction Activity</h2>
        <p className={styles.panelHint}>Latest logged predictions from API usage.</p>
        {summary?.recent_items?.length ? (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Condition</th>
                  <th>Source</th>
                  <th>Confidence</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_items.map((item) => (
                  <tr key={item.id}>
                    <td>{formatDateTime(item.timestamp)}</td>
                    <td>{item.display_name}</td>
                    <td>{item.source}</td>
                    <td>{item.confidence != null ? formatPercent(item.confidence) : "N/A"}</td>
                    <td>{item.severity_percent != null ? `${item.severity_percent.toFixed(1)}%` : "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className={styles.emptyText}>No recent predictions to display yet.</p>
        )}
      </section>
    </div>
  );
}
