"""Composition helpers for interfaces."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any

from agentic_book.application.config import RuntimeConfig, VectorStoreBackend
from agentic_book.application.retrieve import SearchCorpus
from agentic_book.domain.models import Chunk
from agentic_book.domain.ports import VectorStore
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.embeddings.hashing import HashingEmbeddingProvider
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore
from agentic_book.infrastructure.vectorstores.memory import InMemoryVectorStore


def build_content_store(content_root: str | Path) -> FilesystemContentObjectStore:
    return FilesystemContentObjectStore(Path(content_root))


def build_index_store(data_dir: str | Path) -> LocalJsonCorpusIndexStore:
    return LocalJsonCorpusIndexStore(Path(data_dir))


def build_content_store_from_config(config: RuntimeConfig) -> FilesystemContentObjectStore:
    if config.storage_backend != "filesystem":
        raise ValueError(f"Unsupported storage backend for local wiring: {config.storage_backend}")
    return build_content_store(config.content_root)


def build_index_store_from_config(config: RuntimeConfig) -> LocalJsonCorpusIndexStore:
    if config.index_backend != "json+lexical":
        raise ValueError(f"Unsupported index backend for local wiring: {config.index_backend}")
    return build_index_store(config.data_dir)


async def build_local_search_corpus(
    chunks: list[Chunk],
    vector_store_backend: VectorStoreBackend = "memory",
    data_dir: str | Path = ".agentic-book-data",
) -> SearchCorpus:
    embedding_provider = HashingEmbeddingProvider()
    vector_store = _build_vector_store(vector_store_backend, Path(data_dir))
    vectors = await embedding_provider.embed_texts([chunk.text for chunk in chunks])
    await vector_store.upsert(chunks, vectors)
    return SearchCorpus(
        lexical_index=SimpleLexicalIndex(chunks),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )


def _build_vector_store(vector_store_backend: VectorStoreBackend, data_dir: Path) -> VectorStore:
    if vector_store_backend == "memory":
        return InMemoryVectorStore()
    if vector_store_backend == "lancedb":
        from agentic_book.infrastructure.vectorstores.lancedb import LanceDBVectorStore

        return LanceDBVectorStore(data_dir / "vector.lancedb")
    raise ValueError(f"Unsupported vector store backend: {vector_store_backend}")


def build_markdown_parser() -> MarkdownDocumentParser:
    return MarkdownDocumentParser()


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))  # type: ignore[arg-type]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    return value
