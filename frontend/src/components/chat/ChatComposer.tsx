import { useState } from "react";

type Props = {
  onSend: (question: string) => Promise<void> | void;
  disabled?: boolean;
};

export default function ChatComposer({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  async function send() {
    const q = text.trim();
    if (!q || disabled) return;
    setText("");
    await onSend(q);
  }

  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        position: "sticky",
        bottom: -15,
        background: "rgba(255,255,255,0.9)",
        backdropFilter: "blur(6px)",
        padding: 12,
        border: "1px solid rgba(0,0,0,0.08)",
        borderRadius: 12,
      }}
    >
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask a question…"
        style={{
          flex: 1,
          padding: 10,
          borderRadius: 10,
          border: "1px solid rgba(0,0,0,0.15)",
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            send();
          }
        }}
        disabled={disabled}
      />
      <button
        onClick={send}
        disabled={disabled || text.trim().length === 0}
        style={{
          padding: "10px 14px",
          borderRadius: 10,
          border: "1px solid rgba(0,0,0,0.15)",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.6 : 1,
          fontWeight: 700,
        }}
      >
        Send
      </button>
    </div>
  );
}
