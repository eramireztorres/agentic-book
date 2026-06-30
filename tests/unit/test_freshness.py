import asyncio
import json
from datetime import date
from pathlib import Path

import pytest

from agentic_book.application.freshness import BuildStaleReport, ProposeDocumentationUpdate
from agentic_book.domain.models import Document, DocumentMetadata


def _metadata(
    document_id: str, title: str, review_after: date | None, change_frequency: str | None = "high"
) -> DocumentMetadata:
    return DocumentMetadata(
        id=document_id,
        title=title,
        type="concept",
        domain=["agents"],
        audience=["engineer"],
        maturity="production",
        status="reviewed",
        last_reviewed=date(2026, 6, 30),
        source_quality="curated",
        source_type="official",
        source_urls=["https://example.com/docs"],
        last_checked=date(2026, 6, 30),
        review_after=review_after,
        change_frequency=change_frequency,  # type: ignore[arg-type]
    )


def _document(
    document_id: str, title: str, review_after: date | None, change_frequency: str | None = "high"
) -> Document:
    return Document(
        metadata=_metadata(document_id, title, review_after, change_frequency),
        body="Body",
        source_uri=f"content/{document_id}.md",
    )


class FakeRepository:
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    async def list_documents(self, layer: str | None = None) -> list[Document]:
        return self._documents

    async def get_document(self, document_id: str) -> Document | None:
        return next((document for document in self._documents if document.metadata.id == document_id), None)


def test_build_stale_report_flags_overdue_and_missing_review_after() -> None:
    repository = FakeRepository(
        [
            _document("concept.current", "Current", date(2026, 7, 1), "medium"),
            _document("concept.old", "Old", date(2026, 6, 1), "high"),
            _document("concept.missing", "Missing", None, None),
        ]
    )

    report = asyncio.run(BuildStaleReport(repository).run(today=date(2026, 6, 30)))

    assert report.checked == 3
    assert [item.document_id for item in report.stale] == ["concept.old", "concept.missing"]
    assert report.stale[0].days_overdue == 29
    assert report.stale[1].reason == "missing review_after"


def test_propose_documentation_update_writes_markdown_and_json(tmp_path: Path) -> None:
    repository = FakeRepository([_document("concept.mcp", "MCP", date(2026, 6, 1))])

    proposal, md_path, json_path = asyncio.run(
        ProposeDocumentationUpdate(repository, tmp_path).run(
            "concept.mcp",
            reason="Upstream protocol changed",
            source_hint="https://example.com/change",
            urgency="high",
            proposed_change="Review transport section.",
            today=date(2026, 6, 30),
        )
    )

    assert proposal.id == "2026-06-30-concept.mcp"
    assert md_path.exists()
    assert json_path.exists()
    assert "Needs human review" not in md_path.read_text()
    data = json.loads(json_path.read_text())
    assert data["status"] == "needs-human-review"
    assert data["source_hint"] == "https://example.com/change"


def test_propose_documentation_update_rejects_invalid_urgency(tmp_path: Path) -> None:
    repository = FakeRepository([_document("concept.mcp", "MCP", date(2026, 6, 1))])

    with pytest.raises(ValueError, match="urgency"):
        asyncio.run(ProposeDocumentationUpdate(repository, tmp_path).run("concept.mcp", reason="x", urgency="urgent"))
