"""Chunk generation use case helpers."""

from __future__ import annotations

import hashlib

from agentic_book.domain.models import Chunk, Document


def chunks_for_document(document: Document) -> list[Chunk]:
    """Create document and section chunks with deterministic ids."""

    chunks: list[Chunk] = [
        Chunk(
            id=f"{document.metadata.id}::document",
            document_id=document.metadata.id,
            text=_contextualize(document, document.body, None),
            kind="document",
            source_uri=document.source_uri,
            metadata=document.metadata,
            content_hash=_sha256(document.body),
        )
    ]
    for section in document.sections:
        chunks.append(
            Chunk(
                id=f"{document.metadata.id}::section::{section.id}",
                document_id=document.metadata.id,
                text=_contextualize(document, section.text, section.heading),
                kind="section",
                source_uri=document.source_uri,
                metadata=document.metadata,
                section_id=section.id,
                section_heading=section.heading,
                content_hash=_sha256(section.text),
            )
        )
    return chunks


def _contextualize(document: Document, text: str, heading: str | None) -> str:
    heading_part = f" | Heading: {heading}" if heading else ""
    prefix = (
        f"[Book: Agentic Book | Layer: {document.metadata.layer} | "
        f"Type: {document.metadata.type} | Title: {document.metadata.title}{heading_part}]"
    )
    return f"{prefix}\n\n{text.strip()}"


def _sha256(text: str) -> str:
    normalized = "\n".join(line.rstrip() for line in text.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
