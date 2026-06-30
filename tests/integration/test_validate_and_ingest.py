import asyncio
from pathlib import Path

from agentic_book.application.ingest import IngestCorpus
from agentic_book.application.validation import ValidateCorpus
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser


def test_validate_content_fixture_is_ok() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser()

    report = asyncio.run(ValidateCorpus(store, parser).run())

    assert report.ok, report.issues
    assert report.documents_checked == 4


def test_validate_content_fixture_is_ok_with_strict_freshness() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser(strict_freshness=True)

    report = asyncio.run(ValidateCorpus(store, parser).run(strict_freshness=True))

    assert report.ok, report.issues
    assert report.documents_checked == 4


def test_ingest_dry_run_counts_documents_and_chunks() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser()

    report = asyncio.run(IngestCorpus(store, parser).run(dry_run=True))

    assert not report.issues
    assert report.documents_seen == 4
    assert report.chunks_planned > report.documents_seen
    assert report.dry_run is True
