import { apiClient } from "./client";
import type { RagSettings, RagStats, RagTurn } from "../types/rag";
import type { UploadedDocument } from "../types/rag";

export type QueryRequest = {
  question: string;
  settings: RagSettings;
};

export type QueryResponse = {
  answer: string;
  sources: RagTurn["sources"];
};

export type UploadResponse = {
  uploaded_files: number;
  saved_to: string;
  documents: any[]; // backend dicts (we map)
  total_chunks_in_store: number;
};

export async function uploadPdfs(files: File[], processImages: boolean): Promise<UploadResponse> {
  const formData = new FormData();
  // IMPORTANT: field name must match your backend param: "files"
  for (const f of files) {
    formData.append("files", f);
  }
  formData.append("process_images", processImages ? "true" : "false");

  const res = await apiClient.post("/rag/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data as UploadResponse;
}

export function mapUploadDocuments(rawDocs: any[]): UploadedDocument[] {
  const now = new Date().toISOString();

  return rawDocs.map((d, idx) => {
    // try common keys (robust)
    const filename =
      d.filename ?? d.file_name ?? d.safe_name ?? d.document_id ?? `document_${idx}`;

    const documentId =
      d.document_id ?? d.id ?? d.safe_name ?? filename;

    return {
      documentId: String(documentId),
      filename: String(filename),
      uploadedAt: now,
      pages: typeof d.pages === "number" ? d.pages : undefined,
      chunkCount: typeof d.chunk_count === "number" ? d.chunk_count : undefined,
    };
  });
}


export async function setBackendSettings(settings: RagSettings): Promise<RagSettings> {
  const payload = {
    llm_model: settings.llmModel,
    top_k: settings.topK,
    chunk_size: settings.chunkSize,
    chunk_overlap: settings.chunkOverlap,
    temperature: settings.temperature,
    max_tokens: settings.maxTokens,
  };

  const res = await apiClient.post("/rag/settings", payload);

  if (!res.data?.ok) {
    throw new Error(res.data?.error ?? "Failed to apply settings");
  }

  const s = res.data.settings;
  // Map back to frontend type
  return {
    llmModel: s.llm_model,
    topK: s.top_k,
    chunkSize: s.chunk_size,
    chunkOverlap: s.chunk_overlap,
    temperature: s.temperature,
    maxTokens: s.max_tokens,
  };
}




export async function fetchStats(): Promise<RagStats> {
  const res = await apiClient.get("/rag/stats");
  const data = res.data;

  return {
    documentCount: data.documentCount ?? 0,
    chunkCount: data.chunkCount ?? 0,
    lastIndexedAt: data.lastIndexedAt, // optional if you add later
  };
}


export async function queryRag(_payload: QueryRequest): Promise<QueryResponse> {
  // später: POST /rag/query
  // return (await apiClient.post("/rag/query", payload)).data;

  // MVP stub:
  return {
    answer: "Backend not connected yet (stub).",
    sources: [],
  };
}
