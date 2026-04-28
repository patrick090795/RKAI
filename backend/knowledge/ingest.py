import re
from collections.abc import Iterable

from django.db import transaction

from .models import Document, DocumentChunk


MAX_CHUNK_CHARS = 950
MIN_CHUNK_CHARS = 220


def _clean_text(value):
    return re.sub(r"\s+", " ", (value or "")).strip()


def _chunk_text(text):
    cleaned = _clean_text(text)
    if not cleaned:
        return []

    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks = []
    current = []
    current_size = 0

    for part in parts:
        part = part.strip()
        if not part:
            continue

        incoming_size = len(part) + (1 if current else 0)
        if current and current_size + incoming_size > MAX_CHUNK_CHARS:
            chunk = " ".join(current).strip()
            if len(chunk) >= MIN_CHUNK_CHARS:
                chunks.append(chunk)
            current = [part]
            current_size = len(part)
            continue

        current.append(part)
        current_size += incoming_size

    if current:
        final_chunk = " ".join(current).strip()
        if final_chunk:
            chunks.append(final_chunk)

    return chunks


def _extract_pdf_chunks(document):
    from pypdf import PdfReader

    chunks = []
    document.file.open("rb")
    try:
        reader = PdfReader(document.file)
        for index, page in enumerate(reader.pages, start=1):
            page_text = _clean_text(page.extract_text() or "")
            if not page_text:
                continue

            for chunk in _chunk_text(page_text):
                chunks.append(
                    {
                        "chunk_text": chunk,
                        "section_title": f"Page {index}",
                        "page_number": str(index),
                    }
                )
    finally:
        document.file.close()

    return chunks


def _extract_url_chunks(document):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(
        document.source_url,
        timeout=15,
        headers={"User-Agent": "RKAI-MVP-Ingest/0.1"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    title = _clean_text(soup.title.string if soup.title else "") or "Web content"
    combined = _clean_text(" ".join(soup.stripped_strings))
    combined = combined[:120000]

    return [
        {
            "chunk_text": chunk,
            "section_title": title,
            "page_number": "URL",
        }
        for chunk in _chunk_text(combined)
    ]


def _build_chunks(document):
    if document.source_type == Document.SourceType.PDF and document.file:
        return _extract_pdf_chunks(document)
    if document.source_type == Document.SourceType.URL and document.source_url:
        return _extract_url_chunks(document)
    return []


def ingest_document_content(document):
    chunk_payloads = _build_chunks(document)
    if not isinstance(chunk_payloads, Iterable):
        return 0

    with transaction.atomic():
        DocumentChunk.objects.filter(document=document).delete()
        DocumentChunk.objects.bulk_create(
            [
                DocumentChunk(
                    document=document,
                    chunk_text=payload["chunk_text"],
                    section_title=payload.get("section_title", ""),
                    page_number=payload.get("page_number", ""),
                )
                for payload in chunk_payloads
                if payload.get("chunk_text")
            ]
        )

    return len(chunk_payloads)
