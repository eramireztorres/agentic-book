from agentic_book.application.chunking import chunks_for_document
from agentic_book.domain.models import ContentObject, ContentObjectRef
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser


def test_chunks_for_document_creates_document_and_section_chunks() -> None:
    text = """---
id: "concept.test"
title: "Test Concept"
type: "concept"
domain: ["agents"]
audience: ["engineer"]
maturity: "experimental"
status: "draft"
last_reviewed: "2026-06-30"
source_quality: "curated"
tags: []
related: []
---

# Test Concept

Intro.
"""
    document = MarkdownDocumentParser().parse(ContentObject(ContentObjectRef("file:///tmp/test.md"), text))
    chunks = chunks_for_document(document)

    assert [chunk.kind for chunk in chunks] == ["document", "section"]
    assert chunks[0].id == "concept.test::document"
    assert chunks[1].id == "concept.test::section::0001"
    assert "Book: Agentic Book" in chunks[0].text
