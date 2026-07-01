import asyncio

import pytest

from agentic_book.application.chunking import chunks_for_document
from agentic_book.domain.models import ContentObject, ContentObjectRef, RetrievalQuery
from agentic_book.infrastructure.embeddings.hashing import HashingEmbeddingProvider
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.vectorstores.lancedb import LanceDBVectorStore


def test_lancedb_vector_store_persists_and_searches(tmp_path) -> None:
    pytest.importorskip("lancedb")
    chunks = _chunks()
    provider = HashingEmbeddingProvider()
    vectors = asyncio.run(provider.embed_texts([chunk.text for chunk in chunks]))
    store = LanceDBVectorStore(tmp_path / "vector.lancedb")

    asyncio.run(store.upsert(chunks, vectors))
    query_vector = asyncio.run(provider.embed_texts(["vector similarity"]))[0]
    results = asyncio.run(
        store.search(RetrievalQuery(query="vector similarity", retrieval_mode="vector"), query_vector)
    )

    assert results
    assert results[0].retrieval_mode == "vector"
    assert results[0].result_id.startswith("lancedb::")

    reopened = LanceDBVectorStore(tmp_path / "vector.lancedb")
    reopened_results = asyncio.run(
        reopened.search(RetrievalQuery(query="vector similarity", retrieval_mode="vector"), query_vector)
    )

    assert reopened_results
    assert reopened_results[0].chunk_id == results[0].chunk_id


def _chunks():
    text = """---
id: "concept.vector-test"
title: "Vector Test"
type: "concept"
domain: ["agents", "retrieval"]
audience: ["engineer"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
tags: ["retrieval"]
related: []
---

# Vector Test

Hybrid retrieval combines lexical search and vector similarity with reciprocal rank fusion.
"""
    document = MarkdownDocumentParser().parse(ContentObject(ContentObjectRef("file:///tmp/vector.md"), text))
    return chunks_for_document(document)
