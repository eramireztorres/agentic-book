import asyncio
from datetime import date

from agentic_book.application.evaluation import EvaluateRetrieval
from agentic_book.domain.models import DocumentMetadata, RetrievalEvalCase, RetrievalQuery, RetrievalResult


class FakeRetrievalEngine:
    def __init__(self, document_ids: list[str]) -> None:
        self._document_ids = document_ids

    async def run(self, query: RetrievalQuery) -> list[RetrievalResult]:
        metadata = DocumentMetadata(
            id="doc",
            title="Doc",
            type="concept",
            domain=["agents"],
            audience=["engineer"],
            maturity="production",
            status="reviewed",
            last_reviewed=date(2026, 6, 30),
            source_quality="curated",
        )
        return [
            RetrievalResult(
                result_id=f"r::{document_id}",
                document_id=document_id,
                chunk_id=f"{document_id}::document",
                title=document_id,
                score=1.0,
                source_uri=f"content/{document_id}.md",
                text="text",
                metadata=metadata,
                retrieval_mode="lexical",
            )
            for document_id in self._document_ids[: query.top_k]
        ]


def test_evaluate_retrieval_computes_hit_rate_mrr_and_unanswerable_success() -> None:
    cases = [
        RetrievalEvalCase(id="hit_first", query="q", expected_document_ids=["doc.a"], top_k=3),
        RetrievalEvalCase(id="hit_second", query="q", expected_document_ids=["doc.b"], top_k=3),
        RetrievalEvalCase(id="unanswerable", query="q", expected_document_ids=[], top_k=3),
    ]

    answerable_report = asyncio.run(EvaluateRetrieval(FakeRetrievalEngine(["doc.a", "doc.b"])).run(cases[:2]))
    unanswerable_report = asyncio.run(EvaluateRetrieval(FakeRetrievalEngine([])).run(cases[2:]))

    assert answerable_report.hit_rate == 1.0
    assert answerable_report.mean_reciprocal_rank == 0.75
    assert unanswerable_report.unanswerable_success_rate == 1.0
    assert unanswerable_report.abstention_rate == 1.0
