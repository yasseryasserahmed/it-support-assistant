from pgvector.psycopg import register_vector

from helpdesk.embedding import embed, load_model
from helpdesk.repository import get_most_relevant_chunks
from helpdesk.storage import get_database_connection

# make sure that the model embedded the document chunks and the query prompt in the same
def get_more_context_from_prompt(prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    model = load_model()
    prompt_embedding = embed(model, [prompt])[0]

    with get_database_connection() as conn:
        register_vector(conn)
        relevant_chunks = get_most_relevant_chunks(
            conn,
            query_embedding=prompt_embedding,
            top_k=5,
        )

    if relevant_chunks:
        context = "\n\n".join(
            (
                f"[{index}] Source: {chunk['document_name']} "
                f"(chunk {chunk['chunk_index'] + 1}; {chunk['document_path']})\n"
                f"{chunk['content']}"
            )
            for index, chunk in enumerate(relevant_chunks, start=1)
        )
    else:
        context = "No relevant context was found in the indexed documents."

    return (
        "Answer the question using only the context below. Cite supporting "
        "sources using their [number]. If the context does not contain the "
        "answer, say you do not know.\n\n"
        f"Question: {prompt}\n\n"
        f"Relevant context:\n{context}"
    )