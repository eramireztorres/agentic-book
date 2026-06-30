from agentic_book.domain.models import ContentObject, ContentObjectRef
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser


def test_markdown_parser_extracts_metadata_and_sections() -> None:
    text = """---
id: "concept.test"
title: "Test Concept"
type: "concept"
domain: ["agents"]
audience: ["engineer"]
maturity: "experimental"
status: "draft"
last_reviewed: "2026-06-30"
source_quality: "curated"
tags: ["test"]
related: []
---

# Test Concept

Intro.

## Details

More text.
"""
    parser = MarkdownDocumentParser()
    document = parser.parse(ContentObject(ContentObjectRef("file:///tmp/test.md"), text))

    assert document.metadata.id == "concept.test"
    assert [section.heading for section in document.sections] == ["Test Concept", "Details"]
    assert document.sections[1].heading_path == ("Test Concept", "Details")
