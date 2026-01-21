import type { RagSettings, RagStats, UploadedDocument } from "../../types/rag";
import GlobalStatsCard from "../cards/GlobalStatsCard";
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
      <GlobalStatsCard stats={stats} setStats={setStats} />
      
    </div>
  );
}
