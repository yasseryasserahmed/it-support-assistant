from fastapi import FastAPI

from helpdesk.ingest_service import ingest_document
from helpdesk.types import IngestRequest

app = FastAPI(title="IT Support Assistant API")


@app.post("/ingest")
def ingest_document_route(payload: IngestRequest):
    document_id = ingest_document(payload.path, payload.content, payload.model_name)
    return {
        "status": "ok" if document_id else "empty",
        "document_id": document_id,
    }
