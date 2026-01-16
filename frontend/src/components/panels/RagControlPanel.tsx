import type { RagSettings, RagStats, UploadedDocument } from "../../types/rag";
import InitializationCard from "../cards/InitializationCard";
import UploadCard from "../cards/UploadCard";

type Props = {
  settings: RagSettings;
  setSettings: (next: RagSettings) => void;
  uploads: UploadedDocument[];
  setUploads: (next: UploadedDocument[]) => void;
  stats: RagStats;
  setStats: (next: RagStats) => void;
};

export default function RagControlPanel({ settings, setSettings, uploads, setUploads, stats, setStats }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <h2 style={{ margin: 0 }}>RAG Control Panel</h2>

      <InitializationCard settings={settings} onApply={setSettings} />

      <UploadCard uploads={uploads} setUploads={setUploads} stats={stats} setStats={setStats} />


            {/* Global Stats */}
      <section
        style={{
          border: "1px solid rgba(0,0,0,0.1)",
          borderRadius: 12,
          padding: 12,
        }}
      >
        <h3 style={{ marginTop: 0 }}>Global Stats</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <div>
            <div style={{ fontSize: 12, opacity: 0.7 }}>Documents</div>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{stats.documentCount}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, opacity: 0.7 }}>Chunks</div>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{stats.chunkCount}</div>
          </div>
        </div>
        {stats.lastIndexedAt && (
          <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
            last indexed: {new Date(stats.lastIndexedAt).toLocaleString()}
          </div>
        )}
      </section>
    </div>
  );
}
