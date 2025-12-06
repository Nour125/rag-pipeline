from pathlib import Path
from backend.app.preprocessing.pdf_preprocessor import analyze_pdf_layout, remove_unnecessary_elements
import lmstudio as lms
def main():
    pdf = Path("data/Data_Science.pdf")

    layouts = analyze_pdf_layout(pdf)
    for layout in layouts:
        print(f"Page {layout.page_number}:")
        for block in layout.text_blocks:
            print(f"  Text block: {block.text}...")
        for image in layout.images:
            print(f"  Image region: {image.id}, bbox: {image.bbox}")

    cleaned_layouts = remove_unnecessary_elements(layouts)
    for layout in cleaned_layouts:
        print(f"Page {layout.page_number}:")
        for block in layout.text_blocks:
            print(f"  Text block: {block.text}...")
        for image in layout.images:
            print(f"  Image region: {image.id}, bbox: {image.bbox}")

if __name__ == "__main__":
    main()
