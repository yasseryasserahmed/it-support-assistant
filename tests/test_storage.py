import numpy as np

from helpdesk import storage


class DummyCursor:
    def __init__(self):
        self.rows = []

    def execute(self, query, params=None):
        self.rows.append((query, params))
        if "RETURNING id" in query:
            return type("Result", (), {"fetchone": lambda self: (42,)})()
        return None

    def fetchone(self):
        return (42,)


class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        pass


def test_ingest_document_inserts_document_and_chunks(monkeypatch):
    seen = []

    def fake_get_database_connection():
        return DummyConnection()

    monkeypatch.setattr(storage, "get_database_connection", fake_get_database_connection)
    monkeypatch.setattr(storage, "chunk_text", lambda text, **kwargs: ["chunk 1", "chunk 2"])
    monkeypatch.setattr(storage, "load_model", lambda model_name=None: "model")
    monkeypatch.setattr(
        storage,
        "embed",
        lambda model, texts: np.array([[0.1, 0.2, 0.3]] * len(texts), dtype=float),
    )

    def fake_execute(self, query, params=None):
        seen.append((query, params))
        if "RETURNING id" in query:
            return type("Result", (), {"fetchone": lambda self: (42,)})()
        return None

    monkeypatch.setattr(DummyCursor, "execute", fake_execute)

    storage.ingest_document("/tmp/doc.txt", "Doc content")

    assert any("INSERT INTO documents" in q for q, _ in seen)
    assert any("INSERT INTO chunks" in q for q, _ in seen)
