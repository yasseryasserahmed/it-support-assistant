import pytest

from helpdesk import context_prompt


class FakeEmbedding:
    def tolist(self):
        return [0.1, 0.2, 0.3]


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_get_more_context_includes_cited_retrieved_chunks(monkeypatch):
    registered = []
    retrieved = []
    chunk = {
        "content": "Restart the workstation.",
        "document_name": "Support guide",
        "document_path": "docs/support-guide.pdf",
        "chunk_index": 1,
    }

    monkeypatch.setattr(context_prompt, "load_model", lambda: "model")
    monkeypatch.setattr(
        context_prompt, "embed", lambda model, texts: [FakeEmbedding()]
    )
    monkeypatch.setattr(
        context_prompt, "get_database_connection", FakeConnection
    )
    monkeypatch.setattr(
        context_prompt, "register_vector", lambda conn: registered.append(conn)
    )

    def fake_get_relevant_chunks(conn, query_embedding, top_k):
        retrieved.append((conn, query_embedding.tolist(), top_k))
        return [chunk]

    monkeypatch.setattr(
        context_prompt, "get_most_relevant_chunks", fake_get_relevant_chunks
    )

    result = context_prompt.get_more_context_from_prompt("How do I restart?")

    assert "Question: How do I restart?" in result
    assert "[1] Source: Support guide (chunk 2; docs/support-guide.pdf)" in result
    assert "Restart the workstation." in result
    assert "say you do not know" in result
    assert registered == [retrieved[0][0]]
    assert retrieved[0][1:] == ([0.1, 0.2, 0.3], 5)


def test_get_more_context_explains_when_no_chunks_match(monkeypatch):
    monkeypatch.setattr(context_prompt, "load_model", lambda: "model")
    monkeypatch.setattr(
        context_prompt, "embed", lambda model, texts: [FakeEmbedding()]
    )
    monkeypatch.setattr(
        context_prompt, "get_database_connection", FakeConnection
    )
    monkeypatch.setattr(context_prompt, "register_vector", lambda conn: None)
    monkeypatch.setattr(
        context_prompt, "get_most_relevant_chunks", lambda *args, **kwargs: []
    )

    result = context_prompt.get_more_context_from_prompt("Unknown question")

    assert "No relevant context was found" in result
    assert "say you do not know" in result


def test_get_more_context_rejects_blank_prompt():
    with pytest.raises(ValueError, match="Prompt must not be empty"):
        context_prompt.get_more_context_from_prompt("  ")
