from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
from zipfile import Path

from app.models.embedder_loader import LMStudioEmbedder
from app.models.llm_client import LLMConfig, LMStudioChatLLM
from app.preprocessing.pdf_preprocessor import preprocess_pdf
from app.utils.chunker import TextChunk, chunk_layout_small2big_mod,expand_chunk_small2big_mod
from app.utils.indexing import FaissVectorStore

@dataclass
class RAGConfig:
    top_k: int = 7

@dataclass
class UploadResult:
    document_id: str
    filename: str
    num_pages: int
    num_chunks: int


class RAGPipeline:
    """
    A simple RAG pipeline that handles PDF uploads, indexing, and question-answering.
    """
    def __init__(self, store: FaissVectorStore, chunks: List[TextChunk], top_k: int = 5) -> None:
        self.embedder = LMStudioEmbedder()
        self.llm = LMStudioChatLLM()
        self.store = store
        self.top_k = top_k
        self.chunks = chunks

        self.chunk_size = 100
        self.chunk_overlap = 20

        self.temperature = 0.2
        self.max_tokens = 2048
    
    def apply_settings(
        self,
        llm_model: str,
        top_k: int,
        chunk_size: int,
        chunk_overlap: int,
        temperature: float,
        max_tokens: int,
    ):
        """
        Apply new settings to the RAG pipeline. This can be extended to trigger re-indexing if needed.
        """
        # Store settings (MVP: only store, no re-indexing here)
        llmCnfig = LLMConfig(model=llm_model, temperature=temperature, max_tokens=max_tokens)

        self.llm = LMStudioChatLLM(config=llmCnfig)
        self.top_k = top_k

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_settings(self) -> dict:
        """
        Retrieve current settings of the RAG pipeline.
        """
        return {
            "llm_model": self.llm.getName(),
            "top_k": self.top_k,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def answer(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.

        
        :param self: The RAGPipeline instance.
        :param question: The question to answer.
        :type question: str
        :return: Description
        :rtype: Dict[str, Any]
        """
        # 1) retrieve
        hits = self.store.search_by_text(question, embedder=self.embedder, top_k=self.top_k)

        # 2) build context
        context_blocks: List[str] = []
        contextDict: Dict[int, str] = {}
        sources: List[Dict[str, Any]] = []
        print("HITS:", len(hits))
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
            # expand chunk to include siblings if it's a small chunk (MVP: simple heuristic based on word count)
            expanded_content_chunks = expand_chunk_small2big_mod(hit=hited_text_chunk,chunks=self.chunks)

            for content_chunk in expanded_content_chunks:
                context_blocks.append(
                    f"[Source score={score:.3f} doc={content_chunk.document_id} chunk_id={content_chunk.chunk_index}]\n"
                    f"{content_chunk.content}"
                )
            contextDict[content_chunk.parent_block_id] = "\n\n---\n\n".join(context_blocks)
            context_blocks = []  # reset for next hit
            # build sources info for frontend (MVP: just return chunk metadata, frontend can fetch full content if needed)
            sources.append(
                {
                    "rank": len(sources) + 1,
                    "score": score,
                    "document_id": meta.get("document_id"),
                    "chunk_id": meta.get("id"),
                    "chunk_index": meta.get("chunk_index"),
                    "page_id": meta.get("page_id"),
                    "content": meta.get("content"),

                    # highlight info
                    "is_child_chunk": bool(meta.get("splited")),  # your field name
                    "parent_block_id": meta.get("parent_block_id"),

                    # link (frontend will use it directly)
                    "document_url": f"/rag/documents/{meta.get('document_id')}",
                }
            )

        # build context text for LLM
        context_text = "\n\n---\n\n".join(contextDict.values())


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

        # 4) user prompt
        user = f"""
                QUESTION:
                {question}
                CONTEXT:
                {context_text}
                """

        # 5) call LLM
        answer_text = self.llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        )

        return {"answer": answer_text, "sources": sources}

    def upload_pdfs(
        self,
        pdf_names: List[str],
        data_folder: Path,
        process_images: bool = True,
    ) -> List[UploadResult]:
        """
        Process and upload PDFs to the RAG pipeline. This includes preprocessing, chunking, and indexing.
        """
        results: List[UploadResult] = []
        all_new_chunks: List[TextChunk] = []

        # For each PDF, preprocess and chunk, then add to store and keep track of results for response
        for pdf_name in pdf_names:
            document_id = pdf_name
            pdf_path = data_folder / pdf_name
            page_layouts = preprocess_pdf(pdf_path, language="en", process_images=process_images)
            doc_chunks = chunk_layout_small2big_mod(
                document_id=document_id,
                layout_pages=page_layouts,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
            all_new_chunks.extend(doc_chunks)

            # prepare result info for this document
            results.append(
                UploadResult(
                    document_id=document_id,
                    filename=pdf_name,
                    num_pages=len(page_layouts),
                    num_chunks=len(doc_chunks),
                )
            )
        # If we have new chunks, add them to the store and the pipeline's chunk list
        if all_new_chunks:
            # update store
            self.store.add_chunks(all_new_chunks)
            # keep for sources/debug
            self.chunks.extend(all_new_chunks)

        return results