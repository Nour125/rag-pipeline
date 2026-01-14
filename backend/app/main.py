from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_rag import router as rag_router
from pathlib import Path
from app.core.rag_pipeline import RAGPipeline
from app.models.embedder_loader import LMStudioEmbedder
from app.preprocessing.pdf_preprocessor import preprocess_pdf
from app.utils.chunker import TextChunk, chunk_layout_small2big_mod
from app.utils.indexing import FaissVectorStore
from app.api import routes_rag

app = FastAPI(
    title="RAG Pipeline Backend",
    version="0.1.0"
)

# ---- CORS SETTINGS ----
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # welche Frontend-URLs dürfen zugreifen
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, ...
    allow_headers=["*"],          # alle Header erlaubt
)

# ---- ROUTES ----
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])


@app.get("/")
def read_root():
    return {"message": "RAG Pipeline Backend is running"}



@app.on_event("startup")
def init_rag():
    # backend/app/main.py  -> parents[2] = project root
    project_root = Path(__file__).resolve().parents[2]
    print(f"Project root: {project_root}")

    pdf_folder = project_root / "data"
    print(f"PDF folder: {pdf_folder}")

    if not pdf_folder.exists():
        print("⚠️ data/ folder not found -> RAG not initialized")
        return

    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print("⚠️ No PDFs found in data/ -> RAG not initialized")
        return

    embedder = LMStudioEmbedder()

    for pdf_path in pdf_files:
        document_id = pdf_path.stem
        print(f"Processing {document_id}...")

        # 1) preprocess (layout + cleanup + image captions -> merged text)
        page_layouts = preprocess_pdf(pdf_path, language="en")

        # 2) chunk
        doc_chunks = chunk_layout_small2big_mod(
            document_id=document_id,
            layout_pages=page_layouts,
            chunk_size=50,
            overlap=10
        )

    print(f"Total chunks across all PDFs: {len(doc_chunks)}")

    # 4) build FAISS store
    vector_store = FaissVectorStore.from_chunks(doc_chunks, embedder=embedder)

    # 5) create RAG pipeline and register it for the route
    routes_rag.RAG_INSTANCE = RAGPipeline(store=vector_store, top_k=5,chunks=doc_chunks)

    print("✅ RAG initialized from PDFs in data/")
