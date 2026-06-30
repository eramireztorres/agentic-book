"""Freshness and local update proposal use cases."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from agentic_book.domain.errors import DocumentNotFoundError
from agentic_book.domain.models import Document, DocumentationUpdateProposal, StaleDocument, StaleReport
from agentic_book.domain.ports import DocumentRepository

_PRIORITY = {"volatile": 0, "high": 1, "medium": 2, "low": 3, None: 4}


class BuildStaleReport:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    async def run(self, today: date | None = None) -> StaleReport:
        current_date = today or date.today()
        documents = await self._repository.list_documents(layer="canonical")
        stale: list[StaleDocument] = []
        for document in documents:
            item = _stale_document(document, today=current_date)
            if item is not None:
                stale.append(item)
        stale.sort(
            key=lambda item: (_PRIORITY.get(item.change_frequency, 4), -(item.days_overdue or 0), item.document_id)
        )
        return StaleReport(checked=len(documents), stale=stale)


class ProposeDocumentationUpdate:
    def __init__(self, repository: DocumentRepository, proposals_dir: Path) -> None:
        self._repository = repository
        self._proposals_dir = proposals_dir

    async def run(
        self,
        document_id: str,
        reason: str,
        source_hint: str | None = None,
        urgency: str = "medium",
        proposed_change: str | None = None,
        today: date | None = None,
    ) -> tuple[DocumentationUpdateProposal, Path, Path]:
        if urgency not in {"low", "medium", "high"}:
            raise ValueError("urgency must be one of: low, medium, high")
        document = await self._repository.get_document(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document not found: {document_id}")
        created_on = today or date.today()
        safe_date = created_on.isoformat()
        proposal = DocumentationUpdateProposal(
            id=f"{safe_date}-{document_id}",
            document_id=document_id,
            reason=reason,
            status="needs-human-review",
            created_on=created_on,
            source_hint=source_hint,
            urgency=urgency,  # type: ignore[arg-type]
            proposed_change=proposed_change,
        )
        output_dir = self._proposals_dir / "documentation-updates"
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{proposal.id}.json"
        md_path = output_dir / f"{proposal.id}.md"
        json_path.write_text(json.dumps(_jsonable(asdict(proposal)), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_proposal_markdown(proposal, document), encoding="utf-8")
        return proposal, md_path, json_path


def _stale_document(document: Document, today: date) -> StaleDocument | None:
    metadata = document.metadata
    if metadata.review_after is None:
        return StaleDocument(
            document_id=metadata.id,
            title=metadata.title,
            source_uri=document.source_uri,
            review_after=None,
            change_frequency=metadata.change_frequency,
            days_overdue=None,
            reason="missing review_after",
        )
    if metadata.review_after >= today:
        return None
    return StaleDocument(
        document_id=metadata.id,
        title=metadata.title,
        source_uri=document.source_uri,
        review_after=metadata.review_after,
        change_frequency=metadata.change_frequency,
        days_overdue=(today - metadata.review_after).days,
        reason="review_after elapsed",
    )


def _proposal_markdown(proposal: DocumentationUpdateProposal, document: Document) -> str:
    return f"""# Documentation update proposal: {proposal.document_id}

- Status: {proposal.status}
- Created on: {proposal.created_on.isoformat()}
- Urgency: {proposal.urgency}
- Document title: {document.metadata.title}
- Source hint: {proposal.source_hint or "n/a"}

## Reason

{proposal.reason}

## Proposed change

{proposal.proposed_change or "Needs human review."}

## Guardrails

This proposal is not canonical content. A maintainer must review it before changing `content/`.
"""


def _jsonable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
