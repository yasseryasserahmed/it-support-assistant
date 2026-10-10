from __future__ import annotations

from pydantic import BaseModel, Field

from helpdesk.embedding import MODEL_NAME


class IngestRequest(BaseModel):
    path: str = Field(..., description="Source document path or identifier")
    content: str = Field(..., description="Raw document content to be chunked and embedded")
    model_name: str = Field(default=MODEL_NAME, description="Embedding model to use for this ingestion")


class ChunkRecord(BaseModel):
    id: int | None = None
    document_id: int
    chunk_index: int
    content: str
    embedding_model: str
    embedding: list[float]


class DocumentRecord(BaseModel):
    id: int | None = None
    path: str
    name: str
    content_hash: str
    created_at: str | None = None
    ingested_at: str | None = None
