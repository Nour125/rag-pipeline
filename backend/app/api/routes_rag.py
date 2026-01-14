from __future__ import annotations
from typing import List
from pathlib import Path
import shutil
import shutil
import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.rag_pipeline import RAGPipeline

router = APIRouter()

# TODO For now: a global store placeholder 
RAG_INSTANCE: RAGPipeline | None = None


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


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
def upload_pdfs(files: List[UploadFile]):
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
    
    results = rag.upload_pdfs(saved_names, raw_dir, language="en", chunk_size=50, overlap=10)

    return {
        "uploaded_files": len(files),
        "saved_to": str(raw_dir),
        "documents": [r.__dict__ for r in results],
        "total_chunks_in_store": len(rag.chunks),
    }