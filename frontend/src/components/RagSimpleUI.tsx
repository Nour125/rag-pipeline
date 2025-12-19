import { useState } from "react" 
import { apiClient } from "../api/client" 

export type RAGSource = {
  score: number 
  document_id: string 
  chunk_index: number 
  content?: string  // you include it in the response, so keep it optional just in case
} 

export type RAGResponse = {
  answer: string 
  sources: RAGSource[] 
} 


export function RagSimpleUI() {
  const [question, setQuestion] = useState("") 
  const [topK, setTopK] = useState<number>(5) 

  const [loading, setLoading] = useState(false) 
  const [error, setError] = useState<string | null>(null) 

  const [result, setResult] = useState<RAGResponse | null>(null) 

  async function handleAsk() {
    setLoading(true) 
    setError(null) 
    setResult(null) 

    try {
      const res = await apiClient.post<RAGResponse>("/rag/query", {
        question,
        top_k: topK,
      }) 
      setResult(res.data) 
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ??
          e?.message ??
          "Request failed"
      ) 
    } finally {
      setLoading(false) 
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "24px auto", padding: 16 }}>
      <h1 style={{ marginBottom: 8 }}>RAG DEMO</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Ask a question → see answer + retrieved chunks.
      </p>

      {/* 1) input + top_k */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 120px 120px",
          gap: 30,
          alignItems: "center",
          marginTop: 16,
        }}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #444",
            background: "transparent",
            color: "inherit",
          }}
        />

        <input
          type="number"
          min={1}
          max={20}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          title="top_k"
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #444",
            background: "transparent",
            color: "inherit",
          }}
        />

        <button
          onClick={handleAsk}
          disabled={loading || question.trim().length === 0}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #444",
            background: loading ? "#222" : "#111",
            color: "inherit",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>

      {error && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            borderRadius: 8,
            border: "1px solid #a33",
          }}
        >
          <b>Error:</b> {error}
        </div>
      )}

      {/* 2) answer */}
      {result && (
        <div
          style={{
            marginTop: 20,
            padding: 14,
            borderRadius: 10,
            border: "1px solid #444",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Answer</h2>
          <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.4 }}>
            {result.answer}
          </div>
        </div>
      )}

      {/* 3) retrieved chunks */}
      {result && (
        <div style={{ marginTop: 18 }}>
          <h2 style={{ marginBottom: 10 }}>
            Retrieved Chunks ({result.sources?.length ?? 0})
          </h2>

          {(result.sources ?? []).map((s, idx) => (
            <details
              key={`${s.document_id}-${s.chunk_index}-${idx}`}
              style={{
                border: "1px solid #444",
                borderRadius: 10,
                padding: 12,
                marginBottom: 10,
              }}
              open={idx < 2} // open first 2 by default
            >
              <summary style={{ cursor: "pointer" }}>
                <b>#{idx + 1}</b> — score={s.score.toFixed(4)} —{" "}
                {s.document_id} — chunk {s.chunk_index}
              </summary>

              <div style={{ marginTop: 10, opacity: 0.9 }}>
                <div style={{ fontSize: 13, opacity: 0.8, marginBottom: 6 }}>
                  document_id: <code>{s.document_id}</code> · chunk_index:{" "}
                  <code>{s.chunk_index}</code>
                </div>

                <pre
                  style={{
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    margin: 0,
                    padding: 10,
                    borderRadius: 8,
                    border: "1px solid #333",
                    background: "#0b0b0b",
                  }}
                >
                  {s.content ?? "(no content in response)"}
                </pre>
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
