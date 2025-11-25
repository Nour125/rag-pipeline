from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router

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


@app.get("/")
def read_root():
    return {"message": "RAG Pipeline Backend is running"}
