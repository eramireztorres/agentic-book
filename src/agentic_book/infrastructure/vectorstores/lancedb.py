"""LanceDB vector store adapter for local persistent vector retrieval."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from agentic_book.domain.models import Chunk, DocumentMetadata, RetrievalQuery, RetrievalResult


class LanceDBVectorStore:
    def __init__(self, db_path: Path, table_name: str = "chunks") -> None:
        self._db_path = db_path
        self._table_name = table_name

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        lancedb = _import_lancedb()
        self._db_path.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(self._db_path))
        if not chunks:
            db.drop_table(self._table_name, ignore_missing=True)
            return
        rows = [_row_for_chunk(chunk, vector) for chunk, vector in zip(chunks, vectors, strict=True)]
        db.create_table(self._table_name, data=rows, mode="overwrite")

    async def search(self, query: RetrievalQuery, query_vector: list[float]) -> list[RetrievalResult]:
        lancedb = _import_lancedb()
        db = lancedb.connect(str(self._db_path))
        if self._table_name not in set(db.list_tables().tables):
            return []
        table = db.open_table(self._table_name)
        # Fetch extra candidates because metadata filters are applied in Python to
        # keep the adapter independent from LanceDB SQL escaping details.
        limit = max(query.top_k * 10, query.top_k, 20)
        rows = table.search(query_vector).limit(limit).to_list()
        results: list[RetrievalResult] = []
        for row in rows:
            chunk = _chunk_from_row(row)
            if not _matches_filters(chunk, query):
                continue
            distance = float(row.get("_distance", 0.0))
            score = 1.0 / (1.0 + max(distance, 0.0))
            if score <= 0:
                continue
            results.append(
                RetrievalResult(
                    result_id=f"lancedb::{chunk.id}",
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    title=chunk.metadata.title,
                    score=score,
                    source_uri=chunk.source_uri,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    retrieval_mode="vector",
                    section_heading=chunk.section_heading,
                    why_retrieved="Matched LanceDB local vector similarity",
                )
            )
            if len(results) >= query.top_k:
                break
        return results


def _import_lancedb() -> Any:
    try:
        import lancedb
    except ImportError as exc:
        raise RuntimeError('LanceDB vector store requires `python -m pip install -e ".[vector-lancedb]"`.') from exc
    return lancedb


def _row_for_chunk(chunk: Chunk, vector: list[float]) -> dict[str, Any]:
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "source_uri": chunk.source_uri,
        "text": chunk.text,
        "kind": chunk.kind,
        "section_id": chunk.section_id,
        "section_heading": chunk.section_heading,
        "content_hash": chunk.content_hash,
        "metadata_json": json.dumps(_jsonable(asdict(chunk.metadata)), sort_keys=True),
        "vector": vector,
    }


def _chunk_from_row(row: dict[str, Any]) -> Chunk:
    metadata = _metadata_from_json(str(row["metadata_json"]))
    return Chunk(
        id=str(row["id"]),
        document_id=str(row["document_id"]),
        text=str(row["text"]),
        kind=row.get("kind", "document"),
        source_uri=str(row["source_uri"]),
        metadata=metadata,
        section_id=_optional_string(row.get("section_id")),
        section_heading=_optional_string(row.get("section_heading")),
        content_hash=_optional_string(row.get("content_hash")),
    )


def _metadata_from_json(value: str) -> DocumentMetadata:
    data = json.loads(value)
    for key in ("last_reviewed", "last_checked", "review_after"):
        if data.get(key):
            data[key] = date.fromisoformat(data[key])
    return DocumentMetadata(**data)


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _jsonable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    return value


def _matches_filters(chunk: Chunk, query: RetrievalQuery) -> bool:
    metadata = chunk.metadata
    filters = query.filters
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
