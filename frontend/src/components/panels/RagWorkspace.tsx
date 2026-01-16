import type { RagTurn } from "../../types/rag";

type Props = {
  turns: RagTurn[];
};

export default function RagWorkspace({ turns }: Props) {
  return (
    <div style={{ maxWidth: 980, margin: "0 auto", display: "flex", flexDirection: "column", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>RAG Workbench</h1>
        <p style={{ margin: "6px 0 0 0", opacity: 0.75 }}>
          Chat + sources will appear as a timeline (one block per question).
        </p>
      </header>

      {/* Phase A: empty state */}
      {turns.length === 0 ? (
        <div
          style={{
            border: "1px dashed rgba(0,0,0,0.25)",
            borderRadius: 12,
            padding: 16,
            opacity: 0.9,
          }}
        >
          No questions yet. In Phase E we will add the chat composer + timeline.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {turns.map((t) => (
            <div key={t.id} style={{ border: "1px solid rgba(0,0,0,0.1)", borderRadius: 12, padding: 12 }}>
              <div style={{ fontWeight: 700 }}>Q:</div>
              <div style={{ marginBottom: 10 }}>{t.question}</div>

              <div style={{ fontWeight: 700 }}>A:</div>
              <div>{t.answer}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
