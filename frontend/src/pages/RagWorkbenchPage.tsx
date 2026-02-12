import { useEffect, useState } from "react";
import RagLayout from "../components/layout/RagLayout";
import RagControlPanel from "../components/panels/RagControlPanel";
import RagWorkspace from "../components/panels/RagWorkspace";
import type { RagSettings, RagStats, RagTurn, UploadedDocument } from "../types/rag";
import { fetchStats } from "../api/ragApi";
import { setBackendSettings } from "../api/ragApi";
import { loadJson, saveJson } from "../utils/storage";

const DEFAULT_SETTINGS: RagSettings = {
  llmModel: "openai/gpt-oss-20b",
  topK: 5,
  chunkSize: 50,
  chunkOverlap: 15,
  temperature: 0.2,
  maxTokens: 3500,

};
const SETTINGS_KEY = "rag_settings_v1";
const UPLOADS_KEY = "rag_uploads_v1";



export default function RagWorkbenchPage() {
  // const [settings, setSettings] = useState<RagSettings>(DEFAULT_SETTINGS);
  // const [uploads, setUploads] = useState<UploadedDocument[]>([]);
  const [stats, setStats] = useState<RagStats>({ documentCount: 0, chunkCount: 0 });
  const [turns, setTurns] = useState<RagTurn[]>([]);
  const [settings, setSettings] = useState<RagSettings>(() => loadJson(SETTINGS_KEY, DEFAULT_SETTINGS));
  const [uploads, setUploads] = useState<UploadedDocument[]>(() => loadJson(UPLOADS_KEY, []));

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

  useEffect(() => {
    saveJson(SETTINGS_KEY, settings);
  }, [settings]);

  useEffect(() => {
    saveJson(UPLOADS_KEY, uploads);
  }, [uploads]);


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
