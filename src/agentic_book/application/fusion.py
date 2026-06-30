"""Rank fusion helpers."""

from __future__ import annotations

from dataclasses import replace

from agentic_book.domain.models import RetrievalQuery, RetrievalResult
from agentic_book.domain.ports import LexicalIndex


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return scores


class FusionSearchCorpus:
    def __init__(self, lexical_index: LexicalIndex) -> None:
        self._lexical_index = lexical_index

    async def run(
        self,
        queries: list[str],
        base_query: RetrievalQuery,
        top_k_per_query: int = 8,
        final_top_k: int = 10,
        rrf_k: int = 60,
    ) -> list[RetrievalResult]:
        clean_queries = [query.strip() for query in queries if query.strip()]
        if not clean_queries:
            return []

        rankings: list[list[str]] = []
        best_result_by_chunk: dict[str, RetrievalResult] = {}
        source_queries_by_chunk: dict[str, list[str]] = {}

        for query_text in clean_queries:
            query = RetrievalQuery(
                query=query_text,
                top_k=top_k_per_query,
                retrieval_mode=base_query.retrieval_mode,
                filters=base_query.filters,
            )
            results = await self._lexical_index.search(query)
            ranking = [result.chunk_id for result in results]
            rankings.append(ranking)
            for result in results:
                current = best_result_by_chunk.get(result.chunk_id)
                if current is None or result.score > current.score:
                    best_result_by_chunk[result.chunk_id] = result
                source_queries_by_chunk.setdefault(result.chunk_id, []).append(query_text)

        fused_scores = reciprocal_rank_fusion(rankings, k=rrf_k)
        fused_results: list[RetrievalResult] = []
        for chunk_id, fused_score in fused_scores.items():
            original = best_result_by_chunk[chunk_id]
            source_queries = sorted(set(source_queries_by_chunk.get(chunk_id, [])))
            fused_results.append(
                replace(
                    original,
                    result_id=f"fusion::{chunk_id}",
                    score=fused_score,
                    retrieval_mode="fusion",
                    why_retrieved="Contributed by subqueries: " + "; ".join(source_queries),
                )
            )
        fused_results.sort(key=lambda result: (-result.score, result.document_id, result.chunk_id))
        return fused_results[:final_top_k]
