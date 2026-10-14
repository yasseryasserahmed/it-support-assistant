from helpdesk.repository import get_most_relevant_chunks


class FakeEmbedding:
    def tolist(self):
        return [0.1, 0.2, 0.3]


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.row_factory = None

    def cursor(self, row_factory):
        self.row_factory = row_factory
        return self.fake_cursor


def test_get_most_relevant_chunks_returns_document_citation_metadata():
    rows = [
        {
            "content": "Restart the workstation.",
            "document_name": "Support guide",
            "document_path": "docs/support-guide.pdf",
            "chunk_index": 0,
        }
    ]
    cursor = FakeCursor(rows)
    conn = FakeConnection(cursor)

    result = get_most_relevant_chunks(conn, FakeEmbedding(), top_k=3)

    assert result == rows
    assert "JOIN documents d ON d.id = c.document_id" in cursor.query
    assert "d.name AS document_name" in cursor.query
    assert "d.path AS document_path" in cursor.query
    assert cursor.params == ([0.1, 0.2, 0.3], [0.1, 0.2, 0.3], 3)
