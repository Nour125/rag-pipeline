from dataclasses import dataclass
from typing import List

from app.preprocessing.pdf_preprocessor import PageLayout

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


def chunk_layout_small2big_mod(
    document_id: str,
    layout_pages: List[PageLayout],
    chunk_size: int = 50,  # Target words per chunk
    overlap: int = 10       # Words of overlap
) -> List[TextChunk]:
    """
    Chunks text blocks from layout pages using a hybrid strategy:
    - If a block is significantly larger than the target chunk size, it will be split into multiple chunks parents and children (METHOD A).
    - If a block is small enough, it will be kept as is (METHOD B).
    
    :param document_id: Unique identifier for the document
    :type document_id: str
    :param layout_pages: List of PageLayout objects representing the document's layout
    :type layout_pages: List[PageLayout]
    :param chunk_size: Target number of words per chunk
    :type chunk_size: int
    :param overlap: Number of words to overlap between chunks
    :type overlap: int
    :return: List of TextChunk objects representing the chunked text blocks
    :rtype: List[TextChunk]
    """
    chunks: List[TextChunk] = []
    global_chunk_index = 0
    for page in layout_pages:
        for blk_idx, block in enumerate(page.text_blocks):
            wordcount = block.wordcount
            
            # METHOD A: PARENT RETRIEVAL (Big Blocks)
            # If block is significantly larger than our target chunk size
            if wordcount > (chunk_size * 1.2): 
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
    Expands a hit chunk to include more context based on its type:
    - If the hit chunk is a child of a split block (METHOD A), 
        it retrieves all sibling chunks that belong to the same parent block,
        effectively reconstructing the full original block.
    - If the hit chunk is a small block (METHOD B),
        it currently returns just the hit chunk itself,
        but the logic is in place to potentially include adjacent chunks for additional context if needed
        (this part is currently disabled to avoid returning too much context).
    """

    # STRATEGY A: It was a split chunk -> Return the FULL Parent Block
    if hit.splited:
        # We reconstruct a new chunk representing the full parent
        hited_text_chunks = [t for t in chunks if t.parent_block_id == hit.parent_block_id]
        return hited_text_chunks

    # STRATEGY B: It was a small block -> Return Window (Prev + Curr + Next)
    else:
        return[hit]
    # THIS PART IS DISABLED FOR NOW, BECAUSE IT OFTEN RETURNS TOO MUCH CONTEXT
        # prev = chunks[hit.chunk_index - 1] if hit.chunk_index > 0 else None
        # next = chunks[hit.chunk_index + 1] if hit.chunk_index < len(chunks) - 1 else None
        # if prev is None:
        #     return [hit, next] if next else [hit]
        # if next is None:
        #     return [prev, hit] if prev else [hit]
        # return [prev,hit,next]

