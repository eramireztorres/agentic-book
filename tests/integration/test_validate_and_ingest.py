import asyncio
from pathlib import Path

from agentic_book.application.ingest import IngestCorpus
from agentic_book.application.validation import ValidateCorpus
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser

MIN_CANONICAL_DOCUMENTS = 13


def test_validate_content_fixture_is_ok() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser()

    report = asyncio.run(ValidateCorpus(store, parser).run())

    assert report.ok, report.issues
    assert report.documents_checked >= MIN_CANONICAL_DOCUMENTS


def test_validate_content_fixture_is_ok_with_strict_freshness() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser(strict_freshness=True)

    report = asyncio.run(ValidateCorpus(store, parser).run(strict_freshness=True))

    assert report.ok, report.issues
    assert report.documents_checked >= MIN_CANONICAL_DOCUMENTS


def test_ingest_dry_run_counts_documents_and_chunks() -> None:
    store = FilesystemContentObjectStore(Path("content"))
    parser = MarkdownDocumentParser()

    report = asyncio.run(IngestCorpus(store, parser).run(dry_run=True))

    assert not report.issues
    assert report.documents_seen >= MIN_CANONICAL_DOCUMENTS
    assert report.chunks_planned > report.documents_seen
    assert report.dry_run is True
