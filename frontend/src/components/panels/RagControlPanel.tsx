import type { RagSettings, RagStats, UploadedDocument } from "../../types/rag";
import GlobalStatsCard from "../cards/GlobalStatsCard";
import InitializationCard from "../cards/InitializationCard";
import UploadCard from "../cards/UploadCard";

type Props = {
  // Current RAG generation and retrieval settings.
  settings: RagSettings;
  // Applies updated settings from the initialization card.
  setSettings: (next: RagSettings) => void;
  // Uploaded documents displayed in the upload card list.
  uploads: UploadedDocument[];
  // Updates the uploaded documents collection.
  setUploads: (next: UploadedDocument[]) => void;
  // Aggregated index statistics shown in the stats card.
  stats: RagStats;
  // Updates aggregated index statistics.
  setStats: (next: RagStats) => void;
  // Baseline settings used by the reset action.
  defaultSettings: RagSettings;
};

/**
 * Composes the full left-side control panel for settings, uploads, and global stats.
 */
export default function RagControlPanel({ settings, setSettings, uploads, setUploads, stats, setStats, defaultSettings }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <h2 style={{ margin: 0 }}>RAG Control Panel</h2>
      <InitializationCard settings={settings} onApply={setSettings} defaultSettings={defaultSettings} />
      <UploadCard uploads={uploads} setUploads={setUploads} stats={stats} setStats={setStats} />
      <GlobalStatsCard stats={stats} setStats={setStats} />
    </div>
  );
}
