from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from typing import Any, List, Dict

from app.preprocessing.pdf_preprocessor import PageLayout, preprocess_pdf

@dataclass
class TextChunk:
    id: str
    document_id: str
    page_id: int
    parent_block_id: int 
    chunk_index: int
    content: str
    splited: bool
    wordcount: int



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
'''
def chunk_layout_small2big_mod(
    document_id: str,
    layout_pages: List[PageLayout]
)-> List[TextChunk]:
    """
    chunk the text blocks in the pages into small chunks like so:
    we look at the wordcount of the text blocks if the wordcount is over 100 words we split the block in two
    (1000 works then deivide over 20 so we get a chunk of 100 words each) so the formula is: 2*(wordcount / 100)
    if its less than 100 we keep it as is
    """
    # TODO: make the chunk size biger
    chunks: List[TextChunk] = []
    for page in layout_pages:
        for i, block in enumerate(page.text_blocks):
            wordcount = block.wordcount
            if wordcount > 100:
                num_splits = round(2 * (wordcount / 100))
                words = _split_text_into_words(block.text)
                split_size = len(words) // num_splits
                for j in range(num_splits):
                    start_idx = j * split_size
                    end_idx = (j + 1) * split_size if j < num_splits - 1 else len(words)
                    chunk_words = words[start_idx:end_idx]
                    chunk_text = " ".join(chunk_words).strip()
                    chunk_id = f"{document_id}-p{page.page_number}-b{i}-s{j}"
                    chunks.append(
                        TextChunk(
                            id=chunk_id,
                            document_id=document_id,
                            page_id=page.page_number,
                            parent_block_id=i + page.page_number * 1000,
                            chunk_index=len(chunks),
                            content=chunk_text,
                            splited=True,
                            wordcount=len(chunk_words),
                        )
                    )
            else:
                chunk_id = f"{document_id}-p{page.page_number}-b{i}"
                chunks.append(
                    TextChunk(
                        id=chunk_id,
                        document_id=document_id,
                        page_id=page.page_number,
                        parent_block_id=i + page.page_number * 1000,
                        chunk_index=len(chunks),
                        content=block.text,
                        splited=False,
                        wordcount=wordcount,
                    )
                )

    return chunks

def expand_chunk_small2big_mod(
        hit: TextChunk,
        layout_pages: List[PageLayout],
)->List[TextChunk]:
    """
    we will take the hit chunk and then see if its splited or not
    if yes we will return the coplete block as a single chunk for the context 
    if not we will return the hit chunk as is + the previous and next chunk if they exist
    """
    if hit.splited:
        # find the block
        page = next((p for p in layout_pages if p.page_number == hit.page_id), None)
        if page is None:
            return [hit]
        block_index = hit.parent_block_id - hit.page_id * 1000
        block = page.text_blocks[block_index]
        chunk_id = f"{hit.document_id}-p{page.page_number}-b{block_index}"
        return [
            TextChunk(
                id=chunk_id,
                document_id=hit.document_id,
                page_id=page.page_number,
                parent_block_id=block_index + page.page_number * 1000,
                chunk_index=hit.chunk_index,
                content=block.text,
                splited=False,
                wordcount=block.wordcount,
            )
        ]
    else:
        # return hit + previous + next if they exist
        page = next((p for p in layout_pages if p.page_number == hit.page_id), None)
        if page is None:
            return [hit]
        block_index = hit.parent_block_id - hit.page_id * 1000
        chunks: List[TextChunk] = []
        # previous
        if block_index > 0:
            prev_block = page.text_blocks[block_index - 1]
            chunk_id = f"{hit.document_id}-p{page.page_number}-b{block_index - 1}"
            chunks.append(
                TextChunk(
                    id=chunk_id,
                    document_id=hit.document_id,
                    page_id=page.page_number,
                    parent_block_id=(block_index - 1) + page.page_number * 1000,
                    chunk_index=hit.chunk_index - 1,
                    content=prev_block.text,
                    splited=False,
                    wordcount=prev_block.wordcount,
                )
            )
        # hit
        chunks.append(hit)
        # next
        if block_index < len(page.text_blocks) - 1:
            next_block = page.text_blocks[block_index + 1]
            chunk_id = f"{hit.document_id}-p{page.page_number}-b{block_index + 1}"
            chunks.append(
                TextChunk(
                    id=chunk_id,
                    document_id=hit.document_id,
                    page_id=page.page_number,
                    parent_block_id=(block_index + 1) + page.page_number * 1000,
                    chunk_index=hit.chunk_index + 1,
                    content=next_block.text,
                    splited=False,
                    wordcount=next_block.wordcount,
                )
            )
        return chunks

'''


