# Rwanda Knowledge AI Assistant

This repository now contains a runnable MVP prototype based on the design blueprint in `Rwanda_Knowledge_AI_Assistant_Design_Blueprint.pdf`.

The prototype focuses on the blueprint's first proof points:

- Ask natural-language questions in English or Kinyarwanda mode.
- Retrieve from an approved demo knowledge base.
- Show citation cards for grounded answers.
- Use the required fallback when evidence is weak: `I am not sure based on the available trusted sources.`
- Browse source documents in a knowledge library.
- Queue admin sources for ingestion/review.
- Capture answer feedback and low-confidence answers for evaluation.

## Run Locally

Frontend only:

```bash
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal.

Backend API:

```bash
py -m pip install -r backend/requirements.txt
py backend/manage.py migrate
py backend/manage.py createsuperuser
py backend/manage.py runserver 127.0.0.1:8000
```

Run both, then open the frontend and sign in. All routes now require authenticated users; admin actions require a staff account.

Docker Compose:

```bash
docker compose up --build
```

Frontend: `http://127.0.0.1:5173`

Backend: `http://127.0.0.1:8000/api/health/`

## Build

```bash
npm run build
```

The built prototype can also be opened directly at `dist/index.html` because Vite is configured with relative asset paths.

## MVP Architecture Direction

The current implementation is a front-end prototype with an in-browser retrieval simulation. The production MVP should keep the same product surface and move the RAG workflow behind API endpoints:

- Frontend: React UI from this prototype.
- Backend: Django REST Framework.
- Database: PostgreSQL with pgvector.
- Jobs: Celery and Redis for PDF/URL ingestion.
- RAG: approved document filtering, chunk retrieval, grounded prompt, answer generation, citations, fallback.
- Governance: role-based admin access, feedback review, low-confidence answer review, audit logs.

Recommended endpoint mapping from the blueprint:

- `POST /api/questions/ask/`
- `GET /api/questions/history/`
- `POST /api/feedback/`
- `GET /api/documents/`
- `POST /api/documents/upload/`
- `POST /api/documents/ingest-url/`
- `GET /api/admin/analytics/`
- `GET /api/admin/unanswered-questions/`
- `GET /api/admin/low-confidence-answers/`
