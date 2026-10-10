from helpdesk.chunking import chunk_text
from helpdesk.embedding import MODEL_NAME, embed, load_model
from helpdesk.repository import save_document_and_chunks
from helpdesk.storage import get_database_connection


def ingest_document(document_path: str, content: str, model_name: str = MODEL_NAME) -> int:
    if not content:
        return 0

    chunks = chunk_text(content)
    if not chunks:
        return 0

    model = load_model(model_name)
    embeddings = embed(model, chunks)

    with get_database_connection() as conn:
        try:
            from pgvector.psycopg import register_vector

            register_vector(conn)
        except Exception:
            pass

        document_id = save_document_and_chunks(
            conn,
            document_path=document_path,
            content=content,
            chunks=chunks,
            embeddings=embeddings,
            model_name=model_name,
        )

    return document_id
