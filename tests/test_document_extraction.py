from types import SimpleNamespace

import pytest

from helpdesk import document_extraction


def test_extract_pdf_text_joins_pages(monkeypatch):
    pages = [
        SimpleNamespace(extract_text=lambda: "First page"),
        SimpleNamespace(extract_text=lambda: "Second page"),
    ]
    monkeypatch.setattr(document_extraction, "PdfReader", lambda _: SimpleNamespace(pages=pages))

    assert document_extraction.extract_pdf_text(b"pdf bytes") == "First page\nSecond page"


def test_extract_pdf_text_rejects_empty_or_scanned_pdf(monkeypatch):
    page = SimpleNamespace(extract_text=lambda: "")
    monkeypatch.setattr(document_extraction, "PdfReader", lambda _: SimpleNamespace(pages=[page]))

    with pytest.raises(ValueError, match="no extractable text"):
        document_extraction.extract_pdf_text(b"pdf bytes")