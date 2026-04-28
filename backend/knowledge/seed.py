DEMO_DOCUMENTS = [
    {
        "slug": "irembo-services",
        "title": "IremboGov public services overview",
        "description": "Guidance for finding and starting public-service applications through Rwanda's digital service portal.",
        "source_type": "url",
        "source_url": "https://www.irembo.gov.rw/",
        "category": "Public services",
        "language": "English",
        "status": "approved",
        "freshness": "Current",
        "chunks": [
            {
                "section_title": "Finding services",
                "page_number": "Portal",
                "chunk_text": "IremboGov is used as a public digital gateway for many government services in Rwanda. A user should search for a service, read the requirements shown for that service, follow the listed steps, and use the official service page for the most current fees, documents, and eligibility details.",
            },
            {
                "section_title": "Trust and next steps",
                "page_number": "Portal",
                "chunk_text": "When a public-service question depends on current requirements, the assistant should cite the official service page and avoid guessing. Users should confirm final instructions on the source page or with the responsible institution.",
            },
        ],
    },
    {
        "slug": "education-research",
        "title": "Education and research information guide",
        "description": "Seed material for education, scholarship, university, research, and institutional knowledge questions.",
        "source_type": "pdf",
        "source_url": "https://www.mineduc.gov.rw/",
        "category": "Education",
        "language": "English",
        "status": "approved",
        "freshness": "Review monthly",
        "chunks": [
            {
                "section_title": "Research discovery",
                "page_number": "4",
                "chunk_text": "Students and researchers need a knowledge library that can surface relevant documents, summarize trusted materials, preserve citations, and help identify source gaps for human review.",
            },
            {
                "section_title": "Language inclusion",
                "page_number": "7",
                "chunk_text": "Kinyarwanda support should begin with language detection, translated or normalized queries, an expanding glossary, and human review for answers that may affect public understanding.",
            },
        ],
    },
    {
        "slug": "business-innovation",
        "title": "Business and innovation support directory",
        "description": "Starter material for business registration, investment guidance, innovation ecosystem, and funding discovery.",
        "source_type": "url",
        "source_url": "https://rdb.rw/",
        "category": "Innovation",
        "language": "English",
        "status": "approved",
        "freshness": "Current",
        "chunks": [
            {
                "section_title": "Ecosystem navigation",
                "page_number": "Directory",
                "chunk_text": "Ecosystem builders and institutions need a source-grounded assistant that can help users discover business, innovation, funding, and collaboration information while linking back to the responsible organizations.",
            },
            {
                "section_title": "Governance",
                "page_number": "Directory",
                "chunk_text": "Documents used for business or innovation guidance should have categories, approval status, source links, and freshness checks so administrators can remove outdated or untrusted material.",
            },
        ],
    },
    {
        "slug": "responsible-ai",
        "title": "Responsible AI operating rules",
        "description": "Rules for grounded answers, citations, privacy, role-based access, and low-confidence review.",
        "source_type": "policy",
        "source_url": "",
        "category": "Governance",
        "language": "English",
        "status": "approved",
        "freshness": "Always active",
        "chunks": [
            {
                "section_title": "Non-negotiable answer rule",
                "page_number": "6",
                "chunk_text": "The assistant should never answer without enough trusted evidence. If retrieval is weak, it must say: I am not sure based on the available trusted sources.",
            },
            {
                "section_title": "Security controls",
                "page_number": "6",
                "chunk_text": "The MVP should use role-based access control for admin actions, avoid collecting sensitive personal data, keep secrets out of source control, validate inputs, and track feedback for human review.",
            },
        ],
    },
    {
        "slug": "rwanda-knowledge-blueprint",
        "title": "Rwanda Knowledge AI Assistant design blueprint",
        "description": "The funder-ready design blueprint that defines the MVP, architecture, RAG workflow, and future roadmap.",
        "source_type": "pdf",
        "source_url": "",
        "category": "Platform design",
        "language": "English",
        "status": "approved",
        "freshness": "Planning draft",
        "chunks": [
            {
                "section_title": "MVP goal",
                "page_number": "1",
                "chunk_text": "The MVP should be a working demo that answers from trusted sources with citations and basic English and Kinyarwanda support.",
            },
            {
                "section_title": "Recommended stack",
                "page_number": "5",
                "chunk_text": "The recommended stack is React with Tailwind CSS, Django REST Framework, PostgreSQL with pgvector, Celery, Redis, a RAG pipeline, Docker, and cloud deployment.",
            },
        ],
    },
]


def seed_demo_sources(Document, DocumentChunk):
    for item in DEMO_DOCUMENTS:
        chunks = item.pop("chunks")
        document, _ = Document.objects.update_or_create(
            slug=item["slug"],
            defaults={**item, "is_active": True},
        )
        for chunk in chunks:
            DocumentChunk.objects.update_or_create(
                document=document,
                section_title=chunk["section_title"],
                page_number=chunk["page_number"],
                defaults={"chunk_text": chunk["chunk_text"]},
            )
        item["chunks"] = chunks
