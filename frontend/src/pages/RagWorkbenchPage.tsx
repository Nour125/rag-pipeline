import { useEffect, useState } from "react";
import RagLayout from "../components/layout/RagLayout";
import RagControlPanel from "../components/panels/RagControlPanel";
import RagWorkspace from "../components/panels/RagWorkspace";
import type { RagSettings, RagStats, RagTurn, UploadedDocument } from "../types/rag";
import { fetchStats } from "../api/ragApi";
import { setBackendSettings } from "../api/ragApi";

const DEFAULT_SETTINGS: RagSettings = {
  llmModel: "qwen/qwen3-vl-4b",
  topK: 5,
  chunkSize: 100,
  chunkOverlap: 20,
  temperature: 0.2,
  maxTokens: 2048,

};

export default function RagWorkbenchPage() {
  const [settings, setSettings] = useState<RagSettings>(DEFAULT_SETTINGS);
  const [uploads, setUploads] = useState<UploadedDocument[]>([]);
  const [stats, setStats] = useState<RagStats>({ documentCount: 0, chunkCount: 0 });
  const [turns, setTurns] = useState<RagTurn[]>([]);

    async function handleApply(next: RagSettings) {
        const confirmed = await setBackendSettings(next);
        setSettings(confirmed);
    }

  // Phase A: load stats (stubbed currently)
  useEffect(() => {
    (async () => {
      const s = await fetchStats();
      setStats(s);
    })();
  }, []);

  return (
    <RagLayout
      left={
        <RagControlPanel
          settings={settings}
          setSettings={handleApply}
          uploads={uploads}
          stats={stats}
        />
      }
      right={<RagWorkspace turns={turns} />}
    />
  );
}
