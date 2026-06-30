"""Machine-readable runtime capabilities for agent consumers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date
from typing import Any

from agentic_book.application.evaluation_profiles import (
    list_retrieval_eval_matrix_rows,
    list_retrieval_eval_profiles,
    resolve_retrieval_eval_row,
)


def build_capabilities_manifest() -> dict[str, Any]:
    return {
        "name": "Agentic Book",
        "retrieval_modes": ["lexical", "vector", "hybrid", "fusion"],
        "embedding_provider": "local-hashing",
        "vector_store": "in-memory",
        "storage_backend": "filesystem",
        "index_backend": "json+lexical+local-vector",
        "mcp": {
            "tools": ["search", "fusion_search", "get_document", "corpus_manifest"],
            "resources": ["agentic-book://manifest", "agentic-book://documents/{document_id}"],
            "prompts": ["summarize_with_citations", "compare_concepts"],
            "search_abstention": {
                "parameter": "min_score",
                "reasons": ["no_results", "below_min_score"],
            },
        },
        "retrieval_eval_profiles": _retrieval_eval_profiles(),
        "retrieval_eval_matrix_rows": _retrieval_eval_matrix_rows(),
        "cloud_ready_boundaries": {
            "content_object_store": "ContentObjectStore port can be backed by filesystem or S3.",
            "corpus_index_store": "CorpusIndexStore port can be backed by local JSON or managed storage.",
            "embedding_provider": "EmbeddingProvider port can be backed by local hashing, hosted embeddings, or Bedrock/OpenAI.",
            "vector_store": "VectorStore port can be backed by in-memory local search or OpenSearch/Qdrant/LanceDB.",
        },
    }


def _retrieval_eval_profiles() -> list[dict[str, Any]]:
    return [_jsonable(profile) for profile in list_retrieval_eval_profiles()]


def _retrieval_eval_matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list_retrieval_eval_matrix_rows():
        resolved = resolve_retrieval_eval_row(row)
        rows.append(
            {
                "row": row.name,
                "profile": row.profile,
                "retrieval_mode": resolved.retrieval_mode,
                "min_hit_rate": resolved.min_hit_rate,
                "min_mrr": resolved.min_mrr,
                "min_unanswerable_success": resolved.min_unanswerable_success,
                "min_score": resolved.min_score,
            }
        )
    return rows


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))  # type: ignore[arg-type]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    return value
