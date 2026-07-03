# agentic-book

Agentic Book is a local, agent-friendly knowledge scaffold for LLM agent architecture topics. It stores curated Markdown documents under `content/`, builds a local retrieval index, and exposes the corpus through a read-only MCP server for agents such as Codex, Claude Code, IDE assistants, or custom multi-agent systems.

The current corpus includes curated material about MCP, FastMCP, retrieval patterns, and an actionable enterprise playbook for making SQL databases consumable by LLM agents.

## Quick Start

These steps take a fresh checkout to a running MCP server.

```bash
git clone git@github.com:eramireztorres/agentic-book.git
cd agentic-book

python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev,mcp]"
```

Validate the curated Markdown corpus:

```bash
agentic-book --content-root content validate-content --strict-freshness
```

Expected output today:

```text
checked=19 issues=0 ok=true
```

Build the local index:

```bash
agentic-book --content-root content --data-dir .agentic-book-data ingest
```

Expected output today:

```text
dry_run=false documents_seen=19 chunks_planned=119 documents_indexed=19 chunks_indexed=119 documents_changed=19 documents_unchanged=0 documents_removed=0 manifest_uri=file://.../ingestion_manifest.json issues=0
```

Try retrieval before starting MCP:

```bash
agentic-book --data-dir .agentic-book-data search "SQL agents MCP governance" --retrieval-mode hybrid --top-k 5
agentic-book --data-dir .agentic-book-data fusion-search --query "SQL agent security" --query "MCP data server" --final-top-k 5
agentic-book --data-dir .agentic-book-data get-document playbook.sql-agent-enterprise
```

Start the MCP server over stdio:

```bash
agentic-book --content-root content --data-dir .agentic-book-data serve-mcp --transport stdio
```

For local HTTP testing instead:

```bash
agentic-book --content-root content --data-dir .agentic-book-data serve-mcp --transport http --host 127.0.0.1 --port 8000
```

The HTTP endpoint is served at:

```text
http://127.0.0.1:8000/mcp
```

Before wiring an MCP client, confirm the executable and index exist:

```bash
test -x /home/erick/repo/agentic-book/.venv/bin/agentic-book
agentic-book --data-dir .agentic-book-data get-document playbook.sql-agent-enterprise
```

If the first command fails, run the Quick Start install steps first. If the second command fails with an index error, run the ingest command again.

## Connect From Codex

Codex supports MCP servers through `config.toml`. The Codex CLI and IDE extension share this configuration. For a project-scoped setup, create or edit `.codex/config.toml` in this repository after the project is trusted.

Use absolute paths so Codex can launch the server even when its process environment does not have your virtualenv on `PATH`:

```toml
[mcp_servers.agentic_book]
command = "/home/erick/repo/agentic-book/.venv/bin/agentic-book"
args = [
  "--content-root", "/home/erick/repo/agentic-book/content",
  "--data-dir", "/home/erick/repo/agentic-book/.agentic-book-data",
  "serve-mcp",
  "--transport", "stdio",
]
cwd = "/home/erick/repo/agentic-book"
startup_timeout_sec = 20
tool_timeout_sec = 60
```

Then restart Codex or open a new Codex session and run `/mcp` in the Codex TUI to confirm that `agentic_book` is connected.

You can also add the server through the Codex CLI using the same command shape:

```bash
codex mcp add agentic_book -- /home/erick/repo/agentic-book/.venv/bin/agentic-book \
  --content-root /home/erick/repo/agentic-book/content \
  --data-dir /home/erick/repo/agentic-book/.agentic-book-data \
  serve-mcp --transport stdio
```

If Codex reports `MCP startup failed: No such file or directory`, the configured `command` path does not exist from Codex's point of view. Recreate the environment and reinstall the package:

```bash
cd /home/erick/repo/agentic-book
python -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e ".[mcp]"
.venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
```

Then start a new Codex session and run `/mcp` again.

## Connect From Claude Code

Claude Code can consume the same stdio MCP server. If you use a project MCP config, add a server entry like this, using absolute paths:

```json
{
  "mcpServers": {
    "agentic-book": {
      "command": "/home/erick/repo/agentic-book/.venv/bin/agentic-book",
      "args": [
        "--content-root", "/home/erick/repo/agentic-book/content",
        "--data-dir", "/home/erick/repo/agentic-book/.agentic-book-data",
        "serve-mcp",
        "--transport", "stdio"
      ]
    }
  }
}
```

If you prefer Claude Code's CLI MCP manager, use the equivalent `claude mcp` command for your installed version and pass the same executable and arguments shown above. Restart Claude Code after changing MCP configuration.

## What Agents Should Call

The MCP server is read-only. It exposes:

