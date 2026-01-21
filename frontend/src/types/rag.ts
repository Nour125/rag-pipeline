export type RagSettings = {
  llmModel: string;
  topK: number;
  chunkSize: number;
  chunkOverlap: number;
  temperature: number;
  maxTokens: number;
};

export type UploadedDocument = {
  documentId: string;
  uploadedAt: string; // ISO string
  pages?: number;
  chunkCount?: number;
  filename: string;      // original oder safe
};

export type RagStats = {
  documentCount: number;
  chunkCount: number;
  lastIndexedAt?: string;
};

export type RagSource = {
  rank: number;
  score: number;

  documentId: string;
  chunkId: string;
  chunkIndex: number | null;
  pageId?: number | null;

  snippet: string;

  isChildChunk?: boolean;
  parentBlockId?: string | null;

  documentUrl?: string;
};

export type RagTurnStatus = "loading" | "success" | "error";

export type RagTurn = {
  id: string; // frontend id
  question: string;
  answer: string;
  createdAt: string;
  sources: RagSource[];
  status: RagTurnStatus;
  errorMessage?: string;
};
