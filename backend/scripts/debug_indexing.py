from pathlib import Path

from backend.app.models.embedder_loader import LMStudioEmbedder
from backend.app.utils.indexing import FaissVectorStore
from backend.app.preprocessing.pdf_preprocessor import preprocess_pdf
from backend.app.utils.chunker import chunk_text  # oder deine Wrapper-Funktion


def build_chunks_for_food_allergy_docs() -> list[dict]:
    """
    Beispiel: nimmt alle PDFs im Ordner data/raw/food_allergy_pdfs,
    preprocess't sie und chunkt sie.
    """
    project_root = Path(__file__).resolve().parents[1]
    print(f" Project root: {project_root}")
    pdf_folder = project_root / "data"

    chunks: list[dict] = []
    doc_counter = 0

    for pdf_path in pdf_folder.glob("*.pdf"):
        doc_counter += 1
        document_id = pdf_path.stem
        print(f"Processing {document_id}...")

        preprocessed_text = preprocess_pdf(pdf_path, language="en")

        doc_chunks = chunk_text(
            document_id=document_id,
            text=preprocessed_text,
            chunk_size_words=220,
            chunk_overlap_words=40,
        )

        for i, ch in enumerate(doc_chunks):
            chunks.append(
                {
                    "id": ch.id,
                    "document_id": ch.document_id,
                    "page": None,  # optional
                    "chunk_index": ch.chunk_index,
                    "global_chunk_id": len(chunks),
                    "content": ch.content,
                    "start_char": ch.start_char,
                    "end_char": ch.end_char,
                }
            )

    print(f"Total chunks across all PDFs: {len(chunks)}")
    return chunks


def main() -> None:
    chunks = build_chunks_for_food_allergy_docs()

    embedder = LMStudioEmbedder()
    vector_store = FaissVectorStore.from_chunks(chunks, embedder=embedder)

    # Beispiel-Anfrage
    query_text = "What are typical symptoms of food allergy in children?"
    print(f"\nQuery: {query_text}\n")

    query_embedding = embedder.embed_text(query_text)
    
    results = vector_store.search_by_embedding(query_embedding, top_k=5)

    for i, res in enumerate(results, start=1):
        meta = res["metadata"]
        print(f"#{i}  score={res['score']:.4f}")
        print(f"   doc_id: {meta.get('document_id')}, chunk_index: {meta.get('chunk_index')}")
        print(f"   content snippet: {meta.get('content')[:200]}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
