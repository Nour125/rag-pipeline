import { useState } from "react";
import { apiClient } from "../api/client";

export function ChatBox() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState<string | null>(null);

  async function handleSend() {
    try {
      const res = await apiClient.get("/health");
      setResponse(JSON.stringify(res.data));
    } catch (err) {
      setResponse("Error calling backend");
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <h1>RAG Pipeline UI (Prototype)</h1>
      <input
        style={{ width: "100%", padding: "8px" }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Your question (RAG kommt später)..."
      />
      <button onClick={handleSend} style={{ marginTop: 8, padding: "8px 16px" }}>
        Test Backend
      </button>
      {response && (
        <pre style={{ marginTop: 16, background: "#111", color: "#0f0", padding: 8 }}>
          {response}
        </pre>
      )}
    </div>
  );
}
