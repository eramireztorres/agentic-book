"""Frontmatter schema validation."""

from __future__ import annotations

from datetime import date
from typing import Any

from agentic_book.domain.errors import InvalidMetadataError
from agentic_book.domain.models import (
    ContentLayer,
    DocumentMetadata,
)

DOCUMENT_TYPES: set[str] = {
    "concept",
    "pattern",
    "platform",
    "playbook",
    "case-study",
    "checklist",
    "risk",
    "tool",
    "standard",
    "glossary",
}
MATURITY_VALUES: set[str] = {"experimental", "emerging", "production", "legacy"}
STATUS_VALUES: set[str] = {"draft", "reviewed", "deprecated"}
SOURCE_QUALITY_VALUES: set[str] = {"primary", "curated", "community", "vendor", "internal"}
LAYER_VALUES: set[str] = {"canonical", "wiki"}
SOURCE_TYPE_VALUES: set[str] = {"official", "vendor", "community", "internal", "derived"}
CHANGE_FREQUENCY_VALUES: set[str] = {"low", "medium", "high", "volatile"}
FRESHNESS_FIELDS: tuple[str, ...] = ("source_type", "last_checked", "review_after", "change_frequency")
REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "title",
    "type",
    "domain",
    "audience",
    "maturity",
    "status",
    "last_reviewed",
    "source_quality",
)


def metadata_from_mapping(
    data: dict[str, Any],
    *,
    default_layer: ContentLayer = "canonical",
    strict_freshness: bool = False,
) -> DocumentMetadata:
    """Build validated metadata from parsed frontmatter."""

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise InvalidMetadataError(f"Missing required metadata fields: {', '.join(missing)}")

    doc_type = _expect_choice(data["type"], DOCUMENT_TYPES, "type")
    maturity = _expect_choice(data["maturity"], MATURITY_VALUES, "maturity")
    status = _expect_choice(data["status"], STATUS_VALUES, "status")
    source_quality = _expect_choice(data["source_quality"], SOURCE_QUALITY_VALUES, "source_quality")
    layer = _expect_choice(data.get("layer", default_layer), LAYER_VALUES, "layer")
    _validate_freshness_presence(data, strict=strict_freshness)
    source_type = _optional_choice(data.get("source_type"), SOURCE_TYPE_VALUES, "source_type")
    change_frequency = _optional_choice(data.get("change_frequency"), CHANGE_FREQUENCY_VALUES, "change_frequency")
    source_urls = _expect_string_list(data.get("source_urls", []), "source_urls")
    if source_type is not None and source_type != "internal" and not source_urls:
        raise InvalidMetadataError("Metadata field 'source_urls' is required when source_type is not internal")

    return DocumentMetadata(
        id=_expect_string(data["id"], "id"),
        title=_expect_string(data["title"], "title"),
        type=doc_type,  # type: ignore[arg-type]
        domain=_expect_string_list(data["domain"], "domain"),
        audience=_expect_string_list(data["audience"], "audience"),
        maturity=maturity,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        last_reviewed=_expect_date(data["last_reviewed"], "last_reviewed"),
        source_quality=source_quality,  # type: ignore[arg-type]
        source_urls=source_urls,
        source_type=source_type,  # type: ignore[arg-type]
        upstream_version=_optional_string(data.get("upstream_version"), "upstream_version"),
        last_checked=_optional_date(data.get("last_checked"), "last_checked"),
        review_after=_optional_date(data.get("review_after"), "review_after"),
        change_frequency=change_frequency,  # type: ignore[arg-type]
        supersedes=_expect_string_list(data.get("supersedes", []), "supersedes"),
        superseded_by=_optional_string(data.get("superseded_by"), "superseded_by"),
        tags=_expect_string_list(data.get("tags", []), "tags"),
        related=_expect_string_list(data.get("related", []), "related"),
        layer=layer,  # type: ignore[arg-type]
    )


def _expect_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidMetadataError(f"Metadata field {field!r} must be a non-empty string")
    return value.strip()


def _expect_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise InvalidMetadataError(f"Metadata field {field!r} must be a list of strings")
    return [item.strip() for item in value]


def _expect_choice(value: Any, allowed: set[str], field: str) -> str:
    text = _expect_string(value, field)
    if text not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise InvalidMetadataError(f"Metadata field {field!r} must be one of: {allowed_values}")
    return text


def _expect_date(value: Any, field: str) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise InvalidMetadataError(f"Metadata field {field!r} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidMetadataError(f"Metadata field {field!r} must be an ISO date string") from exc


def freshness_missing_fields(data: dict[str, Any]) -> list[str]:
    return [field for field in FRESHNESS_FIELDS if field not in data or data.get(field) in (None, "")]


def _validate_freshness_presence(data: dict[str, Any], *, strict: bool) -> None:
    missing = freshness_missing_fields(data)
    if strict and missing:
        raise InvalidMetadataError(f"Missing required freshness metadata fields: {', '.join(missing)}")


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _expect_string(value, field)


def _optional_choice(value: Any, allowed: set[str], field: str) -> str | None:
    if value is None:
        return None
    return _expect_choice(value, allowed, field)


def _optional_date(value: Any, field: str) -> date | None:
    if value is None:
        return None
    return _expect_date(value, field)
