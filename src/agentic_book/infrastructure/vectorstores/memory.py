"""In-memory vector store adapter for local deterministic retrieval."""

from __future__ import annotations

import math

from agentic_book.domain.models import Chunk, RetrievalQuery, RetrievalResult


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._items: dict[str, tuple[Chunk, list[float]]] = {}

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        for chunk, vector in zip(chunks, vectors, strict=True):
            self._items[chunk.id] = (chunk, vector)

    async def search(self, query: RetrievalQuery, query_vector: list[float]) -> list[RetrievalResult]:
        scored: list[RetrievalResult] = []
        for chunk, vector in self._items.values():
            if not _matches_filters(chunk, query):
                continue
            score = _cosine_similarity(query_vector, vector)
            if score <= 0:
                continue
            scored.append(
                RetrievalResult(
                    result_id=f"vector::{chunk.id}",
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    title=chunk.metadata.title,
                    score=score,
                    source_uri=chunk.source_uri,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    retrieval_mode="vector",
                    section_heading=chunk.section_heading,
                    why_retrieved="Matched deterministic local vector similarity",
                )
            )
        scored.sort(key=lambda result: (-result.score, result.document_id, result.chunk_id))
        return scored[: query.top_k]


def _matches_filters(chunk: Chunk, query: RetrievalQuery) -> bool:
    metadata = chunk.metadata
    filters = query.filters
    if filters.layer and metadata.layer not in filters.layer:
        return False
    if filters.type and metadata.type not in filters.type:
        return False
    if filters.maturity and metadata.maturity not in filters.maturity:
        return False
    if filters.status and metadata.status not in filters.status:
        return False
    if filters.domain and not set(filters.domain).intersection(metadata.domain):
        return False
    if filters.audience and not set(filters.audience).intersection(metadata.audience):
        return False
    return not (filters.tags and not set(filters.tags).intersection(metadata.tags))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
