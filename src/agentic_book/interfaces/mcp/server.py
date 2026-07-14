"""FastMCP read-only server for Agentic Book."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from agentic_book.application.capabilities import build_capabilities_manifest
from agentic_book.application.config import RuntimeConfig
from agentic_book.application.documents import GetDocument
from agentic_book.application.freshness import BuildStaleReport
from agentic_book.application.fusion import FusionSearchCorpus
from agentic_book.domain.errors import DocumentNotFoundError
from agentic_book.domain.models import RetrievalFilters, RetrievalMode, RetrievalQuery
from agentic_book.infrastructure.evaluation.json_dataset import (
    load_retrieval_eval_matrix_report,
    load_retrieval_eval_report,
)
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
from agentic_book.interfaces.wiring import build_index_store, build_local_search_corpus, to_jsonable


def create_mcp_server(content_root: str = "content", data_dir: str = ".agentic-book-data"):
    try:
        from fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError('FastMCP is not installed. Install with `python -m pip install -e ".[mcp]"`.') from exc

    env_config = RuntimeConfig.from_env()
    index_store = build_index_store(data_dir)
    mcp = FastMCP(
        name="AgenticBook",
        instructions="Use this server to retrieve grounded context from Agentic Book.",
    )

    @mcp.tool
    async def search(
        query: str,
        top_k: int = 8,
        retrieval_mode: str = "lexical",
        min_score: float = 0.0,
        document_type: str | None = None,
        domain: str | None = None,
        tag: str | None = None,
    ) -> dict:
        """Search the Agentic Book local index with optional low-score abstention."""
        chunks = await index_store.read_chunks()
        filters = _filters(document_type=document_type, domain=domain, tag=tag)
        retrieval_query = RetrievalQuery(
            query=query, top_k=top_k, retrieval_mode=_retrieval_mode(retrieval_mode), filters=filters
        )
        search_corpus = await build_local_search_corpus(
            chunks, vector_store_backend=env_config.vector_store, data_dir=data_dir
        )
        results = await search_corpus.run(retrieval_query)
        max_score = results[0].score if results else 0.0
        reason = _abstention_reason(results_found=bool(results), max_score=max_score, min_score=min_score)
        visible_results = [] if reason else results
        return {
            "results": to_jsonable(visible_results),
            "count": len(visible_results),
            "abstained": reason is not None,
            "reason": reason,
            "max_score": max_score,
            "min_score": min_score,
            "candidate_count": len(results),
        }

    @mcp.tool
    async def fusion_search(
        queries: list[str],
        top_k_per_query: int = 8,
        final_top_k: int = 10,
        rrf_k: int = 60,
        document_type: str | None = None,
        domain: str | None = None,
        tag: str | None = None,
    ) -> dict:
        """Run multi-query lexical search with Reciprocal Rank Fusion."""
        chunks = await index_store.read_chunks()
        filters = _filters(document_type=document_type, domain=domain, tag=tag)
        base_query = RetrievalQuery(query=" | ".join(queries), retrieval_mode="lexical", filters=filters)
        results = await FusionSearchCorpus(SimpleLexicalIndex(chunks)).run(
            queries,
            base_query=base_query,
            top_k_per_query=top_k_per_query,
            final_top_k=final_top_k,
            rrf_k=rrf_k,
        )
        return {"results": to_jsonable(results), "count": len(results)}

    @mcp.tool
    async def get_document(document_id: str) -> dict:
        """Return a complete indexed document by canonical id."""
        try:
            document = await GetDocument(index_store).run(document_id)
        except DocumentNotFoundError as exc:
            return {"error": str(exc), "document": None}
        return {"document": to_jsonable(document)}

    @mcp.tool
    async def corpus_manifest() -> dict:
        """Return local corpus statistics and available capabilities."""
        documents = await index_store.read_documents()
        chunks = await index_store.read_chunks()
        try:
            manifest = await index_store.read_manifest()
            manifest_data = to_jsonable(manifest)
        except FileNotFoundError:
            manifest_data = None
        state = await index_store.read_ingestion_state()
        freshness_report = await BuildStaleReport(index_store).run()
        eval_summary = _latest_eval_summary(Path("evals/reports/latest.json"))
        matrix_summary = _latest_eval_matrix_summary(Path("evals/reports/matrix.json"))
        capabilities = build_capabilities_manifest(active_vector_store=env_config.vector_store)
        return {
            "name": "Agentic Book",
            "documents": len(documents),
            "chunks": len(chunks),
            "manifest": manifest_data,
            "ingestion_state": {
                "schema_version": state.schema_version if state else None,
                "documents_tracked": len(state.documents) if state else 0,
            },
            "freshness": {
                "checked": freshness_report.checked,
                "stale": len(freshness_report.stale),
                "stale_document_ids": [item.document_id for item in freshness_report.stale],
            },
            "latest_eval": eval_summary,
            "latest_eval_matrix": matrix_summary,
            "capabilities": capabilities,
            "retrieval_eval_profiles": capabilities["retrieval_eval_profiles"],
            "retrieval_eval_matrix_rows": capabilities["retrieval_eval_matrix_rows"],
            "retrieval_modes": capabilities["retrieval_modes"],
            "embedding_provider": capabilities["embedding_provider"],
            "vector_store": capabilities["vector_store"],
            "tools": capabilities["mcp"]["tools"],
            "resources": capabilities["mcp"]["resources"],
        }

    @mcp.resource("agentic-book://manifest")
    async def manifest_resource() -> str:
        """Expose corpus manifest as a stable resource."""
        return _resource_json(await corpus_manifest())

    @mcp.resource("agentic-book://documents/{document_id}")
    async def document_resource(document_id: str) -> str:
        """Expose indexed documents as stable resources."""
        return _resource_json(await get_document(document_id))

    @mcp.prompt
    def summarize_with_citations(document_id: str) -> str:
        return (
            f"Retrieve agentic-book://documents/{document_id}, summarize the document, "
            "and cite the document id and relevant section headings."
        )

    @mcp.prompt
    def compare_concepts(concept_a: str, concept_b: str, audience: str = "architect") -> str:
        return (
            f"Compare {concept_a} and {concept_b} for {audience}. "
            "Use search first, then get_document for the strongest evidence."
        )

    return mcp


def _resource_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _filters(document_type: str | None = None, domain: str | None = None, tag: str | None = None) -> RetrievalFilters:
    return RetrievalFilters(
        type=[document_type] if document_type else [],
        domain=[domain] if domain else [],
        tags=[tag] if tag else [],
    )


def run_mcp_server(
    content_root: str = "content",
    data_dir: str = ".agentic-book-data",
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    mcp = create_mcp_server(content_root=content_root, data_dir=data_dir)
    if transport == "stdio":
        mcp.run()
    elif transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        raise ValueError(f"Unsupported MCP transport: {transport}")


# Default FastMCP app for `fastmcp run/list src/agentic_book/interfaces/mcp/server.py:mcp`.
# Configurable tests and CLI paths should prefer `create_mcp_server`.
mcp = create_mcp_server()


def _retrieval_mode(value: str) -> RetrievalMode:
    if value not in {"lexical", "vector", "hybrid"}:
        raise ValueError("retrieval_mode must be one of: lexical, vector, hybrid")
    return cast(RetrievalMode, value)


def _abstention_reason(*, results_found: bool, max_score: float, min_score: float) -> str | None:
    if not results_found:
        return "no_results"
    if max_score < min_score:
        return "below_min_score"
    return None


def _latest_eval_summary(path: Path) -> dict[str, Any] | None:
    report = load_retrieval_eval_report(path)
    if report is None:
        return None
    return {
        "path": str(path),
        "profile": report.get("profile"),
        "retrieval_mode": report.get("retrieval_mode"),
        "cases": report.get("cases"),
        "hit_rate": report.get("hit_rate"),
        "mean_reciprocal_rank": report.get("mean_reciprocal_rank"),
        "unanswerable_success_rate": report.get("unanswerable_success_rate"),
        "abstention_rate": report.get("abstention_rate"),
        "min_score": report.get("min_score"),
    }


def _latest_eval_matrix_summary(path: Path) -> dict[str, Any] | None:
    report = load_retrieval_eval_matrix_report(path)
    if report is None:
        return None
    rows = report.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    return {
        "path": str(path),
        "passed": report.get("passed"),
        "dataset": report.get("dataset"),
        "generated_at": report.get("generated_at"),
        "rows": [
            {
                "row": row.get("row"),
                "passed": row.get("passed"),
                "profile": row.get("profile"),
                "retrieval_mode": row.get("retrieval_mode"),
                "hit_rate": row.get("hit_rate"),
                "mean_reciprocal_rank": row.get("mean_reciprocal_rank"),
                "unanswerable_success_rate": row.get("unanswerable_success_rate"),
                "abstention_rate": row.get("abstention_rate"),
            }
            for row in rows
            if isinstance(row, dict)
        ],
    }
