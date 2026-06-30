from datetime import date

import pytest

from agentic_book.domain.errors import InvalidMetadataError
from agentic_book.domain.metadata_schema import metadata_from_mapping


def valid_metadata() -> dict:
    return {
        "id": "concept.mcp",
        "title": "Model Context Protocol",
        "type": "concept",
        "domain": ["agents", "mcp"],
        "audience": ["engineer"],
        "maturity": "production",
        "status": "reviewed",
        "last_reviewed": "2026-06-30",
        "source_quality": "curated",
        "tags": ["mcp"],
        "related": [],
    }


def test_metadata_from_mapping_accepts_valid_metadata() -> None:
    metadata = metadata_from_mapping(valid_metadata())

    assert metadata.id == "concept.mcp"
    assert metadata.last_reviewed == date(2026, 6, 30)
    assert metadata.layer == "canonical"


def test_metadata_from_mapping_rejects_missing_required_field() -> None:
    data = valid_metadata()
    del data["id"]

    with pytest.raises(InvalidMetadataError, match="Missing required"):
        metadata_from_mapping(data)


def test_metadata_from_mapping_rejects_unknown_type() -> None:
    data = valid_metadata()
    data["type"] = "unknown"

    with pytest.raises(InvalidMetadataError, match="type"):
        metadata_from_mapping(data)


def test_metadata_from_mapping_accepts_freshness_metadata() -> None:
    data = valid_metadata()
    data.update(
        {
            "source_type": "official",
            "source_urls": ["https://modelcontextprotocol.io/docs"],
            "upstream_version": "2026-06",
            "last_checked": "2026-06-30",
            "review_after": "2026-09-30",
            "change_frequency": "high",
        }
    )

    metadata = metadata_from_mapping(data, strict_freshness=True)

    assert metadata.source_type == "official"
    assert metadata.source_urls == ["https://modelcontextprotocol.io/docs"]
    assert metadata.last_checked == date(2026, 6, 30)
    assert metadata.review_after == date(2026, 9, 30)
    assert metadata.change_frequency == "high"


def test_metadata_from_mapping_strict_freshness_rejects_missing_fields() -> None:
    with pytest.raises(InvalidMetadataError, match="freshness metadata"):
        metadata_from_mapping(valid_metadata(), strict_freshness=True)


def test_metadata_from_mapping_requires_source_urls_for_external_sources() -> None:
    data = valid_metadata()
    data.update(
        {
            "source_type": "official",
            "last_checked": "2026-06-30",
            "review_after": "2026-09-30",
            "change_frequency": "high",
        }
    )

    with pytest.raises(InvalidMetadataError, match="source_urls"):
        metadata_from_mapping(data, strict_freshness=True)
