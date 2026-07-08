"""JSON retrieval evaluation dataset loader."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any

from agentic_book.domain.models import FusionEvalCase, FusionEvalReport, RetrievalEvalCase, RetrievalEvalReport


def load_retrieval_eval_cases(path: Path) -> list[RetrievalEvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {path}")
    return [_case_from_mapping(item, path) for item in data]


def _case_from_mapping(data: Any, path: Path) -> RetrievalEvalCase:
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object entries in {path}")
    expected_document_ids = data.get("expected_document_ids", [])
    tags = data.get("tags", [])
    if not isinstance(expected_document_ids, list) or not all(isinstance(item, str) for item in expected_document_ids):
        raise ValueError("expected_document_ids must be a list of strings")
    if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
        raise ValueError("tags must be a list of strings")
    return RetrievalEvalCase(
        id=_required_string(data, "id"),
        query=_required_string(data, "query"),
        expected_document_ids=expected_document_ids,
        top_k=int(data.get("top_k", 5)),
        tags=tags,
        notes=data.get("notes"),
    )


def load_fusion_eval_cases(path: Path) -> list[FusionEvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {path}")
    return [_fusion_case_from_mapping(item, path) for item in data]


def _fusion_case_from_mapping(data: Any, path: Path) -> FusionEvalCase:
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object entries in {path}")
    queries = data.get("queries", [])
    expected_document_ids = data.get("expected_document_ids", [])
    tags = data.get("tags", [])
    if not isinstance(queries, list) or not all(isinstance(item, str) and item.strip() for item in queries):
        raise ValueError("queries must be a non-empty list of strings")
    if not queries:
        raise ValueError("queries must not be empty")
    if not isinstance(expected_document_ids, list) or not all(isinstance(item, str) for item in expected_document_ids):
        raise ValueError("expected_document_ids must be a list of strings")
    if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
        raise ValueError("tags must be a list of strings")
    return FusionEvalCase(
        id=_required_string(data, "id"),
        queries=[item.strip() for item in queries],
        expected_document_ids=expected_document_ids,
        top_k_per_query=int(data.get("top_k_per_query", 8)),
        final_top_k=int(data.get("final_top_k", 5)),
        rrf_k=int(data.get("rrf_k", 60)),
        tags=tags,
        notes=data.get("notes"),
    )


def _required_string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def write_fusion_eval_report(report: FusionEvalReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_retrieval_eval_report(report: RetrievalEvalReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_retrieval_eval_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_retrieval_eval_matrix_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_retrieval_eval_matrix_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


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
