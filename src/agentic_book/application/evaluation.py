"""Retrieval evaluation use cases."""

from __future__ import annotations

from agentic_book.domain.models import (
    RetrievalEvalCase,
    RetrievalEvalProfileName,
    RetrievalEvalReport,
    RetrievalEvalResult,
    RetrievalMode,
    RetrievalQuery,
)
from agentic_book.domain.ports import RetrievalEngine


class EvaluateRetrieval:
    def __init__(
        self,
        retrieval_engine: RetrievalEngine,
        retrieval_mode: RetrievalMode = "lexical",
        min_score: float = 0.0,
        profile: RetrievalEvalProfileName = "custom",
    ) -> None:
        self._retrieval_engine = retrieval_engine
        self._retrieval_mode = retrieval_mode
        self._min_score = min_score
        self._profile = profile

    async def run(self, cases: list[RetrievalEvalCase]) -> RetrievalEvalReport:
        results: list[RetrievalEvalResult] = []
        for case in cases:
            query = RetrievalQuery(query=case.query, top_k=case.top_k, retrieval_mode=self._retrieval_mode)
            retrieval_results = await self._retrieval_engine.run(query)
            max_score = retrieval_results[0].score if retrieval_results else 0.0
            abstained = not retrieval_results or max_score < self._min_score
            retrieved_document_ids = (
                [] if abstained else _unique_document_ids([result.document_id for result in retrieval_results])
            )
            reciprocal_rank = _reciprocal_rank(retrieved_document_ids, case.expected_document_ids)
            hit = reciprocal_rank > 0 if case.answerable else not retrieved_document_ids
            results.append(
                RetrievalEvalResult(
                    case_id=case.id,
                    query=case.query,
                    expected_document_ids=case.expected_document_ids,
                    retrieved_document_ids=retrieved_document_ids,
                    hit=hit,
                    reciprocal_rank=reciprocal_rank,
                    top_k=case.top_k,
                    abstained=abstained,
                    max_score=max_score,
                )
            )

        answerable_results = [result for result in results if result.expected_document_ids]
        unanswerable_results = [result for result in results if not result.expected_document_ids]
        return RetrievalEvalReport(
            profile=self._profile,
            cases=len(results),
            answerable_cases=len(answerable_results),
            unanswerable_cases=len(unanswerable_results),
            hit_rate=_mean([1.0 if result.hit else 0.0 for result in answerable_results]),
            mean_reciprocal_rank=_mean([result.reciprocal_rank for result in answerable_results]),
            unanswerable_success_rate=_mean([1.0 if result.hit else 0.0 for result in unanswerable_results]),
            retrieval_mode=self._retrieval_mode,
            min_score=self._min_score,
            abstention_rate=_mean([1.0 if result.abstained else 0.0 for result in results]),
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
