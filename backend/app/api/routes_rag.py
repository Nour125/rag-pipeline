from __future__ import annotations
from typing import List
from pathlib import Path
import shutil
import shutil
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.rag_pipeline import RAGPipeline

router = APIRouter()

# TODO For now: a global store placeholder 
RAG_INSTANCE: RAGPipeline | None = None


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None

class RagSettingsIn(BaseModel):
    llm_model: str = Field(default="lmstudio-default")
    top_k: int = Field(default=5, ge=1, le=50)

    chunk_size: int = Field(default=500, ge=50, le=5000)
    chunk_overlap: int = Field(default=80, ge=0, le=1000)

    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=800, ge=16, le=4096)


def _require_rag() -> RAGPipeline:
    if RAG_INSTANCE is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized yet.")
    return RAG_INSTANCE

@router.post("/query")
def rag_query(req: QueryRequest):
    rag = _require_rag()
    if req.top_k is not None:
        rag.top_k = req.top_k

    return rag.answer(req.question)


@router.post("/upload")
def upload_pdfs(files: List[UploadFile]= File(...),process_images: bool = Form(True)):
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