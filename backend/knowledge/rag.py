import re

from .models import Answer, Citation, Document, DocumentChunk, Question


FALLBACK = "I am not sure based on the available trusted sources."

KINYARWANDA_HINTS = [
    "amakuru",
    "muraho",
    "serivisi",
    "uburezi",
    "ubushakashatsi",
    "ikinyarwanda",
    "inyandiko",
    "urwanda",
    "icyangombwa",
    "kwiyandikisha",
    "ubuyobozi",
    "ubucuruzi",
]


def normalize(value):
    return [
        token
        for token in re.sub(r"[^a-z0-9\s]", " ", value.lower()).split()
        if token
    ]


def detect_language(question_text, selected_language):
    if selected_language and selected_language != "Auto":
        return selected_language
    lower_question = question_text.lower()
    if any(hint in lower_question for hint in KINYARWANDA_HINTS):
        return "Kinyarwanda"
    return "English"


def score_chunk(question_tokens, chunk):
    document = chunk.document
    searchable = normalize(
        " ".join(
            [
                document.title,
                document.category,
                document.description,
                chunk.chunk_text,
                chunk.section_title,
            ]
        )
    )
    searchable_set = set(searchable)
    matches = [token for token in question_tokens if token in searchable_set]
    long_matches = [
        token
        for token in question_tokens
        if len(token) > 4 and any(token in value or value in token for value in searchable)
    ]
    return len(matches) + len(long_matches)


def retrieve_evidence(question_text, limit=3):
    question_tokens = [token for token in normalize(question_text) if len(token) > 2]
    if not question_tokens:
        return []

    candidates = []
    queryset = (
        DocumentChunk.objects.select_related("document")
        .filter(document__status=Document.Status.APPROVED, document__is_active=True)
        .order_by("document_id", "id")
    )
    for chunk in queryset:
        score = score_chunk(question_tokens, chunk)
        if score > 0:
            candidates.append({"chunk": chunk, "score": score})

    return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]


def confidence_from_evidence(evidence):
    if not evidence:
        return 0
    top_score = evidence[0]["score"]
    support_score = sum(item["score"] for item in evidence)
    return min(0.94, 0.38 + top_score * 0.08 + support_score * 0.025)


def status_from_confidence(confidence):
    if confidence >= 0.74:
        return Answer.Status.ANSWERED
    if confidence >= 0.58:
        return Answer.Status.LOW_CONFIDENCE
    return Answer.Status.NEEDS_REVIEW


def create_answer_text(evidence, language):
    leading = evidence[0]["chunk"]
    supporting = evidence[1]["chunk"] if len(evidence) > 1 else None
    if language == "Kinyarwanda":
        parts = [
            "Dushingiye ku masoko yemejwe, igisubizo kigomba kuva ku nyandiko zizewe kandi kikerekana aho amakuru yavuye.",
            leading.chunk_text,
        ]
        if supporting:
            parts.append(
                f"Andi makuru ashyigikira iki gisubizo agaragara muri \"{supporting.document.title}\"."
            )
        return " ".join(parts)

    parts = [
        "Based on approved sources, the assistant should answer only from retrieved evidence and keep the source visible to the user.",
        leading.chunk_text,
    ]
    if supporting:
        parts.append(f"A supporting source also says: {supporting.chunk_text}")
    return " ".join(parts)


def answer_question(question_text, selected_language="Auto", user=None):
    detected_language = detect_language(question_text, selected_language)
    question = Question.objects.create(
        user=user if user and user.is_authenticated else None,
        question_text=question_text,
        detected_language=detected_language,
    )
    evidence = retrieve_evidence(question_text)
    confidence = confidence_from_evidence(evidence)
    status = status_from_confidence(confidence)
    answer_text = FALLBACK if status == Answer.Status.NEEDS_REVIEW else create_answer_text(evidence, detected_language)

    answer = Answer.objects.create(
        question=question,
        answer_text=answer_text,
        confidence_score=confidence,
        status=status,
        model_used="retrieval-demo",
    )

    if status != Answer.Status.NEEDS_REVIEW:
        for item in evidence:
            chunk = item["chunk"]
            Citation.objects.create(
                answer=answer,
                document=chunk.document,
                source_url=chunk.document.source_url,
                chunk_reference=f"chunk:{chunk.id}",
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                excerpt=chunk.chunk_text,
                score=item["score"],
            )

    return serialize_answer(answer)


def label_status(status):
    return {
        Answer.Status.ANSWERED: "Answered",
        Answer.Status.LOW_CONFIDENCE: "Low confidence",
        Answer.Status.NEEDS_REVIEW: "Needs review",
    }.get(status, status)


def serialize_answer(answer):
    citations = [
        {
            "id": citation.id,
            "documentId": citation.document_id,
            "title": citation.document.title,
            "category": citation.document.category,
            "sourceUrl": citation.source_url,
            "page": citation.page_number,
            "section": citation.section_title,
            "excerpt": citation.excerpt,
            "score": citation.score,
        }
        for citation in answer.citations.select_related("document").all()
    ]
    return {
        "id": answer.id,
        "question": answer.question.question_text,
        "answer": answer.answer_text,
        "language": answer.question.detected_language,
        "confidence": answer.confidence_score,
        "status": label_status(answer.status),
        "modelUsed": answer.model_used,
        "createdAt": answer.created_at.isoformat(),
        "citations": citations,
    }
