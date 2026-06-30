"""Domain-level exceptions."""


class AgenticBookError(Exception):
    """Base exception for domain and application errors."""


class InvalidMetadataError(AgenticBookError):
    """Raised when Markdown frontmatter does not satisfy the content contract."""


class DuplicateDocumentIdError(AgenticBookError):
    """Raised when two content documents declare the same canonical id."""


class DocumentNotFoundError(AgenticBookError):
    """Raised when a document id cannot be resolved."""


class IndexVersionMismatchError(AgenticBookError):
    """Raised when persisted index metadata does not match runtime configuration."""
