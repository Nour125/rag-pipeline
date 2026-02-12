from __future__ import annotations
from typing import Any, List, Optional, Dict
from pathlib import Path
import shutil
import shutil
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

from app.core.rag_pipeline import RAGPipeline

router = APIRouter()
RAG_INSTANCE: RAGPipeline | None = None


class QueryRequest(BaseModel):
    """
    The request body for a RAG query.
    """
    question: str
    # settings: Optional[Dict[str, Any]] = None

class RagSettingsIn(BaseModel):
    """
    The request body for updating RAG settings.
    """
    llm_model: str = Field(default="qwen/qwen3-vl-4b")
    top_k: int = Field(default=5, ge=1, le=50)
    chunk_size: int = Field(default=100, ge=50, le=5000)
    chunk_overlap: int = Field(default=20, ge=0, le=1000)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=16, le=10000)


def _require_rag() -> RAGPipeline:
    """
    Helper to get the RAG instance or raise an error if it's not ready.
    """
    if RAG_INSTANCE is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized yet.")
    return RAG_INSTANCE

@router.post("/query")
def rag_query(req: QueryRequest):
    """
    Endpoint to handle RAG queries. Expects a JSON body with a "question" field.
    """
    rag = _require_rag()
    return rag.answer(req.question)

@router.get("/documents/{document_id}")
def get_document(document_id: str):
    """
    Endpoint to retrieve a document by its ID.
    
    :param document_id: The ID of the document to retrieve.
    :type document_id: str
    """
    # repo root
    project_root = Path(__file__).resolve().parents[3]
    raw_dir = project_root / "data" / "raw"

    # Your upload uses safe_name as filename; document_id should match that.
    file_path = raw_dir / document_id

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=document_id,
    )


@router.post("/upload")
def upload_pdfs(files: List[UploadFile]= File(...),process_images: bool = Form(True)):
    """
    Endpoint to upload one or more PDF files. Expects multipart/form-data with file uploads.
    
    :param files: A list of PDF files to upload.
    :type files: List[UploadFile]
    :param process_images: Whether to process images within the PDFs.
    :type process_images: bool
    """
    rag = _require_rag()

    # project root: backend/app/api/routes_rag.py -> parents[3] = repo root
    project_root = Path(__file__).resolve().parents[3]
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    saved_names: List[str] = []

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Not a PDF: {f.filename}")
        

        # stable + unique file name (avoid collisions)
        safe_name = f"{Path(f.filename).stem}_{uuid.uuid4().hex[:8]}.pdf"
        saved_names.append(safe_name)
        out_path = raw_dir / safe_name
        with out_path.open("wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
    
    results = rag.upload_pdfs(saved_names, raw_dir, process_images=process_images)

    return {
        "uploaded_files": len(files),
        "saved_to": str(raw_dir),
        "documents": [r.__dict__ for r in results],
        "total_chunks_in_store": len(rag.chunks),
    }

@router.post("/settings")
def set_settings(payload: RagSettingsIn):
    """
    Endpoint to update RAG settings. Expects a JSON body with the new settings.
    
    :param payload: The new RAG settings to apply.
    :type payload: RagSettingsIn
    """
    rag = _require_rag()
    
    rag.apply_settings(
        llm_model=payload.llm_model,
        top_k=payload.top_k,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )

    return {"ok": True, "settings": rag.get_settings()}

@router.get("/stats")
def get_stats():
    """
    Endpoint to retrieve document and chunk counts.
    """
    rag = _require_rag()
    # documents count: simplest MVP = number of unique document_ids in chunks
    # If you already track documents somewhere else, use that instead.
    doc_ids = {c.document_id for c in rag.chunks} if rag.chunks else set()

    return {
        "documentCount": len(doc_ids),
        "chunkCount": len(rag.chunks),
        "settings": rag.get_settings() if hasattr(rag, "get_settings") else None,
    }