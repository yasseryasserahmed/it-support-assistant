# IT Support Assistant

An IT helpdesk assistant that answers employee questions from internal documentation, with citations and measured accuracy.

## Architecture overview

The project follows a layered architecture designed for local development now and cloud deployment later:

- API layer: FastAPI routes for ingestion and future query endpoints
- Service layer: chunking, embedding, and orchestration logic
- Repository layer: database writes and reads for document and chunk persistence
- Data layer: PostgreSQL with pgvector for vector search

This keeps the app modular and avoids mixing ingestion business logic with database connection code.

## Database setup

The application uses PostgreSQL with the pgvector extension to store document metadata and chunk embeddings for semantic retrieval. This local-first setup mirrors the architecture we plan to deploy in the cloud later, while keeping the development workflow simple and reproducible.

### Local database with Docker

The database runs in Docker with a persistent named volume so data is retained across container restarts and rebuilds. This lets us develop and validate the ingestion pipeline locally before moving the same design to a managed cloud environment.

- Service: `db`
- Image: `pgvector/pgvector:pg16`
- Port: `127.0.0.1:5433:5432`
- Volume: `pgdata` mounted at `/var/lib/postgresql/data`
- Credentials are defined in `.env`

This keeps the database state local and durable while developing the project while preserving the data model and structure we can later host in Azure or another cloud provider.

### Schema

The database schema is defined in `db-schema.sql` and includes:

- `CREATE EXTENSION IF NOT EXISTS vector;`
- `documents` table for source files and ingestion metadata
- `chunks` table for chunked content and embeddings
- a foreign key from `chunks.document_id` to `documents.id`
- a unique constraint on `(document_id, chunk_index)` to prevent duplicate chunk numbering
- a `content_hash` field to detect whether a document has changed before reprocessing

The schema is designed for a RAG-style ingestion pipeline and is compatible with the same architecture we intend to run in the cloud later.

- one row in `documents` per source file
- many rows in `chunks` per document
- each chunk stores its text content and a vector embedding
- retrieval uses the vector similarity search over chunk embeddings

### Ingestion API

The ingestion flow is exposed through a FastAPI endpoint and is kept separate from the storage layer.

- API file: `src/helpdesk/api.py`
- service logic: `src/helpdesk/ingest_service.py`
- repository logic: `src/helpdesk/repository.py`
- `POST /ingest` accepts JSON text content.
- `POST /ingest/pdf` accepts a PDF as a multipart form field named `file`, extracts its text, and sends it through the same ingestion pipeline.

PDF upload example:

```sh
curl -F "file=@support-guide.pdf" http://localhost:8000/ingest/pdf
```

This structure keeps the database layer focused on persistence and the app logic focused on ingest orchestration.

### Database population flow

The database population process is built around ingesting source documents, splitting them into chunks, generating embeddings, and storing the results. The local implementation is the foundation for the later cloud version, where the same pipeline can be hosted in managed services and connected to the same database schema.

Relevant workflow:

1. Receive a document or text payload through the API.
2. Split the document into text chunks.
3. Generate embeddings for each chunk.
4. Store the document metadata in `documents`.
5. Store each chunk and its embedding in `chunks`.
6. Reuse the same chunk/embedding records during retrieval and answer generation.

The database layer is therefore the persistent storage for the knowledge base that powers the assistant, and it is designed to scale cleanly to a cloud deployment in the future.

Status: in progress
