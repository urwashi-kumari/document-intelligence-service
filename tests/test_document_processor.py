from pathlib import Path

from backend.services.document_processor import extract_text_from_document


def test_extract_text_from_pdf():
    sample_pdf = Path("sample_documents/sample.pdf")

    assert sample_pdf.exists(), "Test PDF does not exist."

    text = extract_text_from_document(
        str(sample_pdf),
        "pdf",
    )

    assert isinstance(text, str)
    assert len(text.strip()) > 0