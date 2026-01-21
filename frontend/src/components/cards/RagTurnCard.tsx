import type { RagTurn } from "../../types/rag";
import { marked } from "marked";
import { useMemo, useState } from "react";

function Badge({ text }: { text: string }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        fontSize: 12,
        border: "1px solid rgba(0,0,0,0.15)",
        opacity: 0.85,
      }}
    >
      {text}
    </span>
  );
}
function SmallButton({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "6px 10px",
        borderRadius: 10,
        border: "1px solid rgba(0,0,0,0.15)",
        cursor: "pointer",
        fontWeight: 650,
        fontSize: 12,
        opacity: 0.9,
      }}
    >
      {children}
    </button>
  );
}

export default function RagTurnCard({ turn }: { turn: RagTurn }) {
    const htmlContent = marked(turn.answer ?? "null");
    const [sourcesOpen, setSourcesOpen] = useState(true);
    const hasSources = turn.sources.length > 0;

    const previewSources = useMemo(() => {
    // show first 3 by default if collapsed
    return sourcesOpen ? turn.sources : turn.sources.slice(0, 3);
  }, [sourcesOpen, turn.sources]);

  async function copyAnswer() {
    try {
      await navigator.clipboard.writeText(turn.answer || "");
    } catch {
      // fallback: do nothing
    }
  }
  return (
    <div style={{ border: "1px solid rgba(0,0,0,0.1)", borderRadius: 14, padding: 14 }}>
      {/* User question (right aligned) */}
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <div
          style={{
            maxWidth: "85%",
            padding: 12,
            borderRadius: 14,
            border: "1px solid rgba(0,0,0,0.12)",
            fontWeight: 600,
          }}
        >
          {turn.question}
        </div>
      </div>

      {/* Answer header + actions */}
      <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div style={{ fontSize: 12, opacity: 0.65 }}>Answer</div>
        <div style={{ display: "flex", gap: 8 }}>
          {turn.status === "success" && turn.answer?.trim() && (
            <SmallButton onClick={copyAnswer}>Copy answer</SmallButton>
          )}
          {hasSources && (
            <SmallButton onClick={() => setSourcesOpen((v) => !v)}>
              {sourcesOpen ? "Collapse sources" : "Expand sources"}
            </SmallButton>
          )}
        </div>
      </div>
      
      {/* Answer body */}
      <div style={{ marginTop: 6 }}>
        {turn.status === "loading" && (
          <div style={{ display: "flex", gap: 10, alignItems: "center", opacity: 0.8 }}>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                border: "2px solid rgba(0,0,0,0.2)",
                borderTopColor: "rgba(0,0,0,0.65)",
                animation: "spin 0.8s linear infinite",
              }}
            />
            <div>Generating answer…</div>
            <style>
              {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
            </style>
          </div>
        )}

        {turn.status === "error" && (
          <div
            style={{
              border: "1px solid rgba(220,20,60,0.35)",
              background: "rgba(220,20,60,0.06)",
              borderRadius: 12,
              padding: 12,
            }}
          >
            <div style={{ fontWeight: 800, color: "crimson" }}>Request failed</div>
            <div style={{ marginTop: 6, opacity: 0.9 }}>{turn.errorMessage ?? "Unknown error"}</div>
          </div>
        )}

        {turn.status === "success" && (
          <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}dangerouslySetInnerHTML={{ __html: htmlContent }}/>
        )}
      </div>

      {/* Sources */}
      <div style={{ marginTop: 14 }}>
        <div style={{ fontSize: 12, opacity: 0.65 }}>
          Top sources ({turn.sources.length}){!sourcesOpen && turn.sources.length > 3 ? " • showing 3" : ""}
        </div>

        {turn.status === "success" && turn.sources.length === 0 ? (
          <div style={{ fontSize: 13, opacity: 0.75, marginTop: 8 }}>No sources returned.</div>
        ) : null}

        {turn.status !== "success" ? null : (
          <div style={{ marginTop: 8 }}>
            {previewSources.length === 0 ? null : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                {previewSources.map((s) => {
                  const isChild = Boolean(s.isChildChunk);
                  return (
                    <div
                      key={`${s.documentId}-${s.chunkId}-${s.rank}`}
                      style={{
                        border: isChild ? "2px solid rgba(255, 165, 0, 0.7)" : "1px solid rgba(0,0,0,0.08)",
                        borderRadius: 12,
                        padding: 10,
                        background: isChild ? "rgba(255,165,0,0.06)" : "transparent",
                      }}
                    >
                      {/* Header */}
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <div style={{ fontWeight: 800, fontSize: 13 }}>#{s.rank}</div>
                          {isChild && <Badge text="child chunk" />}
                        </div>

                        <div style={{ fontSize: 12, opacity: 0.75 }}>
                          score: <b>{s.score.toFixed(3)}</b>
                        </div>
                      </div>

                      {/* Meta */}
                      <div style={{ marginTop: 8, fontSize: 12, opacity: 0.75 }}>
                        doc: <b>{s.documentId}</b>
                      </div>

                      <div style={{ marginTop: 4, fontSize: 12, opacity: 0.75 }}>
                        chunk_index: <b>{s.chunkIndex ?? "—"}</b>{" "}
                        {typeof s.pageId === "number" ? (
                          <>
                            • page: <b>{s.pageId}</b>
                          </>
                        ) : null}
                      </div>

                      {/* Snippet (clamp when collapsed) */}
                      <div
                        style={{
                          marginTop: 10,
                          fontSize: 13,
                          whiteSpace: "pre-wrap",
                          lineHeight: 1.35,
                          maxHeight: sourcesOpen ? "none" : 110,
                          overflow: sourcesOpen ? "visible" : "hidden",
                        }}
                      >
                        {s.snippet}
                      </div>

                      {/* Link */}
                      <div style={{ marginTop: 10, fontSize: 12 }}>
                        {s.documentUrl ? (
                          <a href={s.documentUrl} target="_blank" rel="noreferrer" style={{ opacity: 0.85 }}>
                            Open document
                          </a>
                        ) : (
                          <span style={{ opacity: 0.6 }}>No document link</span>
                        )}
                      </div>

                      {/* Optional parent info */}
                      {s.parentBlockId ? (
                        <div style={{ marginTop: 6, fontSize: 11, opacity: 0.55 }}>
                          parent_block_id: {s.parentBlockId}
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
      {/* Timestamp */}
      <div style={{ marginTop: 10, fontSize: 11, opacity: 0.55 }}>
        {new Date(turn.createdAt).toLocaleString()}
      </div>
    </div>
  );
}
