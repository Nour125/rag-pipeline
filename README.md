

# RAG Pipeline for Medical Technology Literature Support

## 1. Project Overview

This project implements a Retrieval-Augmented Generation (RAG) pipeline 
to support students and researchers in medical technology with:

- Literature search
- Knowledge extraction from scientific PDFs
- Context-aware question answering
- Optional AI-based image description

The system allows users to upload scientific PDFs and query them 
using a Large Language Model enhanced with semantic retrieval.

---

## 2. Motivation

Medical technology students and researchers need to:

- Read large volumes of scientific literature
- Extract relevant information efficiently
- Compare multiple sources
- Understand complex technical explanations

Traditional keyword search is insufficient for semantic understanding.

This system provides:

- Semantic search using embeddings
- Context-aware LLM responses
- Source transparency
- Optional image captioning for figures

---

## 3. System Architecture

### Backend
- Python
- FastAPI
- FAISS (vector search)
- SentenceTransformers (embeddings)
- Optional image captioning model

### Frontend
- React + TypeScript
- Axios for API communication

### LLM
- LM Studio (local LLM inference)

---

## 4. Pipeline Workflow

1. PDF Upload
2. PDF Preprocessing
3. Text Chunking (small-to-big strategy)
4. Embedding Generation
5. Vector Indexing (FAISS)
6. Retrieval of top-k relevant chunks
7. Prompt Construction
8. LLM Answer Generation
9. Source Attribution

---

## 5. Optional Image Processing

If enabled:

- Images extracted from PDFs
- Processed using an AI captioning model
- Captions embedded into vector database
- Used in retrieval pipeline

If disabled:

- Image processing step is skipped
- Faster ingestion

---
## 6. Installation

### Requirements

- Python 3.11 recommended
- Node.js >= 18
- uv (Python package manager)
- LM Studio (for local LLM inference)

---

# Backend Setup

## 1. Navigate to backend

```bash
cd backend
## 2. Create virtual environment

```
uv venv
```

Activate:

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

## 4. Run backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

# Frontend Setup

## 1. Navigate to frontend

```bash
cd frontend
```

## 2. Install dependencies

```bash
npm install
```

## 3. Start development server

```bash
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# LM Studio Setup

1. Start LM Studio
    
2. Load a compatible LLM model
    
3. Start local server
    
4. Default endpoint:
    

```
http://localhost:1234
```

Make sure the backend is configured to use this base URL.

---

# Full System Run Order

1. Start LM Studio
    
2. Start Backend
    
3. Start Frontend
    
4. Open browser at:
    

```
http://localhost:5173
```



---
## 7. API Endpoints

### Upload PDFs

```
POST /rag/upload
```

### Query the system

```
POST /rag/query
```

Request:

```json
{
  "question": "What are the mechanisms of immunotherapy in food allergy?"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [...]
}
```

### Settings

```
POST /rag/settings
```

Allows configuration of:
- top_k
- image_processing toggle
---

## 8. Project Structure

```
rag-pipeline
├─ backend
│  ├─ app
│  │  ├─ api
│  │  │  └─ routes_rag.py
│  │  ├─ core
│  │  │  └─ rag_pipeline.py
│  │  ├─ main.py
│  │  ├─ models
│  │  │  ├─ embedder_loader.py
│  │  │  ├─ image_captioner.py
│  │  │  └─ llm_client.py
│  │  ├─ preprocessing
│  │  │  └─ pdf_preprocessor.py
│  │  └─ utils
│  │     ├─ chunker.py
│  │     └─ indexing.py
│  ├─ requirements.txt
│  ├─ scripts
│  │  ├─ debug_chunking.py
│  │  ├─ debug_image_captioner.py
│  │  ├─ debug_indexing.py
│  │  └─ debug_pdf_preprocessor.py
│  └─ tests
│     ├─ Output.txt
│     ├─ Output2.txt
│     ├─ Output3.txt
│     ├─ Output4.txt
│     ├─ Output4_expanded.txt
│     ├─ Output5.txt
│     └─ Output5_expanded.txt
├─ config
├─ data
│  ├─ foo.pdf
│  ├─ LectureNotes.pdf
│  ├─ Microsoft PowerPoint - V13 Usability Engineering II.pdf
│  ├─ Microsoft PowerPoint - V9 Usability Engineering I.pdf
│  ├─ raw
│  │  ├─ foo_33db0ff4.pdf
│  │  ├─ Wrist-Fractures-What-the-Clinician-Wants-to-Know1_4505f075.pdf
│  │  ├─ Wrist-Fractures-What-the-Clinician-Wants-to-Know1_94fcfddf.pdf
│  │  └─ Wrist-Fractures-What-the-Clinician-Wants-to-Know1_d6a99fe9.pdf
│  └─ test_image.jpg
├─ debug_layout
│  ├─ extracted_text.txt
│  ├─ foo-1.jpg
│  ├─ foo-2.jpg
│  ├─ page_002.png
│  └─ page_003.png
├─ frontend
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  └─ vite.svg
│  ├─ README.md
│  ├─ src
│  │  ├─ api
│  │  │  ├─ client.ts
│  │  │  └─ ragApi.ts
│  │  ├─ App.css
│  │  ├─ App.tsx
│  │  ├─ assets
│  │  │  └─ react.svg
│  │  ├─ components
│  │  │  ├─ cards
│  │  │  │  ├─ GlobalStatsCard.tsx
│  │  │  │  ├─ InitializationCard.tsx
│  │  │  │  ├─ RagTurnCard.tsx
│  │  │  │  └─ UploadCard.tsx
│  │  │  ├─ chat
│  │  │  │  ├─ ChatComposer.tsx
│  │  │  │  └─ ConversationTimeline.tsx
│  │  │  ├─ layout
│  │  │  │  └─ RagLayout.tsx
│  │  │  └─ panels
│  │  │     ├─ RagControlPanel.tsx
│  │  │     └─ RagWorkspace.tsx
│  │  ├─ index.css
│  │  ├─ main.tsx
│  │  ├─ pages
│  │  │  └─ RagWorkbenchPage.tsx
│  │  ├─ types
│  │  │  └─ rag.ts
│  │  └─ utils
│  │     └─ storage.ts
│  ├─ tsconfig.app.json
│  ├─ tsconfig.json
│  ├─ tsconfig.node.json
│  └─ vite.config.ts
├─ LICENSE
└─ README.md

```
---

## 9. Methodological Decisions

### Chunking Strategy

Small-to-big chunking:
- Maintains local coherence
- Improves retrieval precision

### Embedding Model

SentenceTransformers-based embedding model

- Semantic similarity retrieval
- Efficient indexing
### Retrieval Strategy

Top-k similarity search using FAISS
### Prompt Design
Retrieved context is inserted into structured prompt template  
before LLM inference.

---

## 10. Author

Developed as part of an academic project  
in Medical Technology & AI applications.
