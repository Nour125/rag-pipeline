import { useState } from "react";
import type { RagStats } from "../../types/rag";
import { fetchStats } from "../../api/ragApi";

type Props = {
  stats: RagStats;
  setStats: (next: RagStats) => void;
};

/**
 * Displays global RAG statistics and allows manual refresh from the backend.
 */
export default function GlobalStatsCard({ stats, setStats }: Props) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches the latest stats and updates local state while preserving lastIndexedAt fallback.
   */
  async function handleRefresh() {
    setIsLoading(true);
    setError(null);
    try {
      const s = await fetchStats();
      // Keep lastIndexedAt if backend doesn't send it
      setStats({
        ...stats,
        ...s,
        lastIndexedAt: s.lastIndexedAt ?? stats.lastIndexedAt,
      });
    } catch (e: any) {
      setError(e?.message ?? "Failed to fetch stats");
    } finally {
      setIsLoading(false);
    }
  }

  // Render a compact stats card with refresh action and error feedback.
  return (
    <section
      style={{
        border: "1px solid rgba(0,0,0,0.1)",
        borderRadius: 12,
        padding: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Global Stats</h3>

        <button
          style={{
            padding: "6px 10px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.15)",
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: isLoading ? 0.6 : 1,
            fontWeight: 600,
          }}
          onClick={handleRefresh}
          disabled={isLoading}
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <div>
          <div style={{ fontSize: 12, opacity: 0.7 }}>Documents</div>
          <div style={{ fontSize: 18, fontWeight: 700 }}>{stats.documentCount}</div>
        </div>
        <div>
          <div style={{ fontSize: 12, opacity: 0.7 }}>Chunks</div>
          <div style={{ fontSize: 18, fontWeight: 700 }}>{stats.chunkCount}</div>
        </div>
      </div>

      {stats.lastIndexedAt && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
          last indexed: {new Date(stats.lastIndexedAt).toLocaleString()}
        </div>
      )}

      {error && (
        <div style={{ marginTop: 10, fontSize: 13 }}>
          <b style={{ color: "crimson" }}>Error:</b> {error}
        </div>
      )}
    </section>
  );
}
