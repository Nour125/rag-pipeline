import { apiClient } from "./client";
import type { RagSettings, RagStats, RagTurn } from "../types/rag";

export type QueryRequest = {
  question: string;
  settings: RagSettings;
};

export type QueryResponse = {
  answer: string;
  sources: RagTurn["sources"];
};


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
  // später: GET /rag/stats
  // return (await apiClient.get("/rag/stats")).data;

  // MVP stub:
  return { documentCount: 0, chunkCount: 0 };
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
