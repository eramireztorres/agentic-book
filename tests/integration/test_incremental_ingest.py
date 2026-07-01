import asyncio
import shutil
from pathlib import Path

from agentic_book.application.ingest import IngestCorpus
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore


def test_incremental_ingest_reuses_unchanged_documents_and_removes_deleted_sources(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    shutil.copytree(Path("content"), content_root)
    store = FilesystemContentObjectStore(content_root)
    parser = MarkdownDocumentParser()
    index_store = LocalJsonCorpusIndexStore(tmp_path / "data")

    first = asyncio.run(IngestCorpus(store, parser, index_store).run(dry_run=False))

    assert first.documents_changed >= 13
    assert first.documents_unchanged == 0
    assert first.documents_removed == 0
    assert first.documents_indexed == first.documents_changed

    second = asyncio.run(IngestCorpus(store, parser, index_store).run(dry_run=False))

    assert second.documents_changed == 0
    assert second.documents_unchanged == first.documents_indexed
    assert second.documents_removed == 0
    assert second.documents_indexed == first.documents_indexed

    (content_root / "concepts" / "mcp.md").unlink()
    third = asyncio.run(IngestCorpus(store, parser, index_store).run(dry_run=False))
    documents = asyncio.run(index_store.read_documents())

    assert third.documents_changed == 0
    assert third.documents_unchanged == first.documents_indexed - 1
    assert third.documents_removed == 1
    assert "concept.mcp" not in {document.metadata.id for document in documents}
