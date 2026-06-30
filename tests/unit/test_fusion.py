import asyncio

from agentic_book.application.chunking import chunks_for_document
from agentic_book.application.fusion import FusionSearchCorpus, reciprocal_rank_fusion
from agentic_book.domain.models import ContentObject, ContentObjectRef, RetrievalQuery
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
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
tags: ["mcp"]
related: []
---

# Test Concept

Use Streamable HTTP for remote MCP servers. Tools and resources are exposed through MCP.
"""
    document = MarkdownDocumentParser().parse(ContentObject(ContentObjectRef("file:///tmp/test.md"), text))
    return chunks_for_document(document)


def test_reciprocal_rank_fusion_scores_shared_items_higher() -> None:
    scores = reciprocal_rank_fusion([["a", "b"], ["b", "c"]], k=60)

    assert scores["b"] > scores["a"]
    assert scores["b"] > scores["c"]


def test_fusion_search_combines_subqueries() -> None:
    results = asyncio.run(
        FusionSearchCorpus(SimpleLexicalIndex(_chunks())).run(
            ["Streamable HTTP", "MCP resources"],
            base_query=RetrievalQuery(query="combined", retrieval_mode="lexical"),
            final_top_k=3,
        )
    )

    assert results
    assert results[0].retrieval_mode == "fusion"
    assert "Contributed by subqueries" in (results[0].why_retrieved or "")
