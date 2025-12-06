from pathlib import Path
from backend.app.utils.chunker import chunk_all_pdfs_in_folder

def main():
    pdf_folder = Path("data")

    chunks = chunk_all_pdfs_in_folder(
        pdf_folder,
        chunk_size_words=220,
        chunk_overlap_words=40,
    )

    print(f"Total chunks: {len(chunks)}")
    # Print first 3 chunks as sample
    for chunk in chunks[:3]:
        print(chunk)
        

if __name__ == "__main__":
    main()
