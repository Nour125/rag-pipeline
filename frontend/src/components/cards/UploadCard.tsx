import { useEffect, useMemo, useState } from "react";
import type { RagStats, UploadedDocument } from "../../types/rag";
import { mapUploadDocuments, uploadPdfs } from "../../api/ragApi";
import { saveJson } from "../../utils/storage";

const UPLOADS_KEY = "rag_uploads_v1";

type Props = {
  uploads: UploadedDocument[];
  setUploads: (next: UploadedDocument[]) => void;
  stats: RagStats;
  setStats: (next: RagStats) => void;
};

/**
 * Handles PDF upload flow, optional image processing, and local upload list rendering.
 */
export default function UploadCard({ uploads, setUploads, stats, setStats }: Props) {
  const [processImages, setProcessImages] = useState(false);
  const [selected, setSelected] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // User-friendly label for the current file selection state.
  const selectedLabel = useMemo(() => {
    if (selected.length === 0) return "No files selected";
    if (selected.length === 1) return selected[0].name;
    return `${selected.length} files selected`;
  }, [selected]);

  /**
   * Uploads selected PDFs to the backend, appends returned documents,
   * and refreshes aggregate stats shown in the dashboard.
   */
  async function handleUpload() {
    if (selected.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const res = await uploadPdfs(selected, processImages);
      const newDocs = mapUploadDocuments(res.documents);

      // Append new uploads while preserving the current list.
      const nextUploads = [...uploads, ...newDocs];
      setUploads(nextUploads);

      // Sync global stats after successful upload.
      setStats({
        ...stats,
        documentCount: nextUploads.length,
        chunkCount: res.total_chunks_in_store,
        lastIndexedAt: new Date().toISOString(),
      });

      // Clear file input state after success.
      setSelected([]);
    } catch (e: any) {
      setError(e?.message ?? "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  // If all documents are cleared globally, reset local upload cache as well.
  useEffect(() => {
    if (stats.documentCount === 0) {
      setUploads([]);
      saveJson(UPLOADS_KEY, []);
    }
  }, [stats, setUploads]);

  // Render upload controls, status, and uploaded document history.
  return (
    <section
      style={{
        border: "1px solid rgba(0,0,0,0.1)",
        borderRadius: 12,
        padding: 12,
      }}
    >
      <h3 style={{ marginTop: 0 }}>Upload PDFs</h3>

      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(e) => setSelected(Array.from(e.target.files ?? []))}
      />

      <div style={{ marginTop: 8, fontSize: 12, opacity: 0.75 }}>{selectedLabel}</div>
      <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <input
          type="checkbox"
          checked={processImages}
          onChange={(e) => setProcessImages(e.target.checked)}
        />
        <span style={{ fontSize: 13 }}>
          Image processing (slow) - generate AI descriptions for PDF images
        </span>
      </label>

      <button
        style={{
          width: "100%",
          marginTop: 10,
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid rgba(0,0,0,0.15)",
          cursor: selected.length > 0 && !isUploading ? "pointer" : "not-allowed",
          opacity: selected.length > 0 && !isUploading ? 1 : 0.6,
          fontWeight: 600,
        }}
        disabled={selected.length === 0 || isUploading}
        onClick={handleUpload}
      >
        {isUploading ? "Uploading..." : "Upload"}
      </button>

      {error && (
        <div style={{ marginTop: 10, fontSize: 13 }}>
          <b style={{ color: "crimson" }}>Error:</b> {error}
        </div>
      )}

      {/* Uploaded docs list */}
      <div style={{ marginTop: 12 }}>
        <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 6 }}>Uploaded documents</div>

        {uploads.length === 0 ? (
          <div style={{ fontSize: 13, opacity: 0.75 }}>No documents uploaded yet.</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {uploads
              .slice()
              .reverse()
              .map((d) => (
                <div
                  key={`${d.documentId}-${d.uploadedAt}`}
                  style={{
                    border: "1px solid rgba(0,0,0,0.08)",
                    borderRadius: 10,
                    padding: 10,
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{d.filename}</div>
                  <div style={{ fontSize: 12, opacity: 0.75 }}>id: {d.documentId}</div>
                  <div style={{ fontSize: 12, opacity: 0.75 }}>
                    uploaded: {new Date(d.uploadedAt).toLocaleString()}
                    {typeof d.pages === "number" ? ` - pages: ${d.pages}` : ""}
                    {typeof d.chunkCount === "number" ? ` - chunks: ${d.chunkCount}` : ""}
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </section>
  );
}
