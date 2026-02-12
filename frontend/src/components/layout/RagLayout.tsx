import type React from "react";

type RagLayoutProps = {
  // Content rendered in the left sidebar panel.
  left: React.ReactNode;
  // Content rendered in the main workspace panel.
  right: React.ReactNode;
};

/**
 * Provides a two-column app layout with a fixed left sidebar and flexible right workspace.
 */
export default function RagLayout({ left, right }: RagLayoutProps) {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Left panel */}
      <aside
        style={{
          width: "30%",
          borderRight: "2px solid rgba(0,0,0,0.1)",
          padding: 16,
          overflowY: "auto",
        }}
      >
        {left}
      </aside>

      {/* Right workspace */}
      <main
        style={{
          flex: 1,
          padding: 16,
          overflowY: "auto",
        }}
      >
        {right}
      </main>
    </div>
  );
}
