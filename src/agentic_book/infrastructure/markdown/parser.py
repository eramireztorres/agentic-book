"""Markdown parser implementation."""

from __future__ import annotations

import re

from agentic_book.domain.metadata_schema import metadata_from_mapping
from agentic_book.domain.models import ContentObject, Document, Section
from agentic_book.infrastructure.markdown.frontmatter import split_frontmatter

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class MarkdownDocumentParser:
    def __init__(self, strict_freshness: bool = False) -> None:
        self._strict_freshness = strict_freshness

    def parse(self, source: ContentObject) -> Document:
        raw_metadata, body = split_frontmatter(source.text)
        metadata = metadata_from_mapping(
            raw_metadata,
            default_layer=source.ref.layer,
            strict_freshness=self._strict_freshness,
        )
        sections = _extract_sections(body, metadata.id)
        return Document(metadata=metadata, body=body, source_uri=source.ref.uri, sections=sections)


def _extract_sections(body: str, document_id: str) -> list[Section]:
    sections: list[Section] = []
    current_heading: str | None = None
    current_level: int | None = None
    current_lines: list[str] = []
    heading_stack: list[tuple[int, str]] = []

    def flush() -> None:
        if current_heading is None or current_level is None:
            return
        section_index = len(sections) + 1
        heading_path = tuple(heading for _, heading in heading_stack)
        sections.append(
            Section(
                id=f"{section_index:04d}",
                document_id=document_id,
                heading=current_heading,
                level=current_level,
                text="\n".join(current_lines).strip(),
                heading_path=heading_path,
            )
        )

    for line in body.splitlines():
        match = HEADING_RE.match(line)
        if match:
            flush()
            current_level = len(match.group(1))
            current_heading = match.group(2).strip()
            current_lines = [line]
            heading_stack = [(level, heading) for level, heading in heading_stack if level < current_level]
            heading_stack.append((current_level, current_heading))
        elif current_heading is not None:
            current_lines.append(line)
    flush()
    return sections
