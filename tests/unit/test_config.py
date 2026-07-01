import pytest

from agentic_book.application.config import RuntimeConfig


def test_runtime_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTIC_BOOK_CONTENT_ROOT", "custom-content")
    monkeypatch.setenv("AGENTIC_BOOK_DATA_DIR", "custom-data")
    monkeypatch.setenv("AGENTIC_BOOK_STORAGE_BACKEND", "filesystem")
    monkeypatch.setenv("AGENTIC_BOOK_INDEX_BACKEND", "json+lexical")
    monkeypatch.setenv("AGENTIC_BOOK_EMBEDDING_PROVIDER", "none")
    monkeypatch.setenv("AGENTIC_BOOK_VECTOR_STORE", "lancedb")
    monkeypatch.setenv("AGENTIC_BOOK_MCP_TRANSPORT", "http")
    monkeypatch.setenv("AGENTIC_BOOK_MCP_HOST", "0.0.0.0")
    monkeypatch.setenv("AGENTIC_BOOK_MCP_PORT", "9000")
    monkeypatch.setenv("AGENTIC_BOOK_AUTO_INGEST", "true")

    config = RuntimeConfig.from_env()

    assert str(config.content_root) == "custom-content"
    assert str(config.data_dir) == "custom-data"
    assert config.vector_store == "lancedb"
    assert config.mcp_transport == "http"
    assert config.mcp_host == "0.0.0.0"
    assert config.mcp_port == 9000
    assert config.auto_ingest is True


def test_runtime_config_rejects_unknown_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTIC_BOOK_INDEX_BACKEND", "unknown")

    with pytest.raises(ValueError, match="AGENTIC_BOOK_INDEX_BACKEND"):
        RuntimeConfig.from_env()


def test_runtime_config_rejects_unknown_vector_store(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTIC_BOOK_VECTOR_STORE", "unknown")

    with pytest.raises(ValueError, match="AGENTIC_BOOK_VECTOR_STORE"):
        RuntimeConfig.from_env()
