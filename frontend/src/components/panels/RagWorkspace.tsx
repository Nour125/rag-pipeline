import { useState } from "react";
import type { RagSettings, RagTurn } from "../../types/rag";
import ChatComposer from "../chat/ChatComposer";
import ConversationTimeline from "../chat/ConversationTimeline";
import { queryRag } from "../../api/ragApi";

/**
 * Generates a unique id for each conversation turn.
 */
function makeId() {
  return crypto.randomUUID();
}

type Props = {
  // All conversation turns rendered in the workspace timeline.
  turns: RagTurn[];
  // State updater used to append and update turns.
  setTurns: React.Dispatch<React.SetStateAction<RagTurn[]>>;
  // Current settings passed from parent (reserved for future query payload use).
  settings: RagSettings;
};

/**
 * Hosts the interactive RAG workspace with timeline and chat composer.
 */
export default function RagWorkspace({ turns, setTurns }: Props) {
  const [isSending, setIsSending] = useState(false);

  /**
   * Sends a question to the backend, inserts an optimistic loading turn,
   * and then replaces that turn with success or error data.
   */
  async function handleSend(question: string) {
    setIsSending(true);

    const turnId = makeId();
    const createdAt = new Date().toISOString();

    const optimistic: RagTurn = {
      id: turnId,
      question,
      answer: "...",
      createdAt,
      sources: [],
      status: "loading",
    };

    setTurns((prev) => [...prev, optimistic]);

    try {
      console.log("RAG QUERY:", { question });
      const res = await queryRag({ question });
      console.log("RAG RESPONSE:", res);

      // Normalize backend source fields to frontend RagTurn source shape.
      const sources = (res.sources ?? []).map((s: any, i: number) => ({
        rank: s.rank ?? i + 1,
        score: s.score,
        documentId: s.document_id,
        chunkId: s.chunk_id,
        chunkIndex: typeof s.chunk_index === "number" ? s.chunk_index : null,
        pageId: typeof s.page_id === "number" ? s.page_id : null,
        snippet: s.content,
        isChildChunk: Boolean(s.is_child_chunk),
        parentBlockId: s.parent_block_id ?? null,
        documentUrl: s.document_url ? `http://127.0.0.1:8000${s.document_url}` : undefined,
      }));

      const updated: RagTurn = {
        ...optimistic,
        answer: res.answer,
        sources,
        status: "success",
      };

      // Update only the matching optimistic turn.
      setTurns((prev) => prev.map((t) => (t.id === turnId ? updated : t)));
    } catch (e: any) {
      setTurns((prev) =>
        prev.map((t) =>
          t.id === turnId
            ? { ...t, status: "error", errorMessage: `Error: ${e?.message ?? "Request failed"}`, answer: "" }
            : t
        )
      );
    } finally {
      setIsSending(false);
    }
  }

  // Render page header, conversation timeline, and message composer.
  return (
    <div style={{ maxWidth: 980, margin: "0 auto", display: "flex", flexDirection: "column", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>RAG Workbench</h1>
        <p style={{ margin: "6px 0 0 0", opacity: 0.75 }}>
          Each question creates a new block with answer + retrieved chunks.
        </p>
      </header>

      {turns.length === 0 ? (
        <div style={{ border: "1px dashed rgba(0,0,0,0.25)", borderRadius: 12, padding: 16, opacity: 0.9 }}>
          Ask your first question below.
        </div>
      ) : (
        <ConversationTimeline turns={turns} />
      )}

      <ChatComposer onSend={handleSend} disabled={isSending} />
    </div>
  );
}
