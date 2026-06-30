"""Ingestion planning and persistence use case."""

from __future__ import annotations

import hashlib

from agentic_book.application.chunking import chunks_for_document
from agentic_book.domain.errors import AgenticBookError
from agentic_book.domain.models import (
    Chunk,
    Document,
    DocumentIngestionRecord,
    IngestionManifest,
    IngestionReport,
    IngestionState,
    ValidationIssue,
)
from agentic_book.domain.ports import ContentObjectStore, CorpusIndexStore, MarkdownParser


class IngestCorpus:
    def __init__(
        self,
        store: ContentObjectStore,
        parser: MarkdownParser,
        index_store: CorpusIndexStore | None = None,
    ) -> None:
        self._store = store
        self._parser = parser
        self._index_store = index_store

    async def run(self, prefix: str = "", layer: str = "canonical", dry_run: bool = True) -> IngestionReport:
        refs = await self._store.list_objects(prefix=prefix, layer=layer)
        previous_state = await self._read_previous_state(dry_run=dry_run)
        previous_documents, previous_chunks = await self._read_previous_index(dry_run=dry_run)
        previous_by_uri = {record.source_uri: record for record in previous_state.documents}
        previous_documents_by_id = {document.metadata.id: document for document in previous_documents}
        previous_chunks_by_document_id = _chunks_by_document_id(previous_chunks)

        issues: list[ValidationIssue] = []
        documents: list[Document] = []
        chunks: list[Chunk] = []
        state_records: list[DocumentIngestionRecord] = []
        current_uris: set[str] = set()
        changed = 0
        unchanged = 0

        for ref in refs:
            current_uris.add(ref.uri)
            try:
                source = await self._store.get_object(ref)
                source_hash = _sha256(source.text)
                previous_record = previous_by_uri.get(ref.uri)
                if previous_record is not None and previous_record.source_hash == source_hash:
                    previous_document = previous_documents_by_id.get(previous_record.document_id)
                    previous_document_chunks = previous_chunks_by_document_id.get(previous_record.document_id)
                    if previous_document is not None and previous_document_chunks is not None:
                        documents.append(previous_document)
                        chunks.extend(previous_document_chunks)
                        state_records.append(previous_record)
                        unchanged += 1
                        continue

                document = self._parser.parse(source)
            except AgenticBookError as exc:
                issues.append(ValidationIssue(source_uri=ref.uri, message=str(exc)))
                continue
            documents.append(document)
            document_chunks = chunks_for_document(document)
            chunks.extend(document_chunks)
            state_records.append(
                DocumentIngestionRecord(
                    document_id=document.metadata.id,
                    source_uri=ref.uri,
                    source_hash=source_hash,
                )
            )
            changed += 1

        removed = len({record.source_uri for record in previous_state.documents} - current_uris)
        manifest_uri = None
        if not dry_run and not issues and self._index_store is not None:
            manifest = IngestionManifest(
                schema_version="1",
                storage_backend="filesystem",
                index_backend="json+lexical",
                documents=len(documents),
                chunks=len(chunks),
            )
            state = IngestionState(schema_version="1", documents=state_records)
            manifest_uri = await self._index_store.write(documents, chunks, manifest, state)

        indexed = not dry_run and not issues and self._index_store is not None
        return IngestionReport(
            documents_seen=len(refs),
            chunks_planned=len(chunks),
            dry_run=dry_run,
            issues=issues,
            documents_indexed=len(documents) if indexed else 0,
            chunks_indexed=len(chunks) if indexed else 0,
            documents_changed=changed,
            documents_unchanged=unchanged,
            documents_removed=removed,
            manifest_uri=manifest_uri,
        )

    async def _read_previous_state(self, *, dry_run: bool) -> IngestionState:
        if self._index_store is None:
            return IngestionState(schema_version="1")
        try:
            state = await self._index_store.read_ingestion_state()
        except FileNotFoundError:
            return IngestionState(schema_version="1")
        return state or IngestionState(schema_version="1")

    async def _read_previous_index(self, *, dry_run: bool) -> tuple[list[Document], list[Chunk]]:
        if dry_run or self._index_store is None:
            return [], []
        try:
            return await self._index_store.read_documents(), await self._index_store.read_chunks()
        except FileNotFoundError:
            return [], []


def _chunks_by_document_id(chunks: list[Chunk]) -> dict[str, list[Chunk]]:
    grouped: dict[str, list[Chunk]] = {}
    for chunk in chunks:
        grouped.setdefault(chunk.document_id, []).append(chunk)
    return grouped


def _sha256(text: str) -> str:
    normalized = "\n".join(line.rstrip() for line in text.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
