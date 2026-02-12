import { useEffect, useMemo, useState } from "react";
import type { RagSettings } from "../../types/rag";

type Props = {
  settings: RagSettings;
  onApply: (next: RagSettings) => void;
  defaultSettings: RagSettings;

};

type StylePreset = "FACTUAL" | "BALANCED" | "CREATIVE";
type DepthPreset = "FAST" | "BALANCED" | "THOROUGH";

function mapStyleToTemperature(p: StylePreset): number {
  if (p === "FACTUAL") return 0.1;
  if (p === "BALANCED") return 0.3;
  return 0.7;
}

function mapDepthToTopK(p: DepthPreset): number {
  if (p === "FAST") return 3;
  if (p === "BALANCED") return 5;
  return 10;
}

function mapDepthToMaxTokens(p: DepthPreset): number {
  if (p === "FAST") return 500;
  if (p === "BALANCED") return 900;
  return 1400;
}



export default function InitializationCard({ settings, onApply, defaultSettings }: Props) {
  const modelOptions = useMemo(
    () => [
      { id: "deepseek/deepseek-r1-0528-qwen3-8b", label: "DeepSeek R1 0528 Qwen3 8B" },
      { id: "google/gemma-3-12b", label: "Google Gemma 3 12B" },
      { id: "meta-llama-3.1-8b-instruct", label: "Meta Llama 3.1 8B Instruct" },
      { id: "openai/gpt-oss-20b", label: "OpenAI GPT OSS 20B" },

    ],
    []
  );

  const [draft, setDraft] = useState<RagSettings>(settings);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Simple presets (local UI state)
  const [stylePreset, setStylePreset] = useState<StylePreset>("BALANCED");
  const [depthPreset, setDepthPreset] = useState<DepthPreset>("BALANCED");

  useEffect(() => setDraft(settings), [settings]);

  // Init presets roughly from existing settings
  useEffect(() => {
    // style
    if (settings.temperature <= 0.15) setStylePreset("FACTUAL");
    else if (settings.temperature <= 0.45) setStylePreset("BALANCED");
    else setStylePreset("CREATIVE");

    // depth
    if (settings.topK <= 3) setDepthPreset("FAST");
    else if (settings.topK <= 6) setDepthPreset("BALANCED");
    else setDepthPreset("THOROUGH");
  }, [settings.temperature, settings.topK]);

  const changed = JSON.stringify(draft) !== JSON.stringify(settings);
  function resetToDefault() {
    setDraft(defaultSettings);
    setStylePreset("BALANCED");
    setDepthPreset("BALANCED");
  }
  function applySimplePreset(nextStyle: StylePreset, nextDepth: DepthPreset) {
    const nextTemp = mapStyleToTemperature(nextStyle);
    const nextTopK = mapDepthToTopK(nextDepth);
    const nextMax = mapDepthToMaxTokens(nextDepth);

    setDraft((prev) => ({
      ...prev,
      temperature: nextTemp,
      topK: nextTopK,
      maxTokens: nextMax,
    }));
  }

  return (
    <section style={{ border: "1px solid rgba(0,0,0,0.1)", borderRadius: 12, padding: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>settings</h3>
        <span style={{ fontSize: 12, opacity: 0.7 }}>{changed ? "Not applied" : "Applied"}</span>
      </div>

      {/* Model */}
      <label style={{ display: "block", marginBottom: 10 }}>
        Model
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
        <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
          Choose the language model that generates the answers.
        </div>
      </label>

      {/* Simple controls */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
        <label style={{ display: "block" }}>
          Answer style
          <select
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            value={stylePreset}
            onChange={(e) => {
              const v = e.target.value as StylePreset;
              setStylePreset(v);
              applySimplePreset(v, depthPreset);
            }}
          >
            <option value="FACTUAL">Factual</option>
            <option value="BALANCED">Balanced</option>
            <option value="CREATIVE">Creative</option>
          </select>
          <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
            Factual = less "free" phrasing, Creative = more variation.
          </div>
        </label>

        <label style={{ display: "block" }}>
          Thoroughness
          <select
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            value={depthPreset}
            onChange={(e) => {
              const v = e.target.value as DepthPreset;
              setDepthPreset(v);
              applySimplePreset(stylePreset, v);
            }}
          >
            <option value="FAST">Fast</option>
            <option value="BALANCED">Normal</option>
            <option value="THOROUGH">Thorough</option>
          </select>
          <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
            Thorough checks more text passages (better, but slower).
          </div>
        </label>
      </div>

      {/* Advanced toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced((v) => !v)}
        style={{
          width: "100%",
          padding: "8px 10px",
          borderRadius: 10,
          border: "1px solid rgba(0,0,0,0.15)",
          cursor: "pointer",
          fontWeight: 650,
          opacity: 0.9,
          marginBottom: 10,
        }}
      >
        {showAdvanced ? "Hide advanced settings" : "Show advanced settings"}
      </button>

      {showAdvanced && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {/* top_k */}
          <label style={{ display: "block" }}>
            How many text passages to check? (top_k): <b>{draft.topK}</b>
            <input
              style={{ width: "100%", marginTop: 6 }}
              type="range"
              min={1}
              max={20}
              value={draft.topK}
              onChange={(e) => setDraft({ ...draft, topK: Number(e.target.value) })}
            />
            <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
              More = more thorough, but slower.
            </div>
          </label>

          {/* chunk size + overlap */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <label style={{ display: "block" }}>
              Chunk size
              <input
                style={{ width: "100%", marginTop: 4 }}
                type="number"
                min={50}
                max={10000}
                value={draft.chunkSize}
                onChange={(e) => setDraft({ ...draft, chunkSize: Number(e.target.value) })}
              />
              <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
                Small = more precise retrieval, large = more context per passage.
              </div>
            </label>

            <label style={{ display: "block" }}>
              Overlap
              <input
                style={{ width: "100%", marginTop: 4 }}
                type="number"
                min={0}
                max={1000}
                value={draft.chunkOverlap}
                onChange={(e) => setDraft({ ...draft, chunkOverlap: Number(e.target.value) })}
              />
              <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
                Helps ensure important sentences are not "split".
              </div>
            </label>
          </div>

          {/* temperature + maxTokens */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <label style={{ display: "block" }}>
              Creativity (Temperature)
              <input
                style={{ width: "100%", marginTop: 4 }}
                type="number"
                step={0.1}
                min={0}
                max={2}
                value={draft.temperature}
                onChange={(e) => setDraft({ ...draft, temperature: Number(e.target.value) })}
              />
              <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
                Low = more deterministic, high = more variation.
              </div>
            </label>

            <label style={{ display: "block" }}>
              Response length (Max tokens)
              <input
                style={{ width: "100%", marginTop: 4 }}
                type="number"
                min={16}
                max={4096}
                value={draft.maxTokens}
                onChange={(e) => setDraft({ ...draft, maxTokens: Number(e.target.value) })}
              />
              <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
                Limit for the response length (too high can be slower).
              </div>
            </label>
          </div>
        </div>
      )}

      {/* Apply */}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.15)",
            cursor: "pointer",
            fontWeight: 650,
            opacity: 0.85,
          }}
          type="button"
          onClick={resetToDefault}
        >
          Reset to default
        </button>

        <button
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.15)",
            cursor: changed ? "pointer" : "not-allowed",
            opacity: changed ? 1 : 0.6,
            fontWeight: 700,
          }}
          disabled={!changed}
          onClick={() => onApply(draft)}
        >
          Apply settings
        </button>
      </div>


      <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
        Tip: For normal use, “Answer style” and “Thoroughness” are sufficient.
      </div>
    </section>
  );
}
