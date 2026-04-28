# Backend API

The Django backend lives in `backend/` and implements the MVP endpoints from the blueprint.

## Local Setup

```bash
py -m pip install -r backend/requirements.txt
py backend/manage.py migrate
py backend/manage.py createsuperuser
py backend/manage.py runserver 127.0.0.1:8000
```

Knowledge app migrations seed five approved demo sources and chunks.

## Smoke Test

```bash
curl http://127.0.0.1:8000/api/health/
curl http://127.0.0.1:8000/api/documents/
```

Ask endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/questions/ask/ \
  -H "Content-Type: application/json" \
  -d "{\"question_text\":\"What is the recommended technical stack?\",\"language\":\"English\"}"
```

Auth endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"<admin-username>\",\"password\":\"<admin-password>\"}"
```

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health/` | API health check. |
| POST | `/api/auth/login/` | Sign in and receive a DRF token. |
| POST | `/api/auth/logout/` | Invalidate the current token. |
| GET | `/api/auth/me/` | Return current auth/session state. |
| POST | `/api/questions/ask/` | Retrieve approved chunks, create an answer, return citations. |
| GET | `/api/questions/history/` | Latest answer history for the authenticated user (anonymous requests return an empty list). |
| POST | `/api/feedback/` | Store helpfulness or issue feedback. |
| GET | `/api/documents/` | List knowledge sources. |
| POST | `/api/documents/upload/` | Queue a PDF source for review. |
| POST | `/api/documents/ingest-url/` | Queue a URL source for review. |
| POST | `/api/documents/{id}/status/` | Update source status (`approved`, `rejected`, `archived`, etc.). |
| GET | `/api/documents/{id}/` | Source detail. |
| DELETE | `/api/documents/{id}/` | Delete a source. |
| GET | `/api/admin/analytics/` | Counts for documents, questions, answers, and feedback. |
| GET | `/api/admin/unanswered-questions/` | Answers that used the uncertainty fallback. |
| GET | `/api/admin/low-confidence-answers/` | Answers needing review. |

All endpoints require authentication by default. Admin endpoints are staff-only.
Use `Authorization: Token <token>` for authenticated API requests after `POST /api/auth/login/`.

`POST /api/documents/upload/` expects `multipart/form-data` and requires a `file` when `source_type` is `pdf`.
Upload and ingest endpoints now attempt content extraction and chunk creation immediately; failures mark the source as `failed`.

## Current RAG Behavior

The backend uses a deterministic keyword retriever over approved chunks. That keeps the MVP testable while preserving the production contract:

1. Detect language.
2. Retrieve approved and active chunks.
3. Score evidence.
4. Create a grounded answer with citations.
5. Return `I am not sure based on the available trusted sources.` when evidence is weak.

The next backend upgrade is replacing keyword scoring with embeddings and pgvector while keeping the same response shape.
