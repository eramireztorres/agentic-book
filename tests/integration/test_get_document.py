import asyncio
from pathlib import Path

import pytest

from agentic_book.application.documents import GetDocument
from agentic_book.application.ingest import IngestCorpus
from agentic_book.domain.errors import DocumentNotFoundError
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore


def _indexed_store(tmp_path: Path) -> LocalJsonCorpusIndexStore:
    store = LocalJsonCorpusIndexStore(tmp_path)
    asyncio.run(
        IngestCorpus(
            FilesystemContentObjectStore(Path("content")),
            MarkdownDocumentParser(),
            store,
        ).run(dry_run=False)
    )
    return store


def test_get_document_returns_indexed_document(tmp_path: Path) -> None:
    store = _indexed_store(tmp_path)

    document = asyncio.run(GetDocument(store).run("concept.mcp"))

    assert document.metadata.title == "Model Context Protocol"
    assert "Streamable HTTP" in document.body


def test_get_document_raises_for_unknown_id(tmp_path: Path) -> None:
    store = _indexed_store(tmp_path)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(GetDocument(store).run("missing.doc"))
