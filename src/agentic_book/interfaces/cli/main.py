"""Command line interface for early project workflows."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

from agentic_book.application.capabilities import build_capabilities_manifest
from agentic_book.application.config import RuntimeConfig
from agentic_book.application.documents import GetDocument
from agentic_book.application.evaluation import EvaluateRetrieval
from agentic_book.application.evaluation_profiles import (
    get_retrieval_eval_profile,
    list_retrieval_eval_matrix_rows,
    resolve_retrieval_eval_row,
)
from agentic_book.application.freshness import BuildStaleReport, ProposeDocumentationUpdate
from agentic_book.application.fusion import FusionSearchCorpus
from agentic_book.application.ingest import IngestCorpus
from agentic_book.application.validation import ValidateCorpus
from agentic_book.domain.models import RetrievalEvalReport, RetrievalFilters, RetrievalQuery, RetrievalResult
from agentic_book.infrastructure.blobstores.filesystem import FilesystemContentObjectStore
from agentic_book.infrastructure.evaluation.json_dataset import (
    load_retrieval_eval_cases,
    write_retrieval_eval_matrix_report,
    write_retrieval_eval_report,
)
from agentic_book.infrastructure.lexical.simple import SimpleLexicalIndex
from agentic_book.infrastructure.markdown.parser import MarkdownDocumentParser
from agentic_book.infrastructure.persistence.json_store import LocalJsonCorpusIndexStore
from agentic_book.interfaces.wiring import build_local_search_corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentic-book")
    parser.add_argument("--content-root", default="content", help="Root directory for canonical Markdown content")
    parser.add_argument("--data-dir", default=".agentic-book-data", help="Directory for local generated indexes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate-content", help="Validate Markdown frontmatter and corpus references"
    )
    validate_parser.add_argument(
        "--strict-freshness",
        action="store_true",
        default=False,
        help="Require source_type, last_checked, review_after, and change_frequency metadata",
    )

    ingest_parser = subparsers.add_parser("ingest", help="Build or plan the local corpus index")
    ingest_parser.add_argument("--dry-run", action="store_true", default=False, help="Plan ingestion without writing")

    search_parser = subparsers.add_parser("search", help="Search the local lexical index")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top-k", type=int, default=8, help="Maximum number of results")
    search_parser.add_argument("--retrieval-mode", choices=["lexical", "vector", "hybrid"], default="lexical")
    _add_filter_args(search_parser)

    fusion_parser = subparsers.add_parser("fusion-search", help="Run multi-query lexical search with RRF")
    fusion_parser.add_argument(
        "--query", dest="queries", action="append", required=True, help="Subquery; repeat this option"
    )
    fusion_parser.add_argument("--top-k-per-query", type=int, default=8)
    fusion_parser.add_argument("--final-top-k", type=int, default=10)
    fusion_parser.add_argument("--rrf-k", type=int, default=60)
    _add_filter_args(fusion_parser)

    document_parser = subparsers.add_parser("get-document", help="Print a complete indexed document by id")
    document_parser.add_argument("document_id", help="Canonical document id")

    eval_parser = subparsers.add_parser(
        "eval-retrieval", help="Evaluate lexical retrieval against a ground-truth dataset"
    )
    eval_parser.add_argument(
        "--dataset", default="evals/retrieval/ground_truth.json", help="Path to retrieval eval JSON"
    )
    eval_parser.add_argument(
        "--profile",
        choices=["baseline", "guarded", "custom"],
        default="baseline",
        help="Evaluation profile defaults for retrieval mode and quality gates",
    )
    eval_parser.add_argument("--retrieval-mode", choices=["lexical", "vector", "hybrid"], default=None)
    eval_parser.add_argument("--min-hit-rate", type=float, default=None, help="Minimum acceptable answerable hit rate")
    eval_parser.add_argument("--min-mrr", type=float, default=None, help="Minimum acceptable mean reciprocal rank")
    eval_parser.add_argument(
        "--min-unanswerable-success",
        type=float,
        default=None,
        help="Minimum acceptable success rate for unanswerable cases",
    )
    eval_parser.add_argument(
        "--min-score", type=float, default=None, help="Abstain when the best result score is below this value"
    )
    eval_parser.add_argument("--write-report", help="Write JSON evaluation report to this path")
    eval_parser.add_argument("--json", action="store_true", default=False, help="Print machine-readable JSON")

    matrix_parser = subparsers.add_parser("eval-matrix", help="Run the standard retrieval evaluation profile matrix")
    matrix_parser.add_argument(
        "--dataset", default="evals/retrieval/ground_truth.json", help="Path to retrieval eval JSON"
    )
    matrix_parser.add_argument(
        "--row",
        choices=["baseline", "vector", "guarded"],
        action="append",
        default=[],
        help="Matrix row to run; repeat to select multiple rows. Defaults to all rows.",
    )
    matrix_parser.add_argument(
        "--write-report",
        default="evals/reports/matrix.json",
        help="Write aggregate JSON evaluation report to this path",
    )
    matrix_parser.add_argument("--json", action="store_true", default=False, help="Print machine-readable JSON")

    stale_parser = subparsers.add_parser("stale-report", help="Report indexed documents due for freshness review")
    stale_parser.add_argument("--json", action="store_true", default=False, help="Print machine-readable JSON")

    proposal_parser = subparsers.add_parser("propose-doc-update", help="Create a local documentation update proposal")
    proposal_parser.add_argument("document_id", help="Canonical document id")
    proposal_parser.add_argument("--reason", required=True, help="Why this document may need an update")
    proposal_parser.add_argument("--source-hint", help="Optional URL or source that motivated the proposal")
    proposal_parser.add_argument("--urgency", choices=["low", "medium", "high"], default="medium")
    proposal_parser.add_argument("--proposed-change", help="Optional suggested change for human review")
    proposal_parser.add_argument("--proposals-dir", default=".proposals", help="Directory for local proposal artifacts")

    capabilities_parser = subparsers.add_parser(
        "capabilities", help="Print machine-readable runtime capabilities for agent consumers"
    )
    capabilities_parser.add_argument("--json", action="store_true", default=False, help="Print machine-readable JSON")

    serve_parser = subparsers.add_parser("serve-mcp", help="Serve the read-only MCP interface")
    serve_parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    env_config = RuntimeConfig.from_env()
    config = RuntimeConfig(
        content_root=Path(args.content_root) if args.content_root != "content" else env_config.content_root,
        data_dir=Path(args.data_dir) if args.data_dir != ".agentic-book-data" else env_config.data_dir,
        storage_backend=env_config.storage_backend,
        index_backend=env_config.index_backend,
        embedding_provider=env_config.embedding_provider,
        mcp_transport=args.transport if hasattr(args, "transport") else env_config.mcp_transport,
        mcp_host=args.host if hasattr(args, "host") else env_config.mcp_host,
        mcp_port=args.port if hasattr(args, "port") else env_config.mcp_port,
        auto_ingest=env_config.auto_ingest,
    )
    content_store = FilesystemContentObjectStore(config.content_root)
    index_store = LocalJsonCorpusIndexStore(config.data_dir)
    markdown_parser = MarkdownDocumentParser()

    if args.command == "validate-content":
        validation_parser = MarkdownDocumentParser(strict_freshness=args.strict_freshness)
        validation_report = asyncio.run(
            ValidateCorpus(content_store, validation_parser).run(strict_freshness=args.strict_freshness)
        )
        for issue in validation_report.issues:
            print(f"{issue.severity.upper()}: {issue.source_uri}: {issue.message}")
        print(
            f"checked={validation_report.documents_checked} "
            f"issues={len(validation_report.issues)} ok={str(validation_report.ok).lower()}"
        )
        return 0 if validation_report.ok else 1

    if args.command == "ingest":
        ingestion_report = asyncio.run(
            IngestCorpus(content_store, markdown_parser, index_store).run(dry_run=args.dry_run)
        )
        for issue in ingestion_report.issues:
            print(f"{issue.severity.upper()}: {issue.source_uri}: {issue.message}")
        print(
            "dry_run={dry_run} documents_seen={documents_seen} chunks_planned={chunks_planned} "
            "documents_indexed={documents_indexed} chunks_indexed={chunks_indexed} "
            "documents_changed={documents_changed} documents_unchanged={documents_unchanged} "
            "documents_removed={documents_removed} manifest_uri={manifest_uri} issues={issues}".format(
                dry_run=str(ingestion_report.dry_run).lower(),
                documents_seen=ingestion_report.documents_seen,
                chunks_planned=ingestion_report.chunks_planned,
                documents_indexed=ingestion_report.documents_indexed,
                chunks_indexed=ingestion_report.chunks_indexed,
                documents_changed=ingestion_report.documents_changed,
                documents_unchanged=ingestion_report.documents_unchanged,
                documents_removed=ingestion_report.documents_removed,
                manifest_uri=ingestion_report.manifest_uri or "none",
                issues=len(ingestion_report.issues),
            )
        )
        return 0 if not ingestion_report.issues else 1

    if args.command == "search":
        try:
            chunks = asyncio.run(index_store.read_chunks())
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        filters = _filters_from_args(args)
        query = RetrievalQuery(query=args.query, top_k=args.top_k, retrieval_mode=args.retrieval_mode, filters=filters)
        search_corpus = asyncio.run(build_local_search_corpus(chunks))
        results = asyncio.run(search_corpus.run(query))
        _print_results(results)
        return 0

    if args.command == "fusion-search":
        try:
            chunks = asyncio.run(index_store.read_chunks())
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        base_query = RetrievalQuery(
            query=" | ".join(args.queries), retrieval_mode="lexical", filters=_filters_from_args(args)
        )
        results = asyncio.run(
            FusionSearchCorpus(SimpleLexicalIndex(chunks)).run(
                args.queries,
                base_query=base_query,
                top_k_per_query=args.top_k_per_query,
                final_top_k=args.final_top_k,
                rrf_k=args.rrf_k,
            )
        )
        _print_results(results)
        return 0

    if args.command == "get-document":
        try:
            document = asyncio.run(GetDocument(index_store).run(args.document_id))
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        except Exception as exc:
            print(f"ERROR: {exc}")
            return 1
        print(f"# {document.metadata.title}")
        print(f"id={document.metadata.id} type={document.metadata.type} status={document.metadata.status}")
        print()
        print(document.body)
        return 0

    if args.command == "eval-retrieval":
        try:
            chunks = asyncio.run(index_store.read_chunks())
            cases = load_retrieval_eval_cases(Path(args.dataset))
            search_corpus = asyncio.run(build_local_search_corpus(chunks))
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        profile = get_retrieval_eval_profile(args.profile)
        retrieval_mode = args.retrieval_mode or profile.retrieval_mode
        min_hit_rate = args.min_hit_rate if args.min_hit_rate is not None else profile.min_hit_rate
        min_mrr = args.min_mrr if args.min_mrr is not None else profile.min_mrr
        min_unanswerable_success = (
            args.min_unanswerable_success
            if args.min_unanswerable_success is not None
            else profile.min_unanswerable_success
        )
        min_score = args.min_score if args.min_score is not None else profile.min_score
        eval_report = asyncio.run(
            EvaluateRetrieval(
                search_corpus, retrieval_mode=retrieval_mode, min_score=min_score, profile=args.profile
            ).run(cases)
        )
        if args.write_report:
            write_retrieval_eval_report(eval_report, Path(args.write_report))
        if args.json:
            print(json.dumps(_jsonable(asdict(eval_report)), indent=2, sort_keys=True))
        else:
            print(
                f"profile={eval_report.profile} retrieval_mode={eval_report.retrieval_mode} "
                f"cases={eval_report.cases} answerable={eval_report.answerable_cases} "
                f"unanswerable={eval_report.unanswerable_cases} hit_rate={eval_report.hit_rate:.3f} "
                f"mrr={eval_report.mean_reciprocal_rank:.3f} "
                f"unanswerable_success_rate={eval_report.unanswerable_success_rate:.3f} "
                f"abstention_rate={eval_report.abstention_rate:.3f}"
            )
            for result in eval_report.results:
                status = "PASS" if result.hit else "FAIL"
                retrieved = ",".join(result.retrieved_document_ids[: result.top_k]) or "none"
                expected = ",".join(result.expected_document_ids) or "none"
                print(
                    f"{status}: {result.case_id} expected={expected} retrieved={retrieved} "
                    f"rr={result.reciprocal_rank:.3f} max_score={result.max_score:.3f} "
                    f"abstained={str(result.abstained).lower()}"
                )
        if not _retrieval_eval_passed(
            report=eval_report,
            min_hit_rate=min_hit_rate,
            min_mrr=min_mrr,
            min_unanswerable_success=min_unanswerable_success,
        ):
            return 1
        return 0

    if args.command == "eval-matrix":
        try:
            chunks = asyncio.run(index_store.read_chunks())
            cases = load_retrieval_eval_cases(Path(args.dataset))
            search_corpus = asyncio.run(build_local_search_corpus(chunks))
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1

        selected_rows = set(args.row)
        matrix_rows = [
            row for row in list_retrieval_eval_matrix_rows() if not selected_rows or row.name in selected_rows
        ]
        entries = []
        matrix_passed = True
        for row in matrix_rows:
            profile = resolve_retrieval_eval_row(row)
            report = asyncio.run(
                EvaluateRetrieval(
                    search_corpus,
                    retrieval_mode=profile.retrieval_mode,
                    min_score=profile.min_score,
                    profile=profile.name,
                ).run(cases)
            )
            passed = _retrieval_eval_passed(
                report=report,
                min_hit_rate=profile.min_hit_rate,
                min_mrr=profile.min_mrr,
                min_unanswerable_success=profile.min_unanswerable_success,
            )
            matrix_passed = matrix_passed and passed
            entry = {
                "row": row.name,
                "passed": passed,
                "profile": report.profile,
                "retrieval_mode": report.retrieval_mode,
                "min_hit_rate": profile.min_hit_rate,
                "min_mrr": profile.min_mrr,
                "min_unanswerable_success": profile.min_unanswerable_success,
                "min_score": profile.min_score,
                "cases": report.cases,
                "answerable_cases": report.answerable_cases,
                "unanswerable_cases": report.unanswerable_cases,
                "hit_rate": report.hit_rate,
                "mean_reciprocal_rank": report.mean_reciprocal_rank,
                "unanswerable_success_rate": report.unanswerable_success_rate,
                "abstention_rate": report.abstention_rate,
            }
            entries.append(entry)
            if not args.json:
                status = "PASS" if passed else "FAIL"
                print(
                    f"{status}: row={row.name} profile={report.profile} "
                    f"retrieval_mode={report.retrieval_mode} cases={report.cases} "
                    f"hit_rate={report.hit_rate:.3f} mrr={report.mean_reciprocal_rank:.3f} "
                    f"unanswerable_success_rate={report.unanswerable_success_rate:.3f} "
                    f"abstention_rate={report.abstention_rate:.3f}"
                )

        matrix_report = {
            "generated_at": datetime.now(UTC).isoformat(),
            "dataset": str(Path(args.dataset)),
            "passed": matrix_passed,
            "rows": entries,
        }
        if args.write_report:
            write_retrieval_eval_matrix_report(matrix_report, Path(args.write_report))
        if args.json:
            print(json.dumps(_jsonable(matrix_report), indent=2, sort_keys=True))
        elif args.write_report:
            print(f"report={args.write_report}")
        return 0 if matrix_passed else 1

    if args.command == "stale-report":
        try:
            stale_report = asyncio.run(BuildStaleReport(index_store).run())
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        if args.json:
            print(json.dumps(_jsonable(asdict(stale_report)), indent=2, sort_keys=True))
            return 0
        print(f"checked={stale_report.checked} stale={len(stale_report.stale)}")
        for item in stale_report.stale:
            review_after = item.review_after.isoformat() if item.review_after else "missing"
            days_overdue = item.days_overdue if item.days_overdue is not None else "n/a"
            print(
                f"- {item.document_id}: review_after={review_after} "
                f"days_overdue={days_overdue} change_frequency={item.change_frequency or 'unknown'} reason={item.reason}"
            )
        return 0

    if args.command == "propose-doc-update":
        try:
            proposal, md_path, json_path = asyncio.run(
                ProposeDocumentationUpdate(index_store, Path(args.proposals_dir)).run(
                    document_id=args.document_id,
                    reason=args.reason,
                    source_hint=args.source_hint,
                    urgency=args.urgency,
                    proposed_change=args.proposed_change,
                )
            )
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}")
            return 1
        except Exception as exc:
            print(f"ERROR: {exc}")
            return 1
        print(f"proposal={proposal.id} status={proposal.status}")
        print(f"markdown={md_path}")
        print(f"json={json_path}")
        return 0

    if args.command == "capabilities":
        capabilities = build_capabilities_manifest()
        if args.json:
            print(json.dumps(_jsonable(capabilities), indent=2, sort_keys=True))
            return 0
        print(f"name={capabilities['name']}")
        print("retrieval_modes=" + ",".join(capabilities["retrieval_modes"]))
        print("tools=" + ",".join(capabilities["mcp"]["tools"]))
        print("profiles=" + ",".join(profile["name"] for profile in capabilities["retrieval_eval_profiles"]))
        print("matrix_rows=" + ",".join(row["row"] for row in capabilities["retrieval_eval_matrix_rows"]))
        return 0

    if args.command == "serve-mcp":
        try:
            from agentic_book.interfaces.mcp.server import run_mcp_server
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 1
        try:
            run_mcp_server(
                content_root=str(config.content_root),
                data_dir=str(config.data_dir),
                transport=config.mcp_transport,
                host=config.mcp_host,
                port=config.mcp_port,
            )
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 1
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _add_filter_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--type", dest="types", action="append", default=[], help="Filter by document type")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Filter by tag")
    parser.add_argument("--domain", dest="domains", action="append", default=[], help="Filter by domain")


def _filters_from_args(args: argparse.Namespace) -> RetrievalFilters:
    return RetrievalFilters(type=args.types, domain=args.domains, tags=args.tags)


def _print_results(results: list[RetrievalResult]) -> None:
    for index, result in enumerate(results, start=1):
        heading = f" | {result.section_heading}" if result.section_heading else ""
        print(f"{index}. {result.document_id}{heading} score={result.score:.3f} chunk={result.chunk_id}")
        print(f"   {result.text.splitlines()[-1][:180]}")
    print(f"results={len(results)}")


def _retrieval_eval_passed(
    *,
    report: RetrievalEvalReport,
    min_hit_rate: float,
    min_mrr: float,
    min_unanswerable_success: float,
) -> bool:
    return (
        report.hit_rate >= min_hit_rate
        and report.mean_reciprocal_rank >= min_mrr
        and report.unanswerable_success_rate >= min_unanswerable_success
    )


def _jsonable(value: object) -> object:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
