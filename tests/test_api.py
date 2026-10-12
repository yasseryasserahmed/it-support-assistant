from fastapi.testclient import TestClient

from helpdesk import api
from helpdesk.embedding import MODEL_NAME


client = TestClient(api.app)


def test_ingest_pdf_extracts_and_ingests_uploaded_file(monkeypatch):
    extracted = []
    ingested = []

    def fake_extract_pdf_text(content: bytes) -> str:
        extracted.append(content)
        return "Extracted support guide"

    def fake_ingest_document(
        path: str, content: str, model_name: str = MODEL_NAME
    ) -> int:
        ingested.append((path, content, model_name))
        return 42

    monkeypatch.setattr(api, "extract_pdf_text", fake_extract_pdf_text)
    monkeypatch.setattr(api, "ingest_document", fake_ingest_document)

    response = client.post(
        "/ingest/pdf",
        files={"file": ("support-guide.pdf", b"pdf bytes", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "document_id": 42}
    assert extracted == [b"pdf bytes"]
    assert ingested == [
        ("support-guide.pdf", "Extracted support guide", MODEL_NAME)
    ]


def test_ingest_pdf_returns_unprocessable_entity_for_unextractable_pdf(monkeypatch):
    def reject_pdf(_: bytes) -> str:
        raise ValueError("PDF contains no extractable text.")

    monkeypatch.setattr(api, "extract_pdf_text", reject_pdf)

    response = client.post(
        "/ingest/pdf",
        files={"file": ("scanned.pdf", b"pdf bytes", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "PDF contains no extractable text."}


def test_ingest_pdf_returns_unprocessable_entity_for_malformed_pdf():
    response = client.post(
        "/ingest/pdf",
        files={"file": ("malformed.pdf", b"not a PDF", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Uploaded file is not a valid PDF."}


def test_ingest_pdf_rejects_files_over_upload_limit(monkeypatch):
    def unexpected_extraction(_: bytes) -> str:
        raise AssertionError("Oversized upload should not be extracted")

    monkeypatch.setattr(api, "extract_pdf_text", unexpected_extraction)

    response = client.post(
        "/ingest/pdf",
        files={
            "file": (
                "oversized.pdf",
                b"x" * (api.MAX_PDF_UPLOAD_SIZE + 1),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "PDF exceeds the 10 MiB upload limit."}
