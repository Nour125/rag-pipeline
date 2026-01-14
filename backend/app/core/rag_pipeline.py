from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from app.models.embedder_loader import LMStudioEmbedder
from app.models.llm_client import LMStudioChatLLM
from app.utils.chunker import TextChunk,expand_chunk_small2big_mod
from app.utils.indexing import FaissVectorStore

@dataclass
class RAGConfig:
    top_k: int = 7


class RAGPipeline:
    def __init__(self, store: FaissVectorStore, chunks: List[TextChunk], top_k: int = 5) -> None:
        self.embedder = LMStudioEmbedder()
        self.llm = LMStudioChatLLM()
        self.store = store
        self.top_k = top_k
        self.chunks = chunks

    def answer(self, question: str) -> Dict[str, Any]:
        # 1) retrieve
        hits = self.store.search_by_text(question, embedder=self.embedder, top_k=self.top_k)

        # 2) build context
        context_blocks: List[str] = []
        sources: List[Dict[str, Any]] = []
        for h in hits:
            meta = h["metadata"]
            score = h["score"]
            hited_text_chunk = TextChunk(
                    id=meta.get("id"),
                    document_id=meta.get("document_id"),
                    page_id=meta.get("page_id"),
                    parent_block_id=meta.get("parent_block_id"),
                    chunk_index=meta.get("chunk_index"),
                    content=meta.get("content"),
                    splited=meta.get("splited"), 
                    wordcount=meta.get("wordcount")
                )
            expanded_content_chunks = expand_chunk_small2big_mod(hit=hited_text_chunk,chunks=self.chunks)

            for content_chunk in expanded_content_chunks:
                context_blocks.append(
                    f"[Source score={score:.3f} doc={content_chunk.document_id} chunk_id={content_chunk.id}]\n"
                    f"{content_chunk.content}"
                )
            sources.append(
                {
                    "score": score,
                    "document_id": meta.get("document_id"),
                    "chunk_id": meta.get("id"),
                    "content": meta.get("content"), 
                }
            )

        context_text = "\n\n---\n\n".join(context_blocks)

        # 3) prompt
        system = (
            "You are a helpful assistant. "
            "Answer using ONLY the provided context. "
            "You may explain scientific or medical information in a descriptive, factual manner "
            "as stated in the context, but do NOT give personal advice, instructions, or recommendations. "
            "If the question is irrelevant, violent, or unrelated to the context, respond exactly with: "
            "\"I can't answer this type of question.\" "
            "Cite sources by referring to the chunk_id."
        )




        user = f"""
                QUESTION:
                {question}
                CONTEXT:
                {context_text}
                """

        # 4) call LLM
        answer_text = self.llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        )

        return {"answer": answer_text, "sources": sources}
