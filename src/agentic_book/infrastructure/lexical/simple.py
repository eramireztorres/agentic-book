"""Simple lexical index baseline."""

from __future__ import annotations

import math
import re
from collections import Counter

from agentic_book.domain.models import Chunk, RetrievalFilters, RetrievalQuery, RetrievalResult

TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*")


class SimpleLexicalIndex:
    def __init__(self, chunks: list[Chunk] | None = None) -> None:
        self._chunks = chunks or []

    async def upsert(self, chunks: list[Chunk]) -> None:
        known = {chunk.id: chunk for chunk in self._chunks}
        for chunk in chunks:
            known[chunk.id] = chunk
        self._chunks = list(known.values())

    async def search(self, query: RetrievalQuery) -> list[RetrievalResult]:
        query_terms = tokenize(query.query)
        if not query_terms:
            return []
        document_frequency = _document_frequency(self._chunks)
        total_chunks = max(len(self._chunks), 1)

        scored: list[RetrievalResult] = []
        for chunk in self._chunks:
            if not _matches_filters(chunk, query.filters):
                continue
            score = _score_chunk(chunk, query_terms, document_frequency, total_chunks)
            if score <= 0:
                continue
            scored.append(
                RetrievalResult(
                    result_id=f"lexical::{chunk.id}",
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    title=chunk.metadata.title,
                    score=score,
                    source_uri=chunk.source_uri,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    retrieval_mode="lexical",
                    section_heading=chunk.section_heading,
                    why_retrieved="Matched lexical query terms: " + ", ".join(sorted(set(query_terms))),
                )
            )
        scored.sort(key=lambda result: (-result.score, result.document_id, result.chunk_id))
        return scored[: query.top_k]


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _document_frequency(chunks: list[Chunk]) -> Counter[str]:
    frequency: Counter[str] = Counter()
    for chunk in chunks:
        frequency.update(set(tokenize(chunk.text)))
    return frequency


def _score_chunk(
    chunk: Chunk,
    query_terms: list[str],
    document_frequency: Counter[str],
    total_chunks: int,
) -> float:
    term_counts = Counter(tokenize(chunk.text))
    score = 0.0
    for term in query_terms:
        count = term_counts.get(term, 0)
        if count == 0:
            continue
        idf = math.log((1 + total_chunks) / (1 + document_frequency.get(term, 0))) + 1
        score += (1 + math.log(count)) * idf
    if chunk.kind == "section":
        score *= 1.05
    return score


def _matches_filters(chunk: Chunk, filters: RetrievalFilters) -> bool:
    metadata = chunk.metadata
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
