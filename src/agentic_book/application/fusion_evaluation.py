"""Fusion retrieval evaluation use cases."""

from __future__ import annotations

from agentic_book.application.fusion import FusionSearchCorpus
from agentic_book.domain.models import FusionEvalCase, FusionEvalReport, FusionEvalResult, RetrievalQuery


class EvaluateFusionRetrieval:
    def __init__(self, fusion_search: FusionSearchCorpus) -> None:
        self._fusion_search = fusion_search

    async def run(self, cases: list[FusionEvalCase]) -> FusionEvalReport:
        results: list[FusionEvalResult] = []
        for case in cases:
            base_query = RetrievalQuery(query=" | ".join(case.queries), retrieval_mode="lexical")
            retrieval_results = await self._fusion_search.run(
                case.queries,
                base_query=base_query,
                top_k_per_query=case.top_k_per_query,
                final_top_k=case.final_top_k,
                rrf_k=case.rrf_k,
            )
            max_score = retrieval_results[0].score if retrieval_results else 0.0
            retrieved_document_ids = _unique_document_ids([result.document_id for result in retrieval_results])
            reciprocal_rank = _reciprocal_rank(retrieved_document_ids, case.expected_document_ids)
            hit = reciprocal_rank > 0 if case.answerable else not retrieved_document_ids
            results.append(
                FusionEvalResult(
                    case_id=case.id,
                    queries=case.queries,
                    expected_document_ids=case.expected_document_ids,
                    retrieved_document_ids=retrieved_document_ids,
                    hit=hit,
                    reciprocal_rank=reciprocal_rank,
                    final_top_k=case.final_top_k,
                    max_score=max_score,
                )
            )

        answerable_results = [result for result in results if result.expected_document_ids]
        unanswerable_results = [result for result in results if not result.expected_document_ids]
        return FusionEvalReport(
            cases=len(results),
            answerable_cases=len(answerable_results),
            unanswerable_cases=len(unanswerable_results),
            hit_rate=_mean([1.0 if result.hit else 0.0 for result in answerable_results]),
            mean_reciprocal_rank=_mean([result.reciprocal_rank for result in answerable_results]),
            unanswerable_success_rate=_mean([1.0 if result.hit else 0.0 for result in unanswerable_results]),
            results=results,
        )


def _unique_document_ids(document_ids: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for document_id in document_ids:
        if document_id in seen:
            continue
        seen.add(document_id)
        unique.append(document_id)
    return unique


def _reciprocal_rank(retrieved_document_ids: list[str], expected_document_ids: list[str]) -> float:
    expected = set(expected_document_ids)
    for index, document_id in enumerate(retrieved_document_ids, start=1):
        if document_id in expected:
            return 1.0 / index
    return 0.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)
