"""Runtime configuration shared by CLI, MCP, Docker, and future cloud wiring."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

StorageBackend = Literal["filesystem", "s3"]
IndexBackend = Literal["json+lexical", "opensearch", "qdrant", "lancedb"]
EmbeddingProviderName = Literal["none", "openai", "bedrock", "local"]
McpTransport = Literal["stdio", "http"]


@dataclass(frozen=True)
class RuntimeConfig:
    content_root: Path = Path("content")
    data_dir: Path = Path(".agentic-book-data")
    storage_backend: StorageBackend = "filesystem"
    index_backend: IndexBackend = "json+lexical"
    embedding_provider: EmbeddingProviderName = "none"
    mcp_transport: McpTransport = "stdio"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000
    auto_ingest: bool = False

    @classmethod
    def from_env(cls) -> RuntimeConfig:
        return cls(
            content_root=Path(os.getenv("AGENTIC_BOOK_CONTENT_ROOT", "content")),
            data_dir=Path(os.getenv("AGENTIC_BOOK_DATA_DIR", ".agentic-book-data")),
            storage_backend=cast(
                StorageBackend,
                _choice(
                    os.getenv("AGENTIC_BOOK_STORAGE_BACKEND", "filesystem"),
                    {"filesystem", "s3"},
                    "AGENTIC_BOOK_STORAGE_BACKEND",
                ),
            ),
            index_backend=cast(
                IndexBackend,
                _choice(
                    os.getenv("AGENTIC_BOOK_INDEX_BACKEND", "json+lexical"),
                    {"json+lexical", "opensearch", "qdrant", "lancedb"},
                    "AGENTIC_BOOK_INDEX_BACKEND",
                ),
            ),
            embedding_provider=cast(
                EmbeddingProviderName,
                _choice(
                    os.getenv("AGENTIC_BOOK_EMBEDDING_PROVIDER", "none"),
                    {"none", "openai", "bedrock", "local"},
                    "AGENTIC_BOOK_EMBEDDING_PROVIDER",
                ),
            ),
            mcp_transport=cast(
                McpTransport,
                _choice(
                    os.getenv("AGENTIC_BOOK_MCP_TRANSPORT", "stdio"),
                    {"stdio", "http"},
                    "AGENTIC_BOOK_MCP_TRANSPORT",
                ),
            ),
            mcp_host=os.getenv("AGENTIC_BOOK_MCP_HOST", "127.0.0.1"),
            mcp_port=int(os.getenv("AGENTIC_BOOK_MCP_PORT", "8000")),
            auto_ingest=os.getenv("AGENTIC_BOOK_AUTO_INGEST", "false").lower() == "true",
        )


def _choice(value: str, allowed: set[str], name: str) -> str:
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {allowed_values}")
    return value
