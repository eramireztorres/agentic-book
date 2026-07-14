from pathlib import Path


def test_ci_workflow_runs_quality_gates_cross_platform_setup_and_docker_smoke() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "branches: [master, main]" in workflow
    assert "ruff check src tests" in workflow
    assert "ruff format --check src tests" in workflow
    assert "mypy src" in workflow
    assert "agentic-book --content-root content validate-content --strict-freshness" in workflow
    assert "agentic-book --content-root content --data-dir .agentic-book-data ingest" in workflow
    assert "agentic-book capabilities --json" in workflow
    assert "eval-matrix --write-report evals/reports/matrix.json" in workflow
    assert "eval-retrieval --profile guarded --write-report evals/reports/latest.json" in workflow
    assert "eval-fusion --write-report evals/reports/fusion.json" in workflow
    assert "python -m pytest" in workflow
    assert "fastmcp list src/agentic_book/interfaces/mcp/server.py --resources --prompts --json" in workflow
    assert "os: [ubuntu-latest, macos-latest, windows-latest]" in workflow
    assert "./scripts/setup.sh" in workflow
    assert "./scripts/ingest.sh" in workflow
    assert ".\\scripts\\setup.ps1" in workflow
    assert ".\\scripts\\ingest.ps1" in workflow
    assert "docker/build-push-action" in workflow
    assert "push: false" in workflow
    assert "AGENTIC_BOOK_HOST_PORT=18000 docker compose up --detach --no-build" in workflow


def test_native_scripts_separate_install_from_ingest_and_do_not_require_activation() -> None:
    unix_setup = Path("scripts/setup.sh").read_text(encoding="utf-8")
    windows_setup = Path("scripts/setup.ps1").read_text(encoding="utf-8")
    unix_ingest = Path("scripts/ingest.sh").read_text(encoding="utf-8")
    windows_ingest = Path("scripts/ingest.ps1").read_text(encoding="utf-8")

    assert "sys.version_info < (3, 11)" in unix_setup
    assert "sys.version_info < (3, 11)" in windows_setup
    assert 'pip install -e "$repo_root[mcp]"' in unix_setup
    assert 'pip install -e "$RepoRoot[mcp]"' in windows_setup
    assert "validate-content --strict-freshness" not in unix_setup
    assert "validate-content --strict-freshness" not in windows_setup
    assert "validate-content --strict-freshness" in unix_ingest
    assert "validate-content --strict-freshness" in windows_ingest
    assert "get-document playbook.sql-agent-enterprise" in unix_ingest
    assert "get-document playbook.sql-agent-enterprise" in windows_ingest
    assert "source .venv/bin/activate" not in unix_setup
    assert "Activate.ps1" not in windows_setup


def test_docker_runtime_serves_http_mcp_with_auto_ingest_and_healthcheck() -> None:
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
    assert "127.0.0.1:${AGENTIC_BOOK_HOST_PORT:-8000}:8000" in compose
    assert "./content:/app/content:ro" in compose
    assert "healthcheck:" in compose
    assert "socket.create_connection" in compose
    assert "validate-content --strict-freshness" in entrypoint
    assert 'agentic-book --content-root "$content_root" --data-dir "$data_dir" ingest' in entrypoint


def test_spanish_readme_prioritizes_native_setup_then_docker_and_guides() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    native_heading = readme.index("## Inicio rápido: instalación nativa")
    docker_heading = readme.index("## Segunda opción: Docker")
    assert native_heading < docker_heading
    assert "### 2. Clona el repositorio y entra en la carpeta" in readme
    assert "git clone https://github.com/eramireztorres/agentic-book.git" in readme
    assert "cd agentic-book" in readme
    assert "### 3. Instala en Linux" in readme
    assert "### 4. Instala en macOS" in readme
    assert "### 5. Instala en Windows PowerShell" in readme
    assert "### 6. Prepara el índice local" in readme
    assert "./scripts/setup.sh" in readme
    assert "./scripts/ingest.sh" in readme
    assert "powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1" in readme
    assert "powershell -ExecutionPolicy Bypass -File .\\scripts\\ingest.ps1" in readme
    assert "## Alternativa manual para usuarios avanzados" in readme
    assert "No en la instalación nativa recomendada" in readme
    assert "serve-mcp --transport stdio" in readme
    assert "docker compose up --build -d" in readme
    assert "### 5. Detén el servidor Docker" in readme
    assert "docker compose down" in readme
    assert "docker compose down -v" in readme
    assert "codex mcp add agentic_book --url http://127.0.0.1:8000/mcp" in readme
    assert "claude mcp add --transport http agentic_book http://127.0.0.1:8000/mcp" in readme
    assert "No necesitas `OPENAI_API_KEY`" in readme
    assert "Preguntas para comprobar el RAG" in readme
    assert "Después de añadir, reemplazar o eliminar archivos en `content/`, actualiza el índice." in readme
    assert "docker compose restart agentic-book-mcp" in readme
    assert "Después abre una sesión nueva de Codex o Claude Code" in readme
    assert "/home/erick" not in readme

    for guide in (
        Path("docs/guias/instalacion-nativa.md"),
        Path("docs/guias/curacion-contenido.md"),
        Path("docs/guias/desarrollo.md"),
    ):
        assert guide.is_file()
