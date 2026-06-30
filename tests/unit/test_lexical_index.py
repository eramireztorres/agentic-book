import asyncio

from agentic_book.application.chunking import chunks_for_document
from agentic_book.domain.models import ContentObject, ContentObjectRef, RetrievalFilters, RetrievalQuery
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex, tokenize
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser


def _chunks():
    text = """---
id: "concept.test"
title: "Test Concept"
type: "concept"
domain: ["agents", "mcp"]
audience: ["engineer"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
tags: ["streamable-http"]
related: []
---

# Test Concept

Use Streamable HTTP for remote MCP servers.
"""
    document = MarkdownDocumentParser().parse(ContentObject(ContentObjectRef("file:///tmp/test.md"), text))
    return chunks_for_document(document)


def test_tokenize_normalizes_terms() -> None:
    assert tokenize("Streamable HTTP MCP") == ["streamable", "http", "mcp"]


def test_simple_lexical_index_finds_matching_chunk() -> None:
    index = SimpleLexicalIndex(_chunks())
    results = asyncio.run(index.search(RetrievalQuery(query="Streamable HTTP", top_k=2, retrieval_mode="lexical")))

    assert results
    assert results[0].document_id == "concept.test"
    assert results[0].score > 0


def test_simple_lexical_index_applies_filters() -> None:
    index = SimpleLexicalIndex(_chunks())
    filters = RetrievalFilters(tags=["missing"])
    results = asyncio.run(
        index.search(RetrievalQuery(query="Streamable HTTP", filters=filters, retrieval_mode="lexical"))
    )

    assert results == []
