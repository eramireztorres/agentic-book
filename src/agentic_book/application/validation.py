"""Corpus validation use case."""

from __future__ import annotations

from agentic_book.domain.errors import AgenticBookError
from agentic_book.domain.metadata_schema import freshness_missing_fields
from agentic_book.domain.models import ValidationIssue, ValidationReport
from agentic_book.domain.ports import ContentObjectStore, MarkdownParser
from agentic_book.infrastructure.markdown.frontmatter import split_frontmatter


class ValidateCorpus:
    def __init__(self, store: ContentObjectStore, parser: MarkdownParser) -> None:
        self._store = store
        self._parser = parser

    async def run(
        self,
        prefix: str = "",
        layer: str = "canonical",
        strict_related: bool = True,
        strict_freshness: bool = False,
    ) -> ValidationReport:
        refs = await self._store.list_objects(prefix=prefix, layer=layer)
        issues: list[ValidationIssue] = []
        document_ids: dict[str, str] = {}
        related_by_doc: dict[str, list[str]] = {}

        for ref in refs:
            try:
                source = await self._store.get_object(ref)
                raw_metadata, _ = split_frontmatter(source.text)
                missing_freshness = freshness_missing_fields(raw_metadata)
                if missing_freshness and not strict_freshness:
                    issues.append(
                        ValidationIssue(
                            source_uri=ref.uri,
                            message="Missing freshness metadata fields: " + ", ".join(missing_freshness),
                            severity="warning",
                        )
                    )
                document = self._parser.parse(source)
            except AgenticBookError as exc:
                issues.append(ValidationIssue(source_uri=ref.uri, message=str(exc)))
                continue

            existing = document_ids.get(document.metadata.id)
            if existing:
                issues.append(
                    ValidationIssue(
                        source_uri=ref.uri,
                        message=f"Duplicate document id {document.metadata.id!r}; already used by {existing}",
                    )
                )
            else:
                document_ids[document.metadata.id] = ref.uri
            related_by_doc[document.metadata.id] = document.metadata.related

        if strict_related:
            known_ids = set(document_ids)
            for doc_id, related_ids in related_by_doc.items():
                for related_id in related_ids:
                    if related_id not in known_ids:
                        issues.append(
                            ValidationIssue(
                                source_uri=document_ids.get(doc_id, doc_id),
                                message=f"Document {doc_id!r} references unknown related id {related_id!r}",
                            )
                        )

        return ValidationReport(documents_checked=len(refs), issues=issues)
