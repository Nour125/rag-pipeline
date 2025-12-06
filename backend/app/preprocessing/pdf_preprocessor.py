from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
from pypdf import PdfReader


@dataclass
class TextBlock:
    page: int
    bbox: Any  # (x0, y0, x1, y1) – kannst später typisieren
    text: str


@dataclass
class ImageRegion:
    id: str
    page: int
    bbox: Any
    image_bytes: bytes


@dataclass
class PageLayout:
    page_number: int
    text_blocks: List[TextBlock]
    images: List[ImageRegion]


def analyze_pdf_layout(pdf_path: Path) -> List[PageLayout]:
    """
    Uses PyMuPDF to read text blocks and images with bounding boxes.
    """
    doc = fitz.open(pdf_path)
    layouts: List[PageLayout] = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1

        # Text blocks
        text_blocks: List[TextBlock] = []
        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text, *_ = block
            cleaned = " ".join(text.split())
            if cleaned.strip():
                text_blocks.append(
                    TextBlock(
                        page=page_number,
                        bbox=(x0, y0, x1, y1),
                        text=cleaned,
                    )
                )

        # Images
        image_regions: List[ImageRegion] = []
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            # Image data
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            # Bounding box approximieren (nicht perfekt, aber ok für MVP)
            # Optional: layout-Analyse verbessern
            image_rects = page.get_image_rects(xref)
            if not image_rects:
                continue
            rect = image_rects[0]
            bbox = (rect.x0, rect.y0, rect.x1, rect.y1)

            image_regions.append(
                ImageRegion(
                    id=f"page{page_number}_img{img_index}",
                    page=page_number,
                    bbox=bbox,
                    image_bytes=image_bytes,
                )
            )

        layouts.append(
            PageLayout(
                page_number=page_number,
                text_blocks=text_blocks,
                images=image_regions,
            )
        )

    return layouts

def remove_unnecessary_elements(layout_pages: List[PageLayout]) -> List[PageLayout]:
    """
    Very simple cleanup:
    - Remove very short text blocks that repeat on every page (e.g. headers/footers).
    """
    # Beispiel: Kandidaten sammeln (Text, page_count)
    text_count: Dict[str, int] = {}
    for layout in layout_pages:
        for block in layout.text_blocks:
            key = block.text.strip()
            text_count[key] = text_count.get(key, 0) + 1

    # Alles, was auf >50% der Seiten vorkommt und sehr kurz ist, gilt als "Boilerplate"
    total_pages = len(layout_pages)
    boilerplate_texts = {
        t
        for t, count in text_count.items()
        if count > total_pages / 2 or len(t) < 50
    }

    cleaned_pages: List[PageLayout] = []
    for layout in layout_pages:
        filtered_blocks = [
            b for b in layout.text_blocks if b.text not in boilerplate_texts
        ]
        cleaned_pages.append(
            PageLayout(
                page_number=layout.page_number,
                text_blocks=filtered_blocks,
                images=layout.images,
            )
        )

    return cleaned_pages