def chunk_layout_small2big_mod(
    document_id: str,
    layout_pages: List[PageLayout],
    chunk_size: int = 100,  # Target words per chunk
    overlap: int = 20       # Words of overlap
) -> List[TextChunk]:
    chunks: List[TextChunk] = []
    global_chunk_index = 0
    for page in layout_pages:
        for blk_idx, block in enumerate(page.text_blocks):
            wordcount = block.wordcount
            
            # METHOD A: PARENT RETRIEVAL (Big Blocks)
            # If block is significantly larger than our target chunk size
            if wordcount > (chunk_size * 1.5): 
                words = block.text.split() # Simple split; consider specialized tokenizers for production
                
                # Sliding window with overlap
                current_idx = 0
                sub_chunk_id = 0
                
                while current_idx < len(words):
                    # Define window
                    end_idx = min(current_idx + chunk_size, len(words))
                    chunk_words = words[current_idx:end_idx]
                    chunk_text = " ".join(chunk_words)
                    
                    # Create Chunk
                    unique_id = f"{document_id}-p{page.page_number}-b{blk_idx}-s{sub_chunk_id}"
                    chunks.append(TextChunk(
                        id=unique_id,
                        document_id=document_id,
                        page_id=page.page_number,
                        parent_block_id=blk_idx + page.page_number * 1000,
                        chunk_index=global_chunk_index,
                        content=chunk_text,
                        splited=True, # Mark as child of a parent block
                        wordcount=len(chunk_words)
                    ))
                    global_chunk_index += 1
                    # Move pointer, but backstep for overlap
                    current_idx += (chunk_size - overlap)
                    sub_chunk_id += 1
                    
                    # Break to prevent infinite loops if overlap >= chunk_size (sanity check)
                    if current_idx >= len(words): 
                        break

            # METHOD B: WINDOW RETRIEVAL (Small Blocks)
            else:
                unique_id = f"{document_id}-p{page.page_number}-b{blk_idx}"
                chunks.append(TextChunk(
                    id=unique_id,
                    document_id=document_id,
                    page_id=page.page_number,
                    parent_block_id=blk_idx + page.page_number * 1000,
                    chunk_index=global_chunk_index,
                    content=block.text,
                    splited=False, # Mark as standalone/contextual
                    wordcount=wordcount
                ))
                global_chunk_index += 1
    return chunks

def expand_chunk_small2big_mod(
    hit: TextChunk,
    chunks: List[TextChunk],
) -> List[TextChunk]:
    """
    Expands the context based on the chunk type.
    """

    # STRATEGY A: It was a split chunk -> Return the FULL Parent Block
    if hit.splited:
        # We reconstruct a new chunk representing the full parent
        hited_text_chunks = [t for t in chunks if t.parent_block_id == hit.parent_block_id]
        return hited_text_chunks

    # STRATEGY B: It was a small block -> Return Window (Prev + Curr + Next)
    else:
        prev = chunks[hit.chunk_index - 1] if hit.chunk_index > 0 else None
        next = chunks[hit.chunk_index + 1] if hit.chunk_index < len(chunks) - 1 else None
        return [prev,hit,next]

def chunk_layout_small2big(
    document_id: str,
    layout_pages: List["PageLayout"],
    *,
    small_chunk_words: int = 160,
    min_chunk_words: int = 60,
) -> List[TextChunk]:
    """
    Build SMALL chunks from PageLayout/TextBlocks.
    These chunks are what you embed and store in the vector DB.

    Strategy:
    - Iterate pages
    - Pack consecutive text_blocks until reaching small_chunk_words
    - Emit chunk (page-local)
    - Never cross page boundary (keeps provenance + expansion easy)
    """
    chunks: List[TextChunk] = []
    chunk_index = 0

    for page in layout_pages:
        i = 0
        while i < len(page.text_blocks):
            start_i = i
            current_words = 0
            parts: List[str] = []

            # Pack blocks until we hit target
            while i < len(page.text_blocks) and current_words < small_chunk_words:
                t = _normalize_text(page.text_blocks[i].text)
                if t:
                    parts.append(t)
                    # prefer metadata wordcount if available, else approximate
                    wc = page.text_blocks[i].wordcount
                    current_words += wc
                i += 1

            content = "\n".join(parts).strip()

            # If content is too small and we still have room, try to add one more block
            if current_words < min_chunk_words and i < len(page.text_blocks):
                t = _normalize_text(page.text_blocks[i].text)
                if t:
                    parts.append(t)
                    wc = page.text_blocks[i].wordcount
                    current_words += wc
                    i += 1
                content = "\n".join(parts).strip()

            if not content:
                break

            end_i = max(start_i, i - 1)

            start_block_index = start_i
            end_block_index = end_i

            chunk_id = f"{document_id}-p{page.page_number}-c{chunk_index}"

            chunks.append(
                TextChunk(
                    id=chunk_id,
                    document_id=document_id,
                    page_id=page.page_number,
                    chunk_index=chunk_index,
                    content=content,
                    start_block_index=start_block_index,
                    end_block_index=end_block_index,
                    wordcount=current_words,
                )
            )
            chunk_index += 1

            # Move forward: no overlap at small-chunk level (Small2Big handles context)
            # If you want a tiny overlap, you can set i = max(start_i+1, i-1) etc.

    return chunks

