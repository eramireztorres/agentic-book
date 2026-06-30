# agentic-book
Updated and agentic-friendly book on LLM agent design and related topics.

## Current implementation status

This repository now contains the first implementation slice of the roadmap:

- Python package scaffold under `src/agentic_book`.
- Domain models and ports for content objects, documents, chunks, and retrieval contracts.
- Local filesystem content store.
- Markdown frontmatter parser for the project's constrained metadata format.
- Corpus validation, dry-run ingestion, freshness reporting, and local update proposal use cases.
- CLI entry point for validation, ingestion, retrieval, freshness review, and MCP serving.
- GitHub Actions CI and Docker runtime for local HTTP MCP deployment.
- Runtime configuration from environment variables for local and future cloud wiring.
- Incremental ingestion state that reuses unchanged documents and removes deleted sources from the index.
- Retrieval evaluation dataset and CLI baseline for hit rate and MRR.
- Local deterministic vector retrieval and hybrid lexical/vector retrieval by RRF.
- Retrieval abstention thresholds, JSON eval reports, and enriched MCP corpus manifest.
- Initial canonical Markdown fixtures under `content/`.

## Local setup

```bash
python -m pip install -e ".[dev]"
```

## Useful commands

```bash
agentic-book --content-root content validate-content
agentic-book --content-root content validate-content --strict-freshness
agentic-book --content-root content ingest --dry-run
agentic-book --content-root content ingest
agentic-book search "Streamable HTTP MCP" --top-k 3
agentic-book search "hybrid retrieval" --retrieval-mode vector --top-k 3
agentic-book search "hybrid retrieval" --retrieval-mode hybrid --top-k 3
agentic-book fusion-search --query "Streamable HTTP" --query "MCP resources" --final-top-k 3
agentic-book get-document concept.mcp
agentic-book eval-retrieval
agentic-book eval-matrix
agentic-book capabilities --json
agentic-book stale-report
agentic-book propose-doc-update concept.mcp --reason "Possible upstream protocol change"
agentic-book serve-mcp --transport stdio
docker compose up --build
ruff check src tests
ruff format --check src tests
mypy src
python -m pytest
```

Expected current output:

```text
checked=4 issues=0 ok=true
dry_run=true documents_seen=4 chunks_planned=13 documents_indexed=0 chunks_indexed=0 documents_changed=4 documents_unchanged=0 documents_removed=0 manifest_uri=none issues=0
dry_run=false documents_seen=4 chunks_planned=13 documents_indexed=4 chunks_indexed=13 documents_changed=4 documents_unchanged=0 documents_removed=0 manifest_uri=file://.../ingestion_manifest.json issues=0
profile=baseline retrieval_mode=lexical cases=6 answerable=5 unanswerable=1 hit_rate=1.000 mrr=1.000 unanswerable_success_rate=1.000 abstention_rate=0.167
checked=4 stale=0
proposal=YYYY-MM-DD-concept.mcp status=needs-human-review
```

## Freshness workflow

Canonical documents can include freshness metadata such as `source_urls`, `source_type`, `last_checked`, `review_after`, and `change_frequency`. Use strict validation in CI once the corpus is fully migrated:

```bash
agentic-book --content-root content validate-content --strict-freshness
```

`stale-report` reads the generated local index and reports documents whose `review_after` date has elapsed. `propose-doc-update` creates local artifacts under `.proposals/documentation-updates/`; these are review inputs, not canonical content changes.

## Runtime configuration

The local CLI and container read these environment variables through `RuntimeConfig`:

```bash
AGENTIC_BOOK_CONTENT_ROOT=content
AGENTIC_BOOK_DATA_DIR=.agentic-book-data
AGENTIC_BOOK_STORAGE_BACKEND=filesystem
AGENTIC_BOOK_INDEX_BACKEND=json+lexical
AGENTIC_BOOK_EMBEDDING_PROVIDER=none
AGENTIC_BOOK_MCP_TRANSPORT=http
AGENTIC_BOOK_MCP_HOST=127.0.0.1
AGENTIC_BOOK_MCP_PORT=8000
AGENTIC_BOOK_AUTO_INGEST=false
```

The only implemented local backends are `filesystem` and `json+lexical`; the explicit settings make later S3/OpenSearch/Qdrant wiring a configuration and adapter problem rather than a domain rewrite.

