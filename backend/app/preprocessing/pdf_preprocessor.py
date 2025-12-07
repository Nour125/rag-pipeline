from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from backend.app.models.image_captioner import caption_image_with_qwen_vl
import fitz  # PyMuPDF


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

def generate_image_descriptions(
    images: List[ImageRegion],
    *,
    language: str = "en",
) -> Dict[str, str]:
    """
    Generates a textual description for each image using LM Studio (e.g. qwen/qwen3-vl-4b).

    Args:
        images: List of ImageRegion objects extracted from the PDF layout.
        language: 'en' or 'de' language of the generated captions.

    Returns:
        Mapping from image_id (ImageRegion.id) to description text.
    """
    id_to_caption: Dict[str, str] = {}

    for img in images:
        try:
            caption = caption_image_with_qwen_vl(
                image_bytes=img.image_bytes,
                model="qwen/qwen3-vl-4b",
                language=language,
                max_tokens=512,
            )
        except Exception as e:
            # Fallback wenn etwas schiefgeht
            caption = f"[Image description unavailable: {e}]"

        id_to_caption[img.id] = caption

    return id_to_caption

def merge_text_and_image_descriptions(
    layout_pages: List[PageLayout],
    image_captions: Dict[str, str],
) -> str:
    """
    Simpler Ansatz:
    - Für jede Seite werden Bild-Regionen in künstliche TextBlöcke mit Caption umgewandelt.
    - Am Ende hat jede Seite nur noch TextBlöcke.
    - Diese werden nach y-Koordinate sortiert und zu Fließtext zusammengefügt.
    """

    all_doc_lines: List[str] = []

    # Seiten in Reihenfolge
    for layout in sorted(layout_pages, key=lambda lp: lp.page_number):
        # 1) Ausgangspunkt: vorhandene Textblöcke
        combined_blocks: List[TextBlock] = list(layout.text_blocks)

        # 2) Für jedes Bild einen TextBlock einfügen
        for img in layout.images:
            caption = image_captions.get(img.id)

            if caption:
                text = f"[IMAGE: {caption}]"
            else:
                text = "[IMAGE: No description available]"

            # künstlicher TextBlock an Position des Bildes
            caption_block = TextBlock(
                page=img.page,
                bbox=img.bbox,
                text=text,
            )
            combined_blocks.append(caption_block)

        # 3) Sortieren nach y0 = vertikale Position
        combined_blocks.sort(key=lambda b: b.bbox[1])  # bbox = (x0, y0, x1, y1)

        # 4) Text der Seite bauen
        page_lines = [block.text for block in combined_blocks if block.text.strip()]
        page_text = "\n".join(page_lines).strip()

        if page_text:
            all_doc_lines.append(f"[PAGE {layout.page_number}]")
            all_doc_lines.append(page_text)

    # 5) Alles zu einem Dokument-String
    return "\n\n".join(all_doc_lines)


def preprocess_pdf(
    pdf_path: Path,
    *,
    language: str = "en",
) -> str:
    """
    Full preprocessing pipeline for a PDF:
    1) Layout detection (text blocks + images)
    2) Remove unnecessary/boilerplate text elements
    3) Generate image descriptions via LM Studio
    4) Merge text and image descriptions into a single text string
    """
    # 1) Layout-Analyse
    layouts = analyze_pdf_layout(pdf_path)

    # 2) Boilerplate entfernen
    cleaned_layouts = remove_unnecessary_elements(layouts)

    # 3) Alle Bilder einsammeln
    all_images: List[ImageRegion] = []
    for layout in cleaned_layouts:
        all_images.extend(layout.images)

    # 4) Bildbeschreibungen erzeugen
    image_captions = generate_image_descriptions(
        images=all_images,
        language=language,
    )

    # 5) Text + Bildbeschreibungen zusammenführen
    merged_text = merge_text_and_image_descriptions(
        layout_pages=cleaned_layouts,
        image_captions=image_captions,
    )

    return merged_text
