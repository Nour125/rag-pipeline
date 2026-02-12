from pathlib import Path
from app.preprocessing.pdf_preprocessor import preprocess_pdf
from app.utils.chunker import chunk_layout_small2big_mod, expand_chunk_small2big_mod

def main():
    project_root = Path(__file__).resolve().parents[2]
    pdf_folder = project_root / "data"
    preprocessed_layout_pages = preprocess_pdf(pdf_folder / "foo.pdf", language="en")

    chunks = chunk_layout_small2big_mod(
        document_id="foo.pdf",
        layout_pages=preprocessed_layout_pages,
    )
    hit = chunks[5]
    expanded_chunks = expand_chunk_small2big_mod(hit, chunks)
    
    print(f"Total chunks: {len(chunks)}")

    with open("Output5.txt", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(f"CHUNK ID: {c.id}\n")
            f.write(f"DOC: {c.document_id}\n")
            f.write(f"PARENT BLOCK ID: {c.parent_block_id}\n")
            f.write(f"CHUNK INDEX: {c.chunk_index}\n")
            f.write(f"CONTENT:\n{c.content}\n")
            f.write(f"PAGE ID: {c.page_id}\n")
            f.write(f"WORDCOUNT: {c.wordcount}\n")
            f.write(f"SPLITED: {c.splited}\n")
            f.write("-" * 50 + "\n\n")

    with open("Output5_expanded.txt", "w", encoding="utf-8") as f:
        for c in expanded_chunks:
            f.write(f"CHUNK ID: {c.id}\n")
            f.write(f"DOC: {c.document_id}\n")
            f.write(f"PARENT BLOCK ID: {c.parent_block_id}\n")
            f.write(f"CONTENT:\n{c.content}\n")
            f.write(f"PAGE ID: {c.page_id}\n")
            f.write(f"WORDCOUNT: {c.wordcount}\n")
            f.write(f"SPLITED: {c.splited}\n")
            f.write("-" * 50 + "\n\n")
        

        
if __name__ == "__main__":
    main()
