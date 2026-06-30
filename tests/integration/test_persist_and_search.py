import asyncio
from pathlib import Path

from agentic_book.application.ingest import IngestCorpus
from agentic_book.application.retrieve import SearchCorpus
from agentic_book.domain.models import RetrievalQuery
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore


def test_ingest_persists_json_and_search_finds_mcp_transport(tmp_path: Path) -> None:
    content_store = FilesystemContentObjectStore(Path("content"))
    index_store = LocalJsonCorpusIndexStore(tmp_path)
    parser = MarkdownDocumentParser()

    ingest_report = asyncio.run(IngestCorpus(content_store, parser, index_store).run(dry_run=False))

    assert not ingest_report.issues
    assert ingest_report.documents_indexed == 4
    assert ingest_report.chunks_indexed == 13
    assert (tmp_path / "documents.json").exists()
    assert (tmp_path / "chunks.json").exists()
    assert (tmp_path / "ingestion_manifest.json").exists()

    chunks = asyncio.run(index_store.read_chunks())
    results = asyncio.run(
        SearchCorpus(SimpleLexicalIndex(chunks)).run(
            RetrievalQuery(query="Streamable HTTP MCP", top_k=3, retrieval_mode="lexical")
        )
    )

    assert results
    assert results[0].document_id == "concept.mcp"
