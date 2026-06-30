"""Local JSON persistence for documents, chunks, and ingestion manifest."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from agentic_book.domain.models import (
    Chunk,
    Document,
    DocumentIngestionRecord,
    DocumentMetadata,
    IngestionManifest,
    IngestionState,
    Section,
)


class LocalJsonCorpusIndexStore:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._documents_path = data_dir / "documents.json"
        self._chunks_path = data_dir / "chunks.json"
        self._manifest_path = data_dir / "ingestion_manifest.json"
        self._state_path = data_dir / "ingestion_state.json"

    async def write(
        self,
        documents: list[Document],
        chunks: list[Chunk],
        manifest: IngestionManifest,
        state: IngestionState | None = None,
    ) -> str:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(self._documents_path, [document_to_dict(document) for document in documents])
        self._write_json(self._chunks_path, [chunk_to_dict(chunk) for chunk in chunks])
        self._write_json(self._manifest_path, asdict(manifest))
        if state is not None:
            self._write_json(self._state_path, ingestion_state_to_dict(state))
        return self._manifest_path.resolve().as_uri()

    async def read_chunks(self) -> list[Chunk]:
        return [chunk_from_dict(item) for item in self._read_json_list(self._chunks_path)]

    async def read_documents(self) -> list[Document]:
        return [document_from_dict(item) for item in self._read_json_list(self._documents_path)]

    async def read_manifest(self) -> IngestionManifest:
        if not self._manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self._manifest_path}. Run `agentic-book ingest` first.")
        data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in {self._manifest_path}")
        return IngestionManifest(**data)

    async def read_ingestion_state(self) -> IngestionState | None:
        if not self._state_path.exists():
            return None
        data = json.loads(self._state_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in {self._state_path}")
        return ingestion_state_from_dict(data)

    async def list_documents(self, layer: str | None = None) -> list[Document]:
        documents = await self.read_documents()
        if layer is None:
            return documents
        return [document for document in documents if document.metadata.layer == layer]

    async def get_document(self, document_id: str) -> Document | None:
        for document in await self.read_documents():
            if document.metadata.id == document_id:
                return document
        return None

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _read_json_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            raise FileNotFoundError(f"Index file not found: {path}. Run `agentic-book ingest` first.")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON list in {path}")
        return data


def document_to_dict(document: Document) -> dict[str, Any]:
    return {
        "metadata": metadata_to_dict(document.metadata),
        "body": document.body,
        "source_uri": document.source_uri,
        "sections": [section_to_dict(section) for section in document.sections],
    }


def document_from_dict(data: dict[str, Any]) -> Document:
    return Document(
        metadata=metadata_from_dict(data["metadata"]),
        body=data["body"],
        source_uri=data["source_uri"],
        sections=[section_from_dict(item) for item in data.get("sections", [])],
    )


def chunk_to_dict(chunk: Chunk) -> dict[str, Any]:
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "text": chunk.text,
        "kind": chunk.kind,
        "source_uri": chunk.source_uri,
        "metadata": metadata_to_dict(chunk.metadata),
        "section_id": chunk.section_id,
        "section_heading": chunk.section_heading,
        "content_hash": chunk.content_hash,
    }


def chunk_from_dict(data: dict[str, Any]) -> Chunk:
    return Chunk(
        id=data["id"],
        document_id=data["document_id"],
        text=data["text"],
        kind=data["kind"],
        source_uri=data["source_uri"],
        metadata=metadata_from_dict(data["metadata"]),
        section_id=data.get("section_id"),
        section_heading=data.get("section_heading"),
        content_hash=data.get("content_hash"),
    )


def metadata_to_dict(metadata: DocumentMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in ("last_reviewed", "last_checked", "review_after"):
        value = data.get(field_name)
        if isinstance(value, date):
            data[field_name] = value.isoformat()
    return data


def metadata_from_dict(data: dict[str, Any]) -> DocumentMetadata:
    copied = dict(data)
    for field_name in ("last_reviewed", "last_checked", "review_after"):
        if isinstance(copied.get(field_name), str):
            copied[field_name] = date.fromisoformat(copied[field_name])
    return DocumentMetadata(**copied)


def section_to_dict(section: Section) -> dict[str, Any]:
    data = asdict(section)
    data["heading_path"] = list(section.heading_path)
    return data


def section_from_dict(data: dict[str, Any]) -> Section:
    copied = dict(data)
    copied["heading_path"] = tuple(copied.get("heading_path", []))
    return Section(**copied)


def ingestion_state_to_dict(state: IngestionState) -> dict[str, Any]:
    return {
        "schema_version": state.schema_version,
        "documents": [asdict(record) for record in state.documents],
    }


def ingestion_state_from_dict(data: dict[str, Any]) -> IngestionState:
    records = [DocumentIngestionRecord(**item) for item in data.get("documents", [])]
    return IngestionState(schema_version=data["schema_version"], documents=records)
