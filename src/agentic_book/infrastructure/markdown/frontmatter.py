"""Small frontmatter parser for the project's constrained YAML subset."""

from __future__ import annotations

import ast
from typing import Any

from agentic_book.domain.errors import InvalidMetadataError


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise InvalidMetadataError("Markdown document must start with YAML frontmatter")
    try:
        _, raw_metadata, body = text.split("---\n", 2)
    except ValueError as exc:
        raise InvalidMetadataError("Markdown frontmatter must be closed with ---") from exc
    return parse_simple_yaml(raw_metadata), body.strip()


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Parse the YAML subset used by content fixtures.

    Supported forms:
    - `key: "value"`
    - `key: value`
    - `key: ["a", "b"]`
    - block lists:
      key:
        - "a"
    """

    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        if not raw_line.strip():
            continue
        if raw_line.startswith("  - "):
            if current_list_key is None:
                raise InvalidMetadataError(f"List item without key at frontmatter line {line_number}")
            result[current_list_key].append(_parse_scalar(raw_line[4:].strip()))
            continue
        if raw_line.startswith(" "):
            raise InvalidMetadataError(f"Unsupported indentation at frontmatter line {line_number}")
        if ":" not in raw_line:
            raise InvalidMetadataError(f"Invalid frontmatter line {line_number}: {raw_line}")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise InvalidMetadataError(f"Empty frontmatter key at line {line_number}")
        if not value:
            result[key] = []
            current_list_key = key
        else:
            result[key] = _parse_scalar(value)
            current_list_key = None
    return result


def _parse_scalar(value: str) -> Any:
    if value.startswith("["):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise InvalidMetadataError(f"Invalid inline list: {value}") from exc
        if not isinstance(parsed, list):
            raise InvalidMetadataError(f"Expected inline list: {value}")
        return parsed
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise InvalidMetadataError(f"Invalid quoted string: {value}") from exc
    return value
