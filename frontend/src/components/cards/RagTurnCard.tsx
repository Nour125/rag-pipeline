import type { RagTurn } from "../../types/rag";
import { marked } from "marked";

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

export default function RagTurnCard({ turn }: { turn: RagTurn }) {
    const htmlContent = marked(turn.answer ?? "null");

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

      {/* Answer */}
      <div style={{ marginTop: 12 }}>
        <div style={{ fontSize: 12, opacity: 0.65, marginBottom: 6 }}>Answer</div>
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.45 }} dangerouslySetInnerHTML={{ __html: htmlContent }}></div>
      </div>

      {/* Sources */}
      <div style={{ marginTop: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <div style={{ fontSize: 12, opacity: 0.65 }}>Top sources ({turn.sources.length})</div>
        </div>

        {turn.sources.length === 0 ? (
          <div style={{ fontSize: 13, opacity: 0.75, marginTop: 8 }}>No sources returned.</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginTop: 8 }}>
            {turn.sources.map((s) => {
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
                    {typeof s.pageId === "number" ? <> • page: <b>{s.pageId}</b></> : null}
                  </div>

                  {/* Snippet */}
                  <div style={{ marginTop: 10, fontSize: 13, whiteSpace: "pre-wrap" }}>
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
      {/* Timestamp */}
      <div style={{ marginTop: 10, fontSize: 11, opacity: 0.55 }}>
        {new Date(turn.createdAt).toLocaleString()}
      </div>
    </div>
  );
}
