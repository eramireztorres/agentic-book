from pathlib import Path

import pytest

from agentic_book.infrastructure.blobstores import filesystem


def test_uri_to_path_decodes_posix_file_uri() -> None:
    path = filesystem._uri_to_path("file:///tmp/agentic%20book/test.md")

    assert path == Path("/tmp/agentic book/test.md")


def test_uri_to_path_normalizes_windows_drive_uri(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filesystem.os, "name", "nt")

    path = filesystem._uri_to_path("file:///D:/a/agentic-book/agentic-book/content/test.md")

    assert str(path).replace("\\", "/") == "D:/a/agentic-book/agentic-book/content/test.md"


def test_uri_to_path_rejects_non_file_uri() -> None:
    with pytest.raises(ValueError, match="Unsupported filesystem URI"):
        filesystem._uri_to_path("https://example.com/test.md")
