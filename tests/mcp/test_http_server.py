import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from agentic_book.application.ingest import IngestCorpus
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore


def test_http_mcp_server_serves_manifest_and_guarded_search(tmp_path: Path) -> None:
    pytest.importorskip("fastmcp")
    from fastmcp import Client

    store = LocalJsonCorpusIndexStore(tmp_path / "data")
    asyncio.run(
        IngestCorpus(
            FilesystemContentObjectStore(Path("content")),
            MarkdownDocumentParser(),
            store,
        ).run(dry_run=False)
    )
    port = _free_port()
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "agentic_book.interfaces.cli.main",
            "--content-root",
            "content",
            "--data-dir",
            str(tmp_path / "data"),
            "serve-mcp",
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_for_port("127.0.0.1", port, process)

        async def run_client() -> tuple[dict, dict, dict]:
            async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                manifest = await client.call_tool("corpus_manifest", {})
                search = await client.call_tool("search", {"query": "Streamable HTTP MCP", "top_k": 2})
                guarded = await client.call_tool(
                    "search",
                    {"query": "Streamable HTTP MCP", "top_k": 2, "min_score": 999.0},
                )
                return manifest.data, search.data, guarded.data

        manifest, search, guarded = asyncio.run(run_client())
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    assert manifest["documents"] == 4
    assert manifest["capabilities"]["mcp"]["search_abstention"]["parameter"] == "min_score"
    assert {row["row"] for row in manifest["retrieval_eval_matrix_rows"]} == {"baseline", "vector", "guarded"}
    assert search["count"] >= 1
    assert search["abstained"] is False
    assert guarded["count"] == 0
    assert guarded["abstained"] is True
    assert guarded["reason"] == "below_min_score"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_port(host: str, port: int, process: subprocess.Popen[str], timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1)
            raise AssertionError(
                f"MCP server exited early with {process.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            )
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.1)
    process.terminate()
    stdout, stderr = process.communicate(timeout=5)
    raise AssertionError(f"MCP server did not listen on {host}:{port}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
