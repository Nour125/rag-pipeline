import faiss
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from app.api.routes_rag import router as rag_router
from pathlib import Path
from app.core.rag_pipeline import RAGPipeline
from app.models.embedder_loader import LMStudioEmbedder
from app.utils.indexing import FaissVectorStore
from app.api import routes_rag

# FastAPI-Instanz erstellen
app = FastAPI(
    title="RAG Pipeline Backend",
    version="0.1.0"
)

# CORS-Middleware hinzufügen, damit das Frontend (z.B. Vite) auf die API zugreifen kann
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

# API-Router für RAG-Funktionalitäten einbinden
app.include_router(rag_router, prefix="/rag", tags=["rag"])

# Einfacher Root-Endpunkt zur Überprüfung, ob die API läuft
@app.get("/")
def read_root():
    return {"message": "RAG Pipeline Backend is running"}

# Beim Start der API: RAG-Pipeline mit leerem FAISS-Index initialisieren
@app.on_event("startup")
def init_rag():
    embedder = LMStudioEmbedder()
    # 1) probe embedding dim
    probe = embedder.embed_text("dim_probe")
    probe = np.asarray(probe, dtype="float32").reshape(1, -1)
    dim = probe.shape[1]

    # 2) create EMPTY FAISS index
    index = faiss.IndexFlatIP(dim)

    # 3) create EMPTY store
    vector_store = FaissVectorStore(index=index, metadata=[], embedder=embedder)

    # 4) register pipeline
    routes_rag.RAG_INSTANCE = RAGPipeline(store=vector_store, top_k=5, chunks=[])

    print(f"✅ RAG initialized (empty). FAISS dim={dim}. Use /rag/upload to add PDFs.")
