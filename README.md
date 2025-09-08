# OpenWords — OSS transcript search & clipper (skeleton)

MVP stack:
- **API**: FastAPI
- **Worker**: Celery (Redis broker)
- **Search**: OpenSearch (BM25) + Qdrant (vectors, optional)
- **Storage**: MinIO (S3 compatible) — video/transcripts
- **DB**: Postgres
- **Web**: Next.js

## Quick start (dev)
```bash
# 1) Start services
docker compose up -d --build

# 2) Open web
open http://localhost:3000  # (mac)  or  xdg-open http://localhost:3000
```

### Services
- API: http://localhost:8000/docs
- Web: http://localhost:3000
- OpenSearch: http://localhost:9200
- Qdrant: http://localhost:6333
- MinIO console: http://localhost:9001 (user: `minio`, pass: `minio123`)
- Postgres: localhost:5432 (user: postgres / password: postgres)


### Docker image versions
Images are pinned for reproducibility:

- API/Worker: `python:3.11-slim`
- Web: `node:20`
- Postgres: `16`
- OpenSearch: `opensearchproject/opensearch:2.13.0`
- Qdrant: `qdrant/qdrant:v1.7.3`
- MinIO: `minio/minio:RELEASE.2024-04-18T19-09-19Z`
- Redis: `redis:7`

> **Note:** This is a skeleton intended for extension. Ingest/transcription is stubbed.