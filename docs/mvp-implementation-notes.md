# MVP Implementation Notes

## Blueprint To Prototype Mapping

| Blueprint module | Implemented in prototype |
| --- | --- |
| Question interface | Ask AI view with language selector, question box, answer card, confidence, citations, and feedback. |
| Knowledge base | Seeded approved source documents with categories, source type, status, freshness, and chunks. |
| RAG engine | In-browser retrieval scoring over approved source chunks, confidence thresholding, and fallback. |
| Admin dashboard | Source governance view with metrics, source queue, category/language fields, and pending review status. |
| Feedback and evaluation | Quality view with feedback items and low-confidence answer review queue. |
| Kinyarwanda support | Language selector, simple detection hints, and Kinyarwanda-mode answer framing. |

## Production Backend Build Order

1. Create Django project with apps for accounts, documents, questions, feedback, and analytics.
2. Add PostgreSQL and pgvector models for documents and document chunks.
3. Implement document upload and URL ingestion endpoints.
4. Add Celery workers for extraction, cleaning, chunking, embedding, and indexing.
5. Replace the in-browser retriever with `POST /api/questions/ask/`.
6. Add role-based access control for admin source management.
7. Add rate limiting, audit logs, file validation, secret management, and deployment configuration.

## Grounding Rule

Every answer must be backed by approved source chunks. If the retriever cannot find enough trusted evidence, the system must return:

```text
I am not sure based on the available trusted sources.
```

## Notes On Seed Data

The included source records are demo seed material for MVP behavior. Before a public pilot, replace or supplement them with reviewed official PDFs, URLs, and institution-approved content.
