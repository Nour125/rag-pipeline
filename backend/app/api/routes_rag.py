from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.rag_pipeline import RAGPipeline

router = APIRouter()

# TODO For now: a global store placeholder (you'll load/build it at startup)
RAG_INSTANCE: RAGPipeline | None = None


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


@router.post("/query")
def rag_query(req: QueryRequest):
    global RAG_INSTANCE
    if RAG_INSTANCE is None:
        raise HTTPException(status_code=503, detail="RAG store not initialized")

    if req.top_k is not None:
        RAG_INSTANCE.top_k = req.top_k

    return RAG_INSTANCE.answer(req.question)
