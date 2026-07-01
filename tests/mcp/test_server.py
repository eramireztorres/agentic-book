import asyncio
from pathlib import Path

import pytest

from agentic_book.application.ingest import IngestCorpus
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore


def test_mcp_server_can_be_created_when_fastmcp_is_installed(tmp_path: Path) -> None:
    pytest.importorskip("fastmcp")
    from fastmcp import Client

    from agentic_book.interfaces.mcp.server import create_mcp_server

    store = LocalJsonCorpusIndexStore(tmp_path)
    asyncio.run(
        IngestCorpus(
            FilesystemContentObjectStore(Path("content")),
            MarkdownDocumentParser(),
            store,
        ).run(dry_run=False)
    )
    server = create_mcp_server(data_dir=str(tmp_path))

    async def run_client() -> tuple[list[str], dict, dict, dict, dict]:
        async with Client(server) as client:
            tools = await client.list_tools()
            manifest = await client.call_tool("corpus_manifest", {})
            search = await client.call_tool("search", {"query": "Streamable HTTP MCP", "top_k": 2})
            guarded_search = await client.call_tool(
                "search",
                {"query": "Streamable HTTP MCP", "top_k": 2, "min_score": 999.0},
            )
            fusion = await client.call_tool(
                "fusion_search",
                {"queries": ["Streamable HTTP", "MCP resources"], "final_top_k": 2},
            )
            return [tool.name for tool in tools], manifest.data, search.data, guarded_search.data, fusion.data

    tool_names, manifest, search, guarded_search, fusion = asyncio.run(run_client())

    assert "search" in tool_names
    assert "fusion_search" in tool_names
    assert "get_document" in tool_names
    assert "corpus_manifest" in tool_names
    assert "stale_report" not in tool_names
    assert "propose_doc_update" not in tool_names
    assert manifest["documents"] >= 13
    assert manifest["ingestion_state"]["documents_tracked"] >= 13
    assert manifest["freshness"]["checked"] >= 13
    assert manifest["freshness"]["stale"] == 0
    assert "hybrid" in manifest["retrieval_modes"]
    assert "fusion" in manifest["retrieval_modes"]
    profile_names = {profile["name"] for profile in manifest["retrieval_eval_profiles"]}
    assert {"baseline", "guarded", "custom"} <= profile_names
    matrix_rows = {row["row"]: row for row in manifest["retrieval_eval_matrix_rows"]}
    assert matrix_rows["baseline"]["retrieval_mode"] == "lexical"
    assert matrix_rows["vector"]["retrieval_mode"] == "vector"
    assert matrix_rows["guarded"]["min_score"] > 0
    assert search["count"] >= 1
    assert search["results"][0]["document_id"] == "concept.mcp"
    assert search["abstained"] is False
    assert search["max_score"] > 0
    assert guarded_search["count"] == 0
    assert guarded_search["candidate_count"] >= 1
    assert guarded_search["abstained"] is True
    assert guarded_search["reason"] == "below_min_score"
    assert guarded_search["max_score"] < guarded_search["min_score"]
    assert fusion["count"] >= 1
    assert fusion["results"][0]["retrieval_mode"] == "fusion"
