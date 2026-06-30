import asyncio

from agentic_book.application.chunking import chunks_for_document
from agentic_book.application.retrieve import SearchCorpus
from agentic_book.domain.models import ContentObject, ContentObjectRef, RetrievalQuery
from agentic_book.infrastructure.embeddings.hashing import HashingEmbeddingProvider
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.vectorstores.memory import InMemoryVectorStore


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


def test_hashing_embedding_provider_is_deterministic() -> None:
    provider = HashingEmbeddingProvider(dimensions=16)

    first = asyncio.run(provider.embed_texts(["hybrid retrieval"]))
    second = asyncio.run(provider.embed_texts(["hybrid retrieval"]))

    assert first == second
    assert len(first[0]) == 16


def test_vector_search_returns_results() -> None:
    chunks = _chunks()
    provider = HashingEmbeddingProvider()
    store = InMemoryVectorStore()
    vectors = asyncio.run(provider.embed_texts([chunk.text for chunk in chunks]))
    asyncio.run(store.upsert(chunks, vectors))
    search = SearchCorpus(SimpleLexicalIndex(chunks), provider, store)

    results = asyncio.run(search.run(RetrievalQuery(query="vector similarity", retrieval_mode="vector", top_k=3)))

    assert results
    assert results[0].retrieval_mode == "vector"


def test_hybrid_search_fuses_lexical_and_vector_results() -> None:
    chunks = _chunks()
    provider = HashingEmbeddingProvider()
    store = InMemoryVectorStore()
    vectors = asyncio.run(provider.embed_texts([chunk.text for chunk in chunks]))
    asyncio.run(store.upsert(chunks, vectors))
    search = SearchCorpus(SimpleLexicalIndex(chunks), provider, store)

    results = asyncio.run(search.run(RetrievalQuery(query="hybrid retrieval", retrieval_mode="hybrid", top_k=3)))

    assert results
    assert results[0].retrieval_mode == "hybrid"
    assert "Fused retrieval modes" in (results[0].why_retrieved or "")
