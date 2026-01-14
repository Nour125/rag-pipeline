from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import numpy as np
import faiss

from app.models.embedder_loader import LMStudioEmbedder
from app.utils.chunker import TextChunk


def _l2_normalize(x: np.ndarray) -> np.ndarray:
    """
    L2-normalize vectors along axis 1.
    """
    if x.ndim == 1:
        x = x[None, :]
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    return x / norms


@dataclass
class FaissVectorStore:
    """
    FAISS-basierter Vektorspeicher:
    - index: FAISS IndexFlatIP (inner product)
    - dim: Vektordimension
    - metadata: Liste mit Metadaten (1:1 zu Index-Zeilen)
    """
    index: faiss.IndexFlatIP
    dim: int
    metadata: List[Dict[str, Any]]

    @classmethod
    def from_chunks(
        cls,
        chunks: List[TextChunk],
        embedder: Optional[LMStudioEmbedder] = None,
    ) -> "FaissVectorStore":
        """
        Baut einen FAISS-Index aus einer Liste von TextChunk-Objekten.
        """
        if embedder is None:
            embedder = LMStudioEmbedder()

        if not chunks:
            raise ValueError("Cannot build FAISS index from empty chunk list")

        texts = [c.content for c in chunks]
        embeddings = embedder.embed_texts(texts)  # shape (n, dim)

        if embeddings.ndim != 2:  # TODO vllt problematisch
            raise ValueError("Embeddings must be a 2D array")

        # Cosine-Similarity über normalisierte Vektoren + inner product
        embeddings = _l2_normalize(embeddings).astype("float32")

        n, dim = embeddings.shape
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        metadata: List[Dict[str, Any]] = []
        for c in chunks:
            meta = {
                "id": c.id,
                "document_id": c.document_id,
                "page_id": c.page_id,
                "parent_block_id": c.parent_block_id,
                "chunk_index": c.chunk_index,
                "content": c.content,
                "splited": c.splited,
                "wordcount": c.wordcount
            }
            metadata.append(meta)

        return cls(index=index, dim=dim, metadata=metadata)

    def search_by_embedding(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suche über vorgegebenen Query-Embedding-Vektor.
        """
        if self.index.ntotal == 0:
            return []

        q = _l2_normalize(query_embedding.astype("float32"))
        if q.ndim == 1:
            q = q[None, :]

        D, I = self.index.search(q, top_k)  # D: scores, I: indices

        results: List[Dict[str, Any]] = []
        scores = D[0]
        indices = I[0]

        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append(
                {
                    "score": float(score),
                    "metadata": meta,
                }
            )

        return results

    def search_by_text(
        self,
        query_text: str,
        embedder: Optional[LMStudioEmbedder] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Convenience: Text → Embedding → Suche.
        """
        if embedder is None:
            embedder = LMStudioEmbedder()

        query_emb = embedder.embed_text(query_text)
        return self.search_by_embedding(query_emb, top_k=top_k)
    
    def clear(self) -> None:
        """
        Removes all vectors from the index and clears metadata.
        """
        self.index.reset()      # FAISS: Index leeren
        self.metadata = []      # Metadaten-Liste leeren
