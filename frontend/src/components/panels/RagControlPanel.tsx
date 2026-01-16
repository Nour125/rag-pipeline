import type { RagSettings, RagStats, UploadedDocument } from "../../types/rag";
import InitializationCard from "../cards/InitializationCard";

type Props = {
  settings: RagSettings;
  setSettings: (next: RagSettings) => void;
  uploads: UploadedDocument[];
  stats: RagStats;
};

export default function RagControlPanel({ settings, setSettings, uploads, stats }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <h2 style={{ margin: 0 }}>RAG Control Panel</h2>

      {/* Phase B: InitializationCard */}
      <InitializationCard settings={settings} onApply={setSettings} />

      {/* Upload (placeholder for Phase C) */}
      <section
        style={{
          border: "1px solid rgba(0,0,0,0.1)",
          borderRadius: 12,
          padding: 12,
        }}
      >
        <h3 style={{ marginTop: 0 }}>Upload PDFs</h3>
        <p style={{ margin: 0, opacity: 0.8 }}>
          (Placeholder) – upload UI comes in Phase C.
        </p>

        <div style={{ marginTop: 10, fontSize: 13, opacity: 0.9 }}>
          Uploaded: <b>{uploads.length}</b>
        </div>
      </section>

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
      </section>
    </div>
  );
}
