import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect

from helpdesk.chunking import chunk_text
from helpdesk.embedding import MODEL_NAME, embed, load_model

load_dotenv()


def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set. Add it to your .env file.")
    return db_url


def get_database_connection():
    return connect(get_database_url())


def initialize_database() -> None:
    schema_path = Path(__file__).resolve().parents[2] / "db-schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    sql = schema_path.read_text(encoding="utf-8")
    statements = [part.strip() for part in sql.split(";") if part.strip()]

    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        conn.commit()


def ingest_document(document_path: str, content: str, model_name: str = "BAAI/bge-small-en-v1.5") -> int:
    from helpdesk.ingest_service import ingest_document as ingest_document_service

    return ingest_document_service(document_path, content, model_name)