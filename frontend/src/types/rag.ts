/**
 * User-configurable backend/query settings for the RAG pipeline.
 */
export type RagSettings = {
  // Model identifier used by the generation backend.
  llmModel: string;
  // Number of retrieved chunks considered for answer generation.
  topK: number;
  // Target text length for each indexed chunk.
  chunkSize: number;
  // Overlap between adjacent chunks to reduce context loss.
  chunkOverlap: number;
  // Sampling temperature controlling response creativity.
  temperature: number;
  // Maximum token budget for generated answers.
  maxTokens: number;
};

/**
 * Metadata for a document uploaded to the RAG store.
 */
export type UploadedDocument = {
  // Stable backend document identifier.
  documentId: string;
  // Upload timestamp in ISO 8601 format.
  uploadedAt: string;
  // Optional page count when available.
  pages?: number;
  // Optional indexed chunk count for the document.
  chunkCount?: number;
  // Display name of the uploaded file.
  filename: string;
};

/**
 * Aggregated index statistics shown in the dashboard.
 */
export type RagStats = {
  // Total number of documents in the store.
  documentCount: number;
  // Total number of indexed chunks across all documents.
  chunkCount: number;
  // Optional timestamp for the last successful indexing update.
  lastIndexedAt?: string;
};

/**
 * Single retrieved evidence item returned with a generated answer.
 */
export type RagSource = {
  // Rank position in retrieval results (1 = best).
  rank: number;
  // Relevance score produced by retrieval.
  score: number;

  // Backend document identifier.
  documentId: string;
  // Backend chunk identifier.
  chunkId: string;
  // Optional numeric chunk index inside the document.
  chunkIndex: number | null;
  // Optional page reference from the source document.
  pageId?: number | null;

  // Text snippet used as evidence.
  snippet: string;

  // Child/parent chunk metadata for hierarchical retrieval.
  isChildChunk?: boolean;
  parentBlockId?: string | null;

  // Optional direct URL to the source document.
  documentUrl?: string;
};

/**
 * Lifecycle state of one conversation turn.
 */
export type RagTurnStatus = "loading" | "success" | "error";

/**
 * Complete frontend representation of a single Q&A turn.
 */
export type RagTurn = {
  // Client-side unique id for rendering and updates.
  id: string;
  // User prompt text.
  question: string;
  // Generated answer text.
  answer: string;
  // Creation timestamp in ISO 8601 format.
  createdAt: string;
  // Evidence sources associated with the answer.
  sources: RagSource[];
  // Current processing state.
  status: RagTurnStatus;
  // Optional error description when status is "error".
  errorMessage?: string;
};
