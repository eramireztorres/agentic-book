"""Document retrieval use cases."""

from __future__ import annotations

from agentic_book.domain.errors import DocumentNotFoundError
from agentic_book.domain.models import Document
from agentic_book.domain.ports import DocumentRepository


class GetDocument:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    async def run(self, document_id: str) -> Document:
        document = await self._repository.get_document(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document not found: {document_id}")
        return document
