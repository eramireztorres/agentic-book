from pathlib import Path


def test_ci_workflow_runs_quality_gates_and_docker_build() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "ruff check src tests" in workflow
    assert "ruff format --check src tests" in workflow
    assert "mypy src" in workflow
    assert "agentic-book --content-root content validate-content --strict-freshness" in workflow
    assert "agentic-book --content-root content --data-dir .agentic-book-data ingest" in workflow
    assert "agentic-book capabilities --json" in workflow
    assert "eval-matrix --write-report evals/reports/matrix.json" in workflow
    assert "eval-retrieval --profile guarded --write-report evals/reports/latest.json" in workflow
    assert "python -m pytest" in workflow
    assert "fastmcp list src/agentic_book/interfaces/mcp/server.py --resources --prompts --json" in workflow
    assert "docker/build-push-action" in workflow
    assert "push: false" in workflow


def test_docker_runtime_serves_http_mcp_with_auto_ingest() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    entrypoint = Path("docker/entrypoint.sh").read_text(encoding="utf-8")

    assert "vector-lancedb = [" in pyproject
    assert "lancedb==0.29.2" in pyproject
    assert 'python -m pip install --root-user-action=ignore ".[mcp]"' in dockerfile
    assert "COPY evals ./evals" in dockerfile
    assert 'ENTRYPOINT ["agentic-book-entrypoint"]' in dockerfile
    assert '"serve-mcp", "--transport", "http"' in dockerfile
    assert "AGENTIC_BOOK_VECTOR_STORE: memory" in compose
    assert 'AGENTIC_BOOK_AUTO_INGEST: "true"' in compose
    assert '- "8000:8000"' in compose
    assert "validate-content --strict-freshness" in entrypoint
    assert 'agentic-book --content-root "$content_root" --data-dir "$data_dir" ingest' in entrypoint