| MCP surface | Purpose |
|---|---|
| `corpus_manifest` tool | Inspect corpus size, freshness, retrieval modes, eval summaries, tools, resources, and prompts. |
| `search` tool | Retrieve ranked chunks with `lexical`, `vector`, or `hybrid` mode, optional filters, and optional `min_score` abstention. |
| `fusion_search` tool | Send multiple subqueries and merge results with Reciprocal Rank Fusion. |
| `get_document` tool | Fetch a complete curated document by canonical `document_id`. |
| `agentic-book://manifest` resource | Read the manifest as an MCP resource. |
| `agentic-book://documents/{document_id}` resource | Read a complete document as an MCP resource. |
| `summarize_with_citations` prompt | Ask the agent to summarize a document with citations. |
| `compare_concepts` prompt | Ask the agent to compare two concepts using retrieval first. |

Recommended agent flow:

```text
1. Call corpus_manifest.
2. Use search or fusion_search with a focused query.
3. Call get_document for the strongest evidence.
4. Answer with document ids, section names, freshness, and limitations.
```

For weak matches, use `search` with `min_score`. If the response includes `abstained=true`, the agent should not answer from that context unless it intentionally lowers the threshold or asks for better documentation.

## Smoke Test Prompts

After connecting the MCP server from Codex, Claude Code, or another MCP client, try these prompts to verify the main MCP surfaces:

```text
Use the agentic_book MCP server. Call corpus_manifest and tell me how many documents and chunks are indexed.
```

```text
Use agentic_book. Search for "SQL agents MCP governance" and return the top 5 document_ids with short reasons.
```

```text
Use agentic_book. Run fusion_search with these subqueries: "SQL agent security", "MCP data server", "semantic layer BI". Then call get_document for the strongest result and summarize it.
```

```text
Use agentic_book. Retrieve playbook.sql-agent-enterprise and summarize the recommendations for executives, architects, and developers.
```

```text
Use agentic_book. What risks should an enterprise consider before exposing a SQL database to LLM agents? Cite the document_ids used.
```

```text
Use agentic_book. Search for "quantum gardening zebra orchid compost" with min_score 999 and explain whether the server abstained.
```

These prompts exercise `corpus_manifest`, `search`, `fusion_search`, `get_document`, and search abstention.

## Add New Curated Markdown

Add curated files under `content/`, not only under `docs/`. The `docs/` directory can hold long human-facing sources; `content/` is the agent-consumable corpus.

Common folders:

```text
content/concepts/
content/patterns/
content/playbooks/
content/platforms/
content/case-studies/
content/checklists/
content/risks/
content/glossary/
content/standards/
content/tools/
```

Directory choice is mostly for humans and maintainers. Retrieval mainly uses each document's frontmatter: `type`, `domain`, `tags`, `related`, and the document text. Keep the directory and `type` aligned so the corpus stays easy to review.

Use these conventions:

| Directory | Use for |
|---|---|
| `content/playbooks/` | End-to-end guides, operating models, roadmaps, handoffs. |
| `content/patterns/` | Reusable architecture, retrieval, security, ingestion, deployment, or governance patterns. |
| `content/checklists/` | Readiness checks, pre-launch checks, recurring operations checks. |
| `content/risks/` | Risks, failure modes, mitigations, controls, threat scenarios. |
| `content/case-studies/` | Concrete examples, reference implementations, scenario walkthroughs. |
| `content/concepts/` | Core definitions that other documents depend on. |
| `content/platforms/` | Vendor, framework, SDK, or runtime guidance. |
| `content/glossary/` | Terms and short definitions. |
| `content/standards/` | Rules, policies, normative criteria, if-then rules. |
| `content/tools/` | Tool contracts, MCP tool descriptions, API wrapper contracts. |

### Split Source Documents Semantically

Do not turn a long PDF into one huge Markdown, and do not split it by page ranges. Split it into semantic units an agent would naturally retrieve.

Good split:

```text
docs/source-playbook.pdf
content/playbooks/source-overview.md
content/patterns/source-ingestion-pattern.md
content/patterns/source-security-pattern.md
content/checklists/source-readiness.md
content/risks/source-risk-register.md
content/glossary/source-glossary.md
```

Bad split:

```text
content/playbooks/source-pages-1-to-5.md
content/playbooks/source-pages-6-to-10.md
content/playbooks/source-pages-11-to-15.md
```

A good curated Markdown file should have one clear purpose, enough context to stand alone, and section headings that make the generated chunks meaningful. As a rule of thumb, prefer 500-1,500 words per document, but let semantic boundaries win over exact length.

Use this frontmatter shape:

```markdown
---
id: "pattern.example"
title: "Example Pattern"
type: "pattern"
domain: ["agents", "mcp", "enterprise-data"]
audience: ["architect", "engineer", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-07-02"
source_quality: "curated"
source_urls:
  - "docs/path/to/source.md"
source_type: "derived"
upstream_version: "2026-07-02"
last_checked: "2026-07-02"
review_after: "2026-10-02"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["mcp", "agents"]
related:
  - "concept.mcp"
---

# Example Pattern

Write one coherent, self-contained document. The ingestor will split it into section-aware chunks.
```

Rules that validation enforces:

