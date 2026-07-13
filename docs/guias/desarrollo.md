# Desarrollo, configuración y calidad

## Entorno de desarrollo

Instala Python 3.11 o superior y crea el entorno sin necesidad de activarlo:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,mcp]"
```

En Windows utiliza `py -3` y los ejecutables de `.venv\Scripts`.

## Checks locales

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src
.venv/bin/python -m pytest
```

Valida la calidad del corpus y el retrieval:

```bash
.venv/bin/agentic-book --content-root content validate-content --strict-freshness
.venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
.venv/bin/agentic-book --data-dir .agentic-book-data eval-matrix --write-report evals/reports/matrix.json
.venv/bin/agentic-book --data-dir .agentic-book-data eval-retrieval --profile guarded --write-report evals/reports/latest.json
.venv/bin/agentic-book --data-dir .agentic-book-data eval-fusion --write-report evals/reports/fusion.json
```

`eval-matrix` compara los perfiles baseline lexical, vector y guarded hybrid. `eval-fusion` comprueba casos multiquery fusionados mediante Reciprocal Rank Fusion. CI utiliza ambos para detectar regresiones.

## Configuración de runtime

| Variable | Valor local predeterminado |
|---|---|
| `AGENTIC_BOOK_CONTENT_ROOT` | `content` |
| `AGENTIC_BOOK_DATA_DIR` | `.agentic-book-data` |
| `AGENTIC_BOOK_STORAGE_BACKEND` | `filesystem` |
| `AGENTIC_BOOK_INDEX_BACKEND` | `json+lexical` |
| `AGENTIC_BOOK_EMBEDDING_PROVIDER` | `none` |
| `AGENTIC_BOOK_VECTOR_STORE` | `memory` |
| `AGENTIC_BOOK_MCP_TRANSPORT` | `stdio` |
| `AGENTIC_BOOK_MCP_HOST` | `127.0.0.1` |
| `AGENTIC_BOOK_MCP_PORT` | `8000` |
| `AGENTIC_BOOK_AUTO_INGEST` | `false` |

El almacenamiento local implementado utiliza filesystem, índices JSON/lexical y vectores deterministas en memoria. LanceDB es opcional:

```bash
.venv/bin/python -m pip install -e ".[vector-lancedb]"
AGENTIC_BOOK_VECTOR_STORE=lancedb .venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
```

Los puertos de dominio y aplicación permiten añadir adaptadores para S3, OpenSearch, Qdrant, embeddings gestionados o rerankers sin reescribir los casos de uso.

## Arquitectura

- `domain`: modelos y protocolos independientes de infraestructura.
- `application`: validación, ingesta, retrieval, evaluación y freshness.
- `infrastructure`: filesystem, persistencia, índices, datasets y vector stores.
- `interfaces`: CLI, wiring y servidor FastMCP.

El servidor MCP es de solo lectura. Las propuestas de actualización documental se guardan como artefactos locales y requieren revisión humana antes de modificar el corpus.

## CI y Docker

GitHub Actions ejecuta lint, formato, tipos, validación del corpus, ingesta, evaluaciones, tests y build de Docker. Los scripts de instalación se comprueban en Linux, macOS y Windows.

La imagen local sirve Streamable HTTP en el puerto 8000. Compose monta `content/` en solo lectura y persiste el índice en un volumen administrado por Docker.
