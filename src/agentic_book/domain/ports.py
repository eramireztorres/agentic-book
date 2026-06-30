"""Domain ports implemented by infrastructure adapters."""

from __future__ import annotations

from typing import Protocol

from agentic_book.domain.models import (
    Chunk,
    ContentObject,
    ContentObjectRef,
    Document,
    IngestionManifest,
    IngestionState,
    RetrievalQuery,
    RetrievalResult,
)


class MarkdownParser(Protocol):
    def parse(self, source: ContentObject) -> Document: ...


class ContentObjectStore(Protocol):
    async def list_objects(self, prefix: str, layer: str = "canonical") -> list[ContentObjectRef]: ...

    async def get_object(self, ref: ContentObjectRef) -> ContentObject: ...


class DocumentRepository(Protocol):
    async def list_documents(self, layer: str | None = None) -> list[Document]: ...

    async def get_document(self, document_id: str) -> Document | None: ...


class CorpusIndexStore(Protocol):
    async def write(
        self,
        documents: list[Document],
        chunks: list[Chunk],
        manifest: IngestionManifest,
        state: IngestionState | None = None,
    ) -> str: ...

    async def read_chunks(self) -> list[Chunk]: ...

    async def read_documents(self) -> list[Document]: ...

    async def read_ingestion_state(self) -> IngestionState | None: ...


class LexicalIndex(Protocol):
    async def upsert(self, chunks: list[Chunk]) -> None: ...

    async def search(self, query: RetrievalQuery) -> list[RetrievalResult]: ...


class RetrievalEngine(Protocol):
    async def run(self, query: RetrievalQuery) -> list[RetrievalResult]: ...


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    async def search(self, query: RetrievalQuery, query_vector: list[float]) -> list[RetrievalResult]: ...


class Reranker(Protocol):
    async def rerank(self, query: str, results: list[RetrievalResult]) -> list[RetrievalResult]: ...