- `id` must be unique.
- `related` ids must exist in the corpus.
- `type`, `maturity`, `status`, `source_quality`, `source_type`, and `change_frequency` must use supported values.
- Freshness fields are required when running `--strict-freshness`.
- Non-internal sources need at least one `source_urls` entry.

After adding or replacing Markdown:

```bash
agentic-book --content-root content validate-content --strict-freshness
agentic-book --content-root content ingest --dry-run
agentic-book --content-root content --data-dir .agentic-book-data ingest
agentic-book --data-dir .agentic-book-data eval-matrix
```

If retrieval rankings changed intentionally, update `evals/retrieval/ground_truth.json` and rerun `eval-matrix`.

If an MCP client such as Codex or Claude Code already has the stdio server running, start a new client session after re-ingesting so it launches a fresh MCP process over the updated index. For HTTP/Docker, restart the service after changing content unless your deployment explicitly runs ingestion on startup.

## Docker HTTP MCP

Docker is useful when you want an HTTP MCP endpoint without installing the package in your host environment.

```bash
docker compose up --build
```

The compose service:

- validates and ingests content at startup with `AGENTIC_BOOK_AUTO_INGEST=true`;
- stores generated indexes in the `agentic-book-data` Docker volume;
- serves MCP over HTTP at `http://127.0.0.1:8000/mcp`.

## Runtime Configuration

The CLI and container read these environment variables through `RuntimeConfig`:

```bash
AGENTIC_BOOK_CONTENT_ROOT=content
AGENTIC_BOOK_DATA_DIR=.agentic-book-data
AGENTIC_BOOK_STORAGE_BACKEND=filesystem
AGENTIC_BOOK_INDEX_BACKEND=json+lexical
AGENTIC_BOOK_EMBEDDING_PROVIDER=none
AGENTIC_BOOK_VECTOR_STORE=memory
AGENTIC_BOOK_MCP_TRANSPORT=stdio
AGENTIC_BOOK_MCP_HOST=127.0.0.1
AGENTIC_BOOK_MCP_PORT=8000
AGENTIC_BOOK_AUTO_INGEST=false
```

Implemented local backends:

- content store: `filesystem`;
- index store: `json+lexical`;
- vector store: `memory` by default, optional `lancedb`.

To use LanceDB locally:

```bash
python -m pip install -e ".[vector-lancedb]"
AGENTIC_BOOK_VECTOR_STORE=lancedb agentic-book --content-root content --data-dir .agentic-book-data ingest
AGENTIC_BOOK_VECTOR_STORE=lancedb agentic-book --data-dir .agentic-book-data search "hybrid retrieval" --retrieval-mode vector --top-k 3
```

The domain and application layers are written behind ports so later S3, OpenSearch, Qdrant, Bedrock, OpenAI embeddings, or rerankers can be added as infrastructure adapters rather than domain rewrites.

## Retrieval Evaluation

The baseline dataset lives at `evals/retrieval/ground_truth.json`.

```bash
agentic-book --data-dir .agentic-book-data eval-matrix --write-report evals/reports/matrix.json
agentic-book --data-dir .agentic-book-data eval-retrieval --profile guarded --write-report evals/reports/latest.json
```

`eval-matrix` runs the standard baseline, vector, and guarded profiles. It reports hit rate, mean reciprocal rank, unanswerable success rate, and abstention rate. CI uses these checks to catch retrieval quality regressions.

## Freshness Workflow

Canonical documents include freshness metadata such as `source_urls`, `source_type`, `last_checked`, `review_after`, and `change_frequency`.

```bash
agentic-book --data-dir .agentic-book-data stale-report
agentic-book --data-dir .agentic-book-data propose-doc-update concept.mcp --reason "Possible upstream protocol change"
```

`propose-doc-update` creates local review artifacts under `.proposals/documentation-updates/`. It does not modify canonical content directly.

## Development Checks

```bash
ruff check src tests
ruff format --check src tests
mypy src
python -m pytest
```

The current test suite includes an HTTP MCP smoke test that starts the server on a free local port and calls `corpus_manifest` plus guarded `search` through a FastMCP client. Tests that require `fastmcp` are skipped if the `mcp` extra is not installed.

## Current Implementation Status

Implemented today:

- Python package scaffold under `src/agentic_book`.
- Domain models and ports for content objects, documents, chunks, retrieval, embeddings, and vector stores.
- Local filesystem content store.
- Markdown frontmatter parser for the constrained metadata format.
- Corpus validation, dry-run ingestion, incremental ingestion, freshness reporting, and local update proposal use cases.
- CLI entry point for validation, ingestion, retrieval, evaluation, freshness review, and MCP serving.
- GitHub Actions CI and Docker runtime for local HTTP MCP deployment.
- Local deterministic vector retrieval, optional LanceDB vector store, and hybrid lexical/vector retrieval by RRF.
- Retrieval abstention thresholds, JSON eval reports, and enriched MCP corpus manifest.
- Curated canonical Markdown under `content/`, including the SQL-agent enterprise playbook corpus.
