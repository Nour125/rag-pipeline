from pathlib import Path
from app.preprocessing.pdf_preprocessor import analyze_pdf_layout, preprocess_pdf, remove_unnecessary_elements
import lmstudio as lms
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from typing import Iterable, Optional
from PyPDF2 import PdfReader

def main():

    def _safe_font(size: int = 14) -> ImageFont.ImageFont:
        """Try to load a truetype font; fallback to default."""
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()
    
    def visualize_layout(
    pdf_path: Path,
    layouts: list,  # list[PageLayout]
    out_dir: Path,
    *,
    zoom: float = 3.0,
    max_pages: Optional[int] = None,
    draw_text_snippet: bool = False,
) -> list[Path]:
        """
        Renders PDF pages and overlays rectangles for each TextBlock bbox.

        - zoom: render scale; 3.0 is a good default
        - draw_text_snippet: if True, prints a short snippet under the label
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(pdf_path)

        font = _safe_font(14)
        saved: list[Path] = []

        # Map page_number -> layout (in case your list is not strictly ordered)
        layout_by_page = {pl.page_number: pl for pl in layouts}

        page_numbers = sorted(layout_by_page.keys())
        if max_pages is not None:
            page_numbers = page_numbers[:max_pages]

        for page_no in page_numbers:
            page = doc[page_no -1]  # PyMuPDF pages are 0-indexed usually
            layout = layout_by_page[page_no]

            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            draw = ImageDraw.Draw(img)

            # Draw each block bbox
            for i, block in enumerate(layout.text_blocks):
                x0, y0, x1, y1 = block.bbox

                # scale bbox by zoom
                x0, y0, x1, y1 = x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom

                # rectangle
                draw.rectangle([x0, y0, x1, y1], width=3, outline="red")

                # label background box
                label = f"{i} | {block.block_type} | wc={block.wordcount}"
                label_x, label_y = x0 + 4, max(0, y0 - 18)
                tw, th = draw.textbbox((0, 0), label, font=font)[2:]
                draw.rectangle([label_x - 2, label_y - 2, label_x + tw + 6, label_y + th + 2], fill="white")
                draw.text((label_x, label_y), label, fill="black", font=font)

                if draw_text_snippet:
                    snippet = (block.text or "").strip().replace("\n", " ")
                    snippet = snippet[:90] + ("…" if len(snippet) > 90 else "")
                    sy = label_y + th + 2
                    sw, sh = draw.textbbox((0, 0), snippet, font=font)[2:]
                    draw.rectangle([label_x - 2, sy - 2, label_x + sw + 6, sy + sh + 2], fill="white")
                    draw.text((label_x, sy), snippet, fill="black", font=font)

            out_path = out_dir / f"page_{page_no+1:03d}.png"
            img.save(out_path)
            saved.append(out_path)

        doc.close()
        return saved

    project_root = Path(__file__).resolve().parents[2]
    pdf_path = project_root / "data/foo.pdf"
    text_output_path = project_root / "debug_layout" / "extracted_text.txt"
    layouts = preprocess_pdf(pdf_path)  # now returns List[PageLayout]
    # print(list(y for x in layouts for y in x.text_blocks))
    paths = visualize_layout(pdf_path, layouts, project_root / "debug_layout", zoom=2.0, max_pages=5)
    # read the text frim the pdf file in pdf_path and save it also to debug_layout without using layout 
    reader = PdfReader(pdf_path)

    with open(text_output_path, "w", encoding="utf-8") as f:
        for page in reader.pages:
            text = page.extract_text()
            if text:
                f.write(text + "\n")

    
    print(paths)

if __name__ == "__main__":
    main()
