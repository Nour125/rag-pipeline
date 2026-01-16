import { useEffect, useMemo, useState } from "react";
import type { RagSettings } from "../../types/rag";

type Props = {
  settings: RagSettings;
  onApply: (next: RagSettings) => void;
};

export default function InitializationCard({ settings, onApply }: Props) {
  // Dummy list (später vom Backend / LM Studio)
  const modelOptions = useMemo(
    () => [
      { id: "qwen/qwen3-vl-4b", label: "LM Studio (default)" },
      { id: "llama-3.1-8b-instruct", label: "Llama 3.1 8B Instruct" },
      { id: "openai/gpt-oss-20b", label: "OpenAI GPT OSS 20B" },
      { id: "qwen2.5-7b-instruct", label: "Qwen 2.5 7B Instruct" },
    ],
    []
  );

  // Draft state (editable without instantly applying)
  const [draft, setDraft] = useState<RagSettings>(settings);

  // Keep draft in sync if settings changes elsewhere
  useEffect(() => {
    setDraft(settings);
  }, [settings]);

  const changed = JSON.stringify(draft) !== JSON.stringify(settings);

  return (
    <section
      style={{
        border: "1px solid rgba(0,0,0,0.1)",
        borderRadius: 12,
        padding: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Initialization</h3>
        <span style={{ fontSize: 12, opacity: 0.7 }}>
          {changed ? "Not applied" : "Applied"}
        </span>
      </div>

      {/* Model Dropdown */}
      <label style={{ display: "block", marginBottom: 10 }}>
        LLM Model
        <select
          style={{ width: "100%", padding: 8, marginTop: 4 }}
          value={draft.llmModel}
          onChange={(e) => setDraft({ ...draft, llmModel: e.target.value })}
        >
          {modelOptions.map((m) => (
            <option key={m.id} value={m.id}>
              {m.label}
            </option>
          ))}
        </select>
      </label>

      {/* top_k slider */}
      <label style={{ display: "block", marginBottom: 10 }}>
        top_k: <b>{draft.topK}</b>
        <input
          style={{ width: "100%", marginTop: 6 }}
          type="range"
          min={1}
          max={10}
          value={draft.topK}
          onChange={(e) => setDraft({ ...draft, topK: Number(e.target.value) })}
        />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, opacity: 0.7 }}>
          <span>1</span>
          <span>10</span>
        </div>
      </label>

      {/* Chunk size + overlap */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
        <label style={{ display: "block" }}>
          Chunk size (words)
          <input
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            type="number"
            min={10}
            max={5000}
            value={draft.chunkSize}
            onChange={(e) => setDraft({ ...draft, chunkSize: Number(e.target.value) })}
          />
        </label>

        <label style={{ display: "block" }}>
          Overlap (words)
          <input
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            type="number"
            min={0}
            max={1000}
            value={draft.chunkOverlap}
            onChange={(e) => setDraft({ ...draft, chunkOverlap: Number(e.target.value) })}
          />
        </label>
      </div>

      {/* Temperature + maxTokens */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>
        <label style={{ display: "block" }}>
          Temperature
          <input
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            type="number"
            step={0.1}
            min={0}
            max={2}
            value={draft.temperature}
            onChange={(e) => setDraft({ ...draft, temperature: Number(e.target.value) })}
          />
        </label>

        <label style={{ display: "block" }}>
          Max tokens
          <input
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            type="number"
            min={16}
            max={4096}
            value={draft.maxTokens}
            onChange={(e) => setDraft({ ...draft, maxTokens: Number(e.target.value) })}
          />
        </label>
      </div>

      {/* Apply button */}
      <button
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid rgba(0,0,0,0.15)",
          cursor: changed ? "pointer" : "not-allowed",
          opacity: changed ? 1 : 0.6,
          fontWeight: 600,
        }}
        disabled={!changed}
        onClick={() => onApply(draft)}
      >
        Apply settings
      </button>

    </section>
  );
}