def expand_chunk_small2big(
    hit: TextChunk,
    layout_pages: List["PageLayout"],
    *,
    big_min_words: int = 450,
    big_max_words: int = 900,
    neighbor_blocks: int = 3,
) -> str:
    """
    Expand a retrieved SMALL chunk into BIG context by adding neighboring blocks on the same page.
    No document-specific heuristics required.
    """
    # Find the page
    page = next((p for p in layout_pages if p.page_number == hit.page_id), None)
    if page is None:
        return hit.content

    blocks = page.text_blocks
    start = max(0, hit.start_block_index - neighbor_blocks)
    end = min(len(blocks) - 1, hit.end_block_index + neighbor_blocks)

    parts: List[str] = []
    total_words = 0

    # First, take the window
    for idx in range(start, end + 1):
        b = blocks[idx]
        if getattr(b, "block_type", 0) != 0:
            continue
        t = _normalize_text(b.text)
        if not t:
            continue
        parts.append(t)
        wc = getattr(b, "wordcount", len(t.split()))
        total_words += wc

    # If still too small, expand outward alternately
    left = start - 1
    right = end + 1
    while total_words < big_min_words and (left >= 0 or right < len(blocks)):
        if left >= 0:
            b = blocks[left]
            if getattr(b, "block_type", 0) == 0:
                t = _normalize_text(b.text)
                if t:
                    parts.insert(0, t)
                    total_words += getattr(b, "wordcount", len(t.split()))
            left -= 1
            if total_words >= big_max_words:
                break

        if right < len(blocks):
            b = blocks[right]
            if getattr(b, "block_type", 0) == 0:
                t = _normalize_text(b.text)
                if t:
                    parts.append(t)
                    total_words += getattr(b, "wordcount", len(t.split()))
            right += 1
            if total_words >= big_max_words:
                break

    # Hard cut if too large (optional: keep whole blocks only; safer for citations)
    return "\n".join(parts).strip()


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
    *,
    preprocessed_layout_pages: List[PageLayout],
) -> List[Dict]:
    """
    Kombiniert Preprocessing (Layout + Bildcaptions) mit deinem bestehenden Chunking.
    """
    #preprocessed_layout_pages = preprocess_pdf(pdf_path, language="en")

    # chunks = chunk_layout_small2big(
    #     document_id=document_id,
    #     layout_pages=preprocessed_layout_pages,
    #     small_chunk_words=small_chunk_words,
    #     min_chunk_words=min_chunk_words,
    # )
    chunks = chunk_layout_small2big_mod(
        document_id=document_id,
        layout_pages=preprocessed_layout_pages,
    )

    result: List[Dict] = []
    for i, chunk in enumerate(chunks):
        result.append(
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "page_id" : chunk.page_id,
                "parent_block_id": chunk.parent_block_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "splited": chunk.splited,
                "wordcount": chunk.wordcount,
            }
        )
    return result


def chunk_all_pdfs_in_folder(
    folder: Path,
    small_chunk_words:int =160,
    min_chunk_words:int =60,
) -> List[Dict[str, Any]]:
    """
    Processes all PDFs in a folder and returns a big list of chunks.
    """
    all_chunks: List[Dict[str, Any]] = []
    for pdf_path in folder.glob("*.pdf"):
        document_id = pdf_path.stem  
        print(f"Processing PDF: {pdf_path.name}")
        doc_chunks = chunk_pdf_document_with_preprocessing(
            document_id=document_id,
            pdf_path=pdf_path,
            small_chunk_words=small_chunk_words,
            min_chunk_words=min_chunk_words,
        )
        all_chunks.extend(doc_chunks)

    return all_chunks
