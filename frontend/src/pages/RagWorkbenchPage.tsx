import { useEffect, useState } from "react";
import RagLayout from "../components/layout/RagLayout";
import RagControlPanel from "../components/panels/RagControlPanel";
import RagWorkspace from "../components/panels/RagWorkspace";
import type { RagSettings, RagStats, RagTurn, UploadedDocument } from "../types/rag";
import { fetchStats, setBackendSettings } from "../api/ragApi";
import { loadJson, saveJson } from "../utils/storage";

// Default UI/backend settings used on first load and reset.
const DEFAULT_SETTINGS: RagSettings = {
  llmModel: "openai/gpt-oss-20b",
  topK: 5,
  chunkSize: 50,
  chunkOverlap: 15,
  temperature: 0.2,
  maxTokens: 3500,
};

// Local storage keys for persistent client-side state.
const SETTINGS_KEY = "rag_settings_v1";
const UPLOADS_KEY = "rag_uploads_v1";

/**
 * Main page container that wires layout, control panel state, and workspace state.
 */
export default function RagWorkbenchPage() {
  const [stats, setStats] = useState<RagStats>({ documentCount: 0, chunkCount: 0 });
  const [turns, setTurns] = useState<RagTurn[]>([]);

  // Restore persisted settings/uploads from local storage on initial mount.
  const [settings, setSettings] = useState<RagSettings>(() => loadJson(SETTINGS_KEY, DEFAULT_SETTINGS));
  const [uploads, setUploads] = useState<UploadedDocument[]>(() => loadJson(UPLOADS_KEY, []));

  /**
   * Applies settings through the backend and stores the confirmed response.
   */
  async function handleApply(next: RagSettings) {
    const confirmed = await setBackendSettings(next);
    setSettings(confirmed);
  }

  // Load current backend stats once when page mounts.
  useEffect(() => {
    (async () => {
      const s = await fetchStats();
      setStats(s);
    })();
  }, []);

  // Persist settings whenever they change.
  useEffect(() => {
    saveJson(SETTINGS_KEY, settings);
  }, [settings]);

  // Persist uploaded document metadata whenever it changes.
  useEffect(() => {
    saveJson(UPLOADS_KEY, uploads);
  }, [uploads]);

  // Render split layout with control panel on the left and conversation workspace on the right.
  return (
    <RagLayout
      left={
        <RagControlPanel
          settings={settings}
          setSettings={handleApply}
          uploads={uploads}
          setUploads={setUploads}
          stats={stats}
          setStats={setStats}
          defaultSettings={DEFAULT_SETTINGS}
        />
      }
      right={<RagWorkspace turns={turns} setTurns={setTurns} settings={settings} />}
    />
  );
}
