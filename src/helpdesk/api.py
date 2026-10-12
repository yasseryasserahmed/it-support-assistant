from fastapi import FastAPI, File, HTTPException, UploadFile
from pypdf.errors import PdfReadError
from starlette.concurrency import run_in_threadpool

from helpdesk.ingest_service import ingest_document
from helpdesk.document_extraction import extract_pdf_text
from helpdesk.types import IngestRequest

app = FastAPI(title="IT Support Assistant API")
MAX_PDF_UPLOAD_SIZE = 10 * 1024 * 1024


@app.post("/ingest")
def ingest_document_route(payload: IngestRequest):
    document_id = ingest_document(payload.path, payload.content, payload.model_name)
    return {
        "status": "ok" if document_id else "empty",
        "document_id": document_id,
    }


@app.post("/ingest/pdf")
async def ingest_pdf_route(file: UploadFile = File(...)):
    pdf_content = await file.read(MAX_PDF_UPLOAD_SIZE + 1)
    if len(pdf_content) > MAX_PDF_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds the {MAX_PDF_UPLOAD_SIZE // (1024 * 1024)} MiB upload limit.",
        )

    try:
        pdf_text = await run_in_threadpool(extract_pdf_text, pdf_content)
    except PdfReadError as exc:
        raise HTTPException(
            status_code=422, detail="Uploaded file is not a valid PDF."
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    document_id = await run_in_threadpool(
        ingest_document, file.filename or "uploaded.pdf", pdf_text
    )
    return {
        "status": "ok" if document_id else "empty",
        "document_id": document_id,
    }
