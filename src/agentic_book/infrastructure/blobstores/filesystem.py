"""Filesystem implementation of ContentObjectStore."""

from __future__ import annotations

from pathlib import Path

from agentic_book.domain.models import ContentObject, ContentObjectRef


class FilesystemContentObjectStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    async def list_objects(self, prefix: str, layer: str = "canonical") -> list[ContentObjectRef]:
        base = (self._root / prefix).resolve()
        if not _is_relative_to(base, self._root):
            raise ValueError(f"Prefix escapes root: {prefix}")
        if not base.exists():
            return []
        refs = [
            ContentObjectRef(uri=_path_to_uri(path), layer=layer)  # type: ignore[arg-type]
            for path in sorted(base.rglob("*.md"))
            if path.is_file()
        ]
        return refs

    async def get_object(self, ref: ContentObjectRef) -> ContentObject:
        path = _uri_to_path(ref.uri)
        resolved = path.resolve()
        if not _is_relative_to(resolved, self._root):
            raise ValueError(f"Object escapes root: {ref.uri}")
        return ContentObject(ref=ref, text=resolved.read_text(encoding="utf-8"))


def _path_to_uri(path: Path) -> str:
    return path.resolve().as_uri()


def _uri_to_path(uri: str) -> Path:
    if not uri.startswith("file://"):
        raise ValueError(f"Unsupported filesystem URI: {uri}")
    return Path(uri.removeprefix("file://"))


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