## Incremental ingestion

`agentic-book ingest` writes `ingestion_state.json` next to the generated index. On subsequent runs it compares source hashes, reuses unchanged documents and chunks, and drops deleted Markdown sources from the generated index. The command reports `documents_changed`, `documents_unchanged`, and `documents_removed` for operational visibility.

## Retrieval modes

The current local runtime supports three retrieval modes without external services:

- `lexical`: deterministic BM25-like lexical baseline.
- `vector`: deterministic local hashing embeddings plus in-memory vector search.
- `hybrid`: lexical and vector rankings fused with Reciprocal Rank Fusion.

The vector adapter is intentionally local and replaceable. It exists to prove the domain/application contracts before adding LanceDB, Qdrant, OpenSearch, Bedrock, OpenAI embeddings, or rerankers.

## Retrieval evaluation

The baseline dataset lives at `evals/retrieval/ground_truth.json`. After ingesting content, run:

```bash
agentic-book --content-root content --data-dir .agentic-book-data eval-matrix --write-report evals/reports/matrix.json
agentic-book --content-root content --data-dir .agentic-book-data eval-retrieval --profile guarded --write-report evals/reports/latest.json
```

The command reports answerable `hit_rate`, `mean_reciprocal_rank`, unanswerable success rate, and abstention rate. Use `--profile baseline` for the default lexical quality gate, `--profile guarded` for hybrid retrieval with abstention and unanswerable-case gating, and `--profile custom` when explicitly calibrating modes or thresholds. Individual flags such as `--retrieval-mode`, `--min-score`, `--min-hit-rate`, `--min-mrr`, and `--min-unanswerable-success` override profile defaults.

`eval-matrix` runs the standard baseline, vector, and guarded rows and writes one aggregate JSON report. Use `--row baseline`, `--row vector`, or `--row guarded` to run a subset while calibrating. CI runs `eval-matrix` plus a latest guarded report so retrieval quality regressions are caught before adding external vector stores, rerankers, or GraphRAG.

`agentic-book capabilities --json` prints the same machine-readable capability contract without starting MCP. It includes retrieval modes, MCP tools/resources/prompts, abstention semantics, evaluation profiles, matrix rows, and cloud-ready adapter boundaries.

The MCP `corpus_manifest` includes ingestion state, freshness summary, active retrieval backends, the shared capability contract, available evaluation profiles, matrix rows, a summary of `evals/reports/latest.json`, and a summary of `evals/reports/matrix.json` when present.

The MCP `search` tool also accepts `min_score`. When no candidates are found, or when the best candidate is below that threshold, it returns no visible results and includes `abstained=true`, `reason` (`"no_results"` or `"below_min_score"`), `max_score`, `min_score`, and `candidate_count`. Agents should treat this as an instruction to avoid answering from weak context and either ask for better documentation, lower the threshold intentionally, or escalate to a documentation update workflow.

## Docker and CI

Local HTTP MCP runtime:

```bash
docker compose up --build
```

The container validates freshness metadata and ingests canonical content at startup when `AGENTIC_BOOK_AUTO_INGEST=true`. It serves MCP over HTTP on port `8000` and stores generated indexes in the `agentic-book-data` volume.

The GitHub Actions workflow in `.github/workflows/ci.yml` runs Ruff linting and format checks, Mypy type checks, strict content validation, local index build, runtime capability inspection, retrieval matrix evaluation, latest guarded report generation, tests, MCP surface inspection, and Docker image build without publishing. This keeps the image ready for a later ECR/Fargate workflow while avoiding registry credentials in the initial CI.

## MCP support

The MCP server is optional and requires the `mcp` extra:

```bash
python -m pip install -e ".[mcp]"
agentic-book --content-root content ingest
agentic-book serve-mcp --transport stdio
```

For local HTTP testing:

```bash
agentic-book --content-root content ingest
agentic-book serve-mcp --transport http --host 127.0.0.1 --port 8000
```

The test suite includes an HTTP MCP smoke test that starts this server on a free local port and calls `corpus_manifest` plus guarded `search` through the FastMCP client.

To inspect the MCP surface after installing the extra:

```bash
fastmcp list src/agentic_book/interfaces/mcp/server.py --resources --prompts --json
```
