from pathlib import Path

import fitz

from backend.services.ocr_service import extract_text_from_image


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.

    First tries native PDF text extraction.
    If a page contains little/no text, render that page
    as an image and use OCR.
    """

    pdf_path = Path(file_path)

    document = fitz.open(pdf_path)

    extracted_pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            # Digital PDF page
            if len(text) >= 20:
                extracted_pages.append(
                    f"[PAGE {page_number}]\n{text}"
                )
                continue

            # Scanned/image PDF page → OCR
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
            )

            image_path = pdf_path.with_name(
                f"{pdf_path.stem}_page_{page_number}.png"
            )

            pixmap.save(image_path)

            try:
                ocr_text = extract_text_from_image(
                    str(image_path)
                )

                extracted_pages.append(
                    f"[PAGE {page_number}]\n{ocr_text}"
                )

            finally:
                if image_path.exists():
                    image_path.unlink()

    finally:
        document.close()

    return "\n\n".join(extracted_pages).strip()


def extract_text_from_document(
    file_path: str,
    file_type: str,
) -> str:
    """
    Extract text from a supported document.
    """

    normalized_type = file_type.lower().lstrip(".")

    if normalized_type == "pdf":
        return extract_text_from_pdf(file_path)

    if normalized_type in {"jpg", "jpeg", "png"}:
        return extract_text_from_image(file_path)

    raise ValueError(
        f"Unsupported document type: {file_type}"
    )