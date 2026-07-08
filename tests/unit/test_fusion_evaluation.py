import asyncio

from agentic_book.application.chunking import chunks_for_document
from agentic_book.application.fusion import FusionSearchCorpus
from agentic_book.application.fusion_evaluation import EvaluateFusionRetrieval
from agentic_book.domain.models import ContentObject, ContentObjectRef, FusionEvalCase
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


def test_evaluate_fusion_retrieval_computes_hit_rate_and_mrr() -> None:
    report = asyncio.run(
        EvaluateFusionRetrieval(FusionSearchCorpus(SimpleLexicalIndex(_chunks()))).run(
            [
                FusionEvalCase(
                    id="hit",
                    queries=["Streamable HTTP", "MCP resources"],
                    expected_document_ids=["concept.test"],
                    final_top_k=3,
                ),
                FusionEvalCase(id="unanswerable", queries=["zebra orchid compost"], expected_document_ids=[]),
            ]
        )
    )

    assert report.cases == 2
    assert report.hit_rate == 1.0
    assert report.mean_reciprocal_rank == 1.0
    assert report.unanswerable_success_rate == 1.0
