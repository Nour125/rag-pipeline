from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from typing import Any, List, Dict

from app.preprocessing.pdf_preprocessor import preprocess_pdf

@dataclass
class TextChunk:
    """
    Represents a single chunk of text from a document.
    """
    id: str
    document_id: str
    chunk_index: int
    content: str
    start_char: int
    end_char: int


def _normalize_text(text: str) -> str:
    """
    Basic normalization:
    - unify newlines
    - strip leading/trailing whitespace
    """
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _split_text_into_words(text: str) -> List[str]:
    """
    Split text into words. This is a simple split on whitespace.
    For our use case (RAG), this is sufficient.
    """
    return text.split()


def extract_text_from_pdf(pdf_path: Path) -> List[Dict]:
    """
    Extracts text per page from a PDF.

    Returns a list of dicts:
    [
      {"page": 1, "text": "..."},
      {"page": 2, "text": "..."},
      ...
    ]
    """
    reader = PdfReader(str(pdf_path))
    pages = []

    for i, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        # Clean up a bit
        cleaned = " ".join(raw_text.split())
        pages.append({"page": i + 1, "text": cleaned})

    return pages

def chunk_text(
    document_id: str,
    text: str,
    chunk_size_words: int = 220,
    chunk_overlap_words: int = 40,
) -> List[TextChunk]:
    """
    Splits the given text into overlapping chunks.

    Args:
        document_id: Identifier for the source document (e.g., filename without suffix).
        text: The full text of the document.
        chunk_size_words: Target size of each chunk in words.
        chunk_overlap_words: How many words overlap between consecutive chunks.

    Returns:
        List of TextChunk objects.
    """
    text = _normalize_text(text)

    if not text:
        return []

    words = _split_text_into_words(text)
    if not words:
        return []

    chunks: List[TextChunk] = []
    start_word_idx = 0
    chunk_index = 0

    # Reconstruct char offsets later
    # We keep a list of (word, start_char, end_char)
    word_offsets = []
    current_pos = 0
    for w in words:
        # Skip leading spaces until first word
        while current_pos < len(text) and text[current_pos].isspace():
            current_pos += 1
        start = text.find(w, current_pos)
        if start == -1:
            # Fallback: we just set to current_pos, not ideal but robust
            start = current_pos
        end = start + len(w)
        word_offsets.append((w, start, end))
        current_pos = end

    total_words = len(words)

    while start_word_idx < total_words:
        end_word_idx = min(start_word_idx + chunk_size_words, total_words)

        # Build chunk content
        chunk_words = [w for (w, _, _) in word_offsets[start_word_idx:end_word_idx]]
        chunk_text_str = " ".join(chunk_words).strip()

        if not chunk_text_str:
            break

        # Determine character offsets for this chunk
        start_char = word_offsets[start_word_idx][1]
        end_char = word_offsets[end_word_idx - 1][2]

        chunk_id = f"{document_id}-{chunk_index}"

        chunks.append(
            TextChunk(
                id=chunk_id,
                document_id=document_id,
                chunk_index=chunk_index,
                content=chunk_text_str,
                start_char=start_char,
                end_char=end_char,
            )
        )

        chunk_index += 1

        # Move window forward with overlap
        if end_word_idx == total_words:
            break

        start_word_idx = max(0, end_word_idx - chunk_overlap_words)

    return chunks

'''
def chunk_pdf_document(
    document_id: str,
    pdf_path: Path,
    chunk_size_words: int = 220,
    chunk_overlap_words: int = 40,
) -> List[Dict[str, Any]]:
    """
    High-level function:
    - extracts text per page
    - splits each page into chunks
    - adds metadata (doc_id, page, chunk_id, etc.)
    """
    pages = extract_text_from_pdf(pdf_path)

    all_chunks: List[Dict[str, Any]] = []
    chunk_counter = 0

    for page in pages:
        page_num = page["page"]
        page_text = page["text"]

        page_chunks = chunk_text(
            document_id=document_id,
            text=page_text,
            chunk_size_words=chunk_size_words,
            chunk_overlap_words=chunk_overlap_words,
        )

        for chunk in page_chunks:
            chunk_counter += 1
            all_chunks.append(
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "page": page_num,
                    "chunk_index": chunk.chunk_index,
                    "global_chunk_id": chunk_counter,
                    "content": chunk.content,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                }
            )

    return all_chunks

'''

def chunk_pdf_document_with_preprocessing(
    document_id: str,
    pdf_path: Path,
    chunk_size_words: int = 220,
    chunk_overlap_words: int = 40,
) -> List[Dict]:
    """
    Kombiniert Preprocessing (Layout + Bildcaptions) mit deinem bestehenden Chunking.
    """
    preprocessed_text = preprocess_pdf(pdf_path, language="en")

    chunks = chunk_text(
        document_id=document_id,
        text=preprocessed_text,
        chunk_size_words=chunk_size_words,
        chunk_overlap_words=chunk_overlap_words,
    )

    result: List[Dict] = []
    for i, chunk in enumerate(chunks):
        result.append(
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "page": None,  # optional, könntest du später aus [PAGE x] Tags ableiten
                "chunk_index": chunk.chunk_index,
                "global_chunk_id": i,
                "content": chunk.content,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }
        )
    return result


def chunk_all_pdfs_in_folder(
    folder: Path,
    chunk_size_words: int = 220,
    chunk_overlap_words: int = 40,
) -> List[Dict[str, Any]]:
    """
    Processes all PDFs in a folder and returns a big list of chunks.
    """
    all_chunks: List[Dict[str, Any]] = []

    for pdf_path in folder.glob("*.pdf"):
        document_id = pdf_path.stem  # z.B. "food_allergy_guide"
        print(f"Processing PDF: {pdf_path.name}")
        doc_chunks = chunk_pdf_document_with_preprocessing(
            document_id=document_id,
            pdf_path=pdf_path,
            chunk_size_words=chunk_size_words,
            chunk_overlap_words=chunk_overlap_words,
        )
        all_chunks.extend(doc_chunks)

    return all_chunks
