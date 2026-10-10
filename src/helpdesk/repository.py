import hashlib
from pathlib import Path


def save_document_and_chunks(conn, document_path: str, content: str, chunks: list[str], embeddings, model_name: str) -> int:
    document_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    file_name = Path(document_path).name

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO documents (path, name, content_hash, created_at)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (path) DO UPDATE
            SET name = EXCLUDED.name,
                content_hash = EXCLUDED.content_hash,
                created_at = now()
            RETURNING id
            """,
            (document_path, file_name, document_hash),
        )
        document_id = cursor.fetchone()[0]

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            cursor.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, content, embedding, embedding_model)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (document_id, chunk_index) DO UPDATE
                SET content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    embedding_model = EXCLUDED.embedding_model
                """,
                (document_id, index, chunk, embedding.tolist(), model_name),
            )
    finally:
        if hasattr(cursor, "close"):
            cursor.close()

    conn.commit()
    return document_id
