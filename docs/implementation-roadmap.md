---
title: "Roadmap de implementacion para Agentic Book"
status: "draft"
created: "2026-06-30"
source:
  - "docs/architecture-recommendations.md"
audience:
  - "implementation agents"
  - "maintainers"
  - "technical reviewers"
defaults:
  stack: "local-first Python"
  architecture: "clean/hexagonal pragmatic"
  ci: "GitHub Actions"
  cloud_target_reference: "AWS"
  mcp_transport:
    - "stdio"
    - "streamable-http"
---

# Roadmap de implementacion para Agentic Book

## 0. Objetivo y definicion de listo

El objetivo es implementar un scaffold local-first que permita servir un libro sobre agentes LLM y temas relacionados de forma amigable para agentes, principalmente mediante un MCP server read-only construido con FastMCP.

El sistema se considera listo para ser consumido por agentes cuando:

- Un agente puede descubrir el corpus, taxonomia, capacidades y rutas disponibles.
- Un agente puede recuperar evidencia desde Markdown canonico mediante busqueda lexical, vectorial e hibrida.
- Un agente puede ejecutar busqueda multi-query con Reciprocal Rank Fusion.
- Un agente puede recuperar documentos completos, secciones y metadata trazable.
- El MCP server expone tools, resources y prompts utiles, no solo tools de busqueda.
- La ingesta incremental evita reindexar contenido no modificado.
- Hay tests y evaluaciones basicas que protegen calidad de retrieval.
- El core del sistema no depende de FastMCP, LanceDB, Qdrant, OpenAI, Cohere ni otros proveedores concretos.

## 1. Decisiones base

Estas decisiones quedan fijadas para evitar que el agente implementador tenga que elegir.

- Lenguaje: Python.
- Packaging: `pyproject.toml` con layout `src/`.
- Arquitectura: Clean/Hexagonal pragmatica.
- Principios SOLID: aplicados via modelos puros, ports pequenos e infraestructura reemplazable.
- Contenido canonico: `content/`.
- Sintesis generada: `wiki/`.
- Skills: procedimientos operativos, no knowledge base principal.
- MCP: FastMCP como interfaz, no como core del dominio.
- Transporte MCP default: `stdio`.
- Transporte remoto/local persistente: Streamable HTTP en `/mcp`.
- Servidor MCP inicial: read-only.
- Admin/ingesta: CLI separado del MCP read-only.
- Retrieval inicial: lexical baseline, vector retrieval, hybrid retrieval, RRF.
- Retrieval avanzado: HyDE, GraphRAG, reranking y CRAG solo despues de evaluacion baseline.
- Vector store default para v1: LanceDB local si se prioriza cero infraestructura.
- Vector store secundario: Qdrant local adapter cuando se quiera acercar a produccion.
- Embeddings: adapter por port; no hardcodear proveedor en application.
- Reranker: adapter opcional; `none` debe funcionar siempre.
- Observabilidad: logs estructurados desde el primer MCP usable.
- Docker: construir una imagen reproducible para servir MCP por HTTP y ejecutar comandos CLI/admin.
- CI: GitHub Actions desde las primeras fases, empezando con validacion estatica, tests unitarios y build de imagen Docker sin publicacion.
- Portabilidad cloud: el core debe poder cambiar filesystem local por S3 y vector store local por OpenSearch/Qdrant/otro adapter sin tocar `domain/`, `application/` ni `interfaces/mcp/`.

## 2. Estructura objetivo del repositorio

Crear esta estructura durante las fases correspondientes, no toda de golpe si no hace falta.

```text
agentic-book/
  .github/
    workflows/
      ci.yml
  Dockerfile
  docker-compose.yml
  .dockerignore
  content/
    concepts/
    platforms/
    patterns/
    enterprise/
    playbooks/
  wiki/
    index.md
    log.md
    maps/
    entities/
    comparisons/
    contradictions/
  skills/
    ingest-book-source/
    maintain-agentic-wiki/
    evaluate-rag-quality/
    security-review-agentic-pattern/
  evals/
    retrieval/
      ground_truth.json
      queries.basic.json
      queries.multi_hop.json
      queries.unanswerable.json
    reports/
  src/
    agentic_book/
      domain/
        __init__.py
        errors.py
        models.py
        ports.py
        metadata_schema.py
      application/
        __init__.py
        ingest.py
        retrieve.py
        fusion.py
        manifests.py
        validation.py
      infrastructure/
        __init__.py
        blobstores/
        cloud/
        embeddings/
        filesystem/
        lexical/
        markdown/
        rerankers/
        vectorstores/
      interfaces/
        __init__.py
        cli/
        mcp/
      evaluation/
        __init__.py
        datasets.py
        metrics.py
        runners.py
  tests/
    unit/
    integration/
    contract/
    mcp/
  docs/
    architecture-recommendations.md
    implementation-roadmap.md
```

## 3. Arquitectura y reglas SOLID

### 3.1 Regla de dependencias

Las dependencias deben apuntar hacia dentro:

```text
interfaces -> application -> domain
infrastructure -> application/domain
```

Reglas:

- `domain/` no importa nada del proyecto salvo librerias estandar y, si se decide, Pydantic.
- `application/` depende de `domain.models` y `domain.ports`.
- `infrastructure/` implementa ports definidos en `domain/`.
- `interfaces/mcp/` llama casos de uso de `application/`.
- Ninguna tool MCP debe contener logica de parsing, ranking o storage.
- Ningun caso de uso debe depender directamente de `pathlib.Path`, S3, OpenSearch, LanceDB, Qdrant o APIs cloud; esas decisiones pertenecen a CLI/configuracion e infraestructura.

### 3.2 Single Responsibility

Cada modulo debe tener una razon clara de cambio:

- `metadata_schema.py`: contrato de frontmatter.
- `markdown/`: parseo y extraccion de headings.
- `ingest.py`: caso de uso de ingesta.
- `retrieve.py`: caso de uso de busqueda.
- `fusion.py`: fusion de rankings.
- `vectorstores/`: adaptadores concretos.
- `interfaces/mcp/`: exposicion MCP.

### 3.3 Open/Closed

El sistema debe permitir anadir:

- otro vector store;
- otro proveedor de embeddings;
- otro reranker;
- otro parser de documentos;
- otra interfaz, por ejemplo REST o CLI;

sin modificar los casos de uso centrales mas alla de wiring/configuracion.

### 3.4 Interface Segregation

Evitar una interfaz gigante tipo `RAGService`. Usar ports pequenos.

```python
from typing import Protocol

class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

class Reranker(Protocol):
    async def rerank(self, query: str, results: list["RetrievalResult"]) -> list["RetrievalResult"]:
        ...
```

### 3.5 Dependency Inversion

Los casos de uso reciben ports en el constructor.

```python
class SearchCorpus:
    def __init__(
        self,
        lexical_index: LexicalIndex,
        vector_store: VectorStore,
        reranker: Reranker | None = None,
    ) -> None:
        self.lexical_index = lexical_index
        self.vector_store = vector_store
        self.reranker = reranker
```

## 4. Modelos y contratos de dominio

Implementar modelos estables antes de infraestructura.

### 4.1 Tipos base

Modelos minimos:

- `DocumentId`
- `SectionId`
- `ChunkId`
- `DocumentMetadata`
- `Document`
- `Section`
- `Chunk`
- `RetrievalQuery`
- `RetrievalFilters`
- `RetrievalResult`
- `CorpusManifest`
- `IngestionManifest`

Ejemplo orientativo:

```python
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

ContentLayer = Literal["canonical", "wiki"]
DocumentType = Literal[
    "concept",
    "pattern",
    "platform",
    "playbook",
    "case-study",
    "checklist",
    "risk",
    "tool",
    "standard",
    "glossary",
]

class DocumentMetadata(BaseModel):
    id: str
    title: str
    type: DocumentType
    domain: list[str] = Field(default_factory=list)
    audience: list[str] = Field(default_factory=list)
    maturity: Literal["experimental", "emerging", "production", "legacy"]
    last_reviewed: date
    source_quality: Literal["primary", "curated", "community", "vendor", "internal"]
    tags: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    layer: ContentLayer = "canonical"
```

### 4.2 Ports minimos

```python
from typing import Protocol

class MarkdownParser(Protocol):
    def parse(self, source: "ContentObject") -> "Document":
        ...

class ContentObjectStore(Protocol):
    async def list_objects(self, prefix: str, layer: str = "canonical") -> list["ContentObjectRef"]:
        ...

    async def get_object(self, ref: "ContentObjectRef") -> "ContentObject":
        ...

class DocumentRepository(Protocol):
    async def list_documents(self, layer: str | None = None) -> list["Document"]:
        ...

    async def get_document(self, document_id: str) -> "Document | None":
        ...

class LexicalIndex(Protocol):
    async def upsert(self, chunks: list["Chunk"]) -> None:
        ...

    async def search(self, query: "RetrievalQuery") -> list["RetrievalResult"]:
        ...

class VectorStore(Protocol):
    async def upsert(self, chunks: list["EmbeddedChunk"]) -> None:
        ...

    async def search(self, query: "RetrievalQuery", query_vector: list[float]) -> list["RetrievalResult"]:
        ...
```

Acceptance:

- Los ports no importan FastMCP.
- Los ports no importan librerias de vector DB.
- Los ports no importan `boto3`, OpenSearch, LanceDB ni Qdrant.
- La CLI puede aceptar paths locales, pero `application/` trabaja con `ContentObjectStore`.
- Los tests pueden crear fakes en memoria.

## 5. Roadmap por fases

## Fase 0: Investigacion y setup tecnico

Objetivo: reducir incertidumbre de APIs antes de escribir codigo dependiente de librerias.

Tareas:

- Verificar FastMCP y MCP:
  - `chub get fastmcp/package --lang py`
  - `chub get mcp/package --lang py`
- Verificar vector stores:
  - `chub search lancedb --json`
  - `chub get lancedb/package --lang py`
  - `chub search qdrant --json`
  - `chub get qdrant-client/package --lang py`
- Verificar embeddings y rerankers cuando se elijan proveedores concretos.
- Crear ADR corto si se cambia el default LanceDB/Qdrant.

Decisiones fijadas:

- Usar `fastmcp==3.1.0` como referencia documental si se elige el paquete FastMCP independiente.
- Usar `mcp==1.27.2` como referencia documental si se elige el SDK oficial.
- Para el primer roadmap de implementacion, preferir `fastmcp` como import principal si el proyecto adopta FastMCP independiente.
- Mantener snippets MCP compatibles con tools/resources/prompts y `stdio`.

Criterios de aceptacion:

- El implementador sabe que paquete MCP usar y por que.
- El implementador ha documentado cualquier divergencia de version.
- No hay snippets copiados de blogs antiguos con SSE como default.

## Fase 1: Contrato de contenido

Objetivo: definir la forma del conocimiento antes de indexarlo.

Tareas:

- Crear `content/` con subcarpetas canonicas.
- Crear ejemplos iniciales de Markdown:
  - un concepto;
  - un patron;
  - una plataforma;
  - un playbook.
- Definir schema frontmatter en `domain/metadata_schema.py`.
- Crear validador CLI `agentic-book validate-content`.
- Definir estados de contenido: `draft`, `reviewed`, `deprecated`.
- Definir regla de ids: `<type>.<slug>`, por ejemplo `concept.mcp`.
- Definir regla de links: `related` siempre usa ids canonicos, no paths.
- Definir metadata de frescura con adopcion gradual: obligatoria para documentos nuevos y migrada con defaults seguros para documentos existentes.
- Definir regla de reemplazo seguro: el path puede cambiar y el contenido puede reemplazarse, pero el `id` canonico debe mantenerse si representa el mismo concepto/documento.

Frontmatter minimo:

```yaml
---
id: "concept.mcp"
title: "Model Context Protocol"
type: "concept"
domain: ["agents", "mcp"]
audience: ["engineer", "architect", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
source_urls:
  - "https://modelcontextprotocol.io/docs"
source_type: "official"
upstream_version: "2026-06-18"
last_checked: "2026-06-30"
review_after: "2026-09-30"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["tools", "resources", "prompts", "stdio", "streamable-http"]
related:
  - "pattern.agentic-resource-discovery"
---
```

Tests:

- Valida frontmatter correcto.
- Rechaza id duplicado.
- Rechaza `related` inexistente en modo estricto.
- Rechaza fechas invalidas.
- Rechaza tipos fuera de taxonomia.
- Valida enums de frescura: `source_type` y `change_frequency`.
- En modo gradual, emite warning para documentos existentes sin metadata de frescura; en modo strict, falla.

Criterios de aceptacion:

- Un agente puede saber si un archivo es indexable sin ejecutar ingestion.
- El contrato diferencia contenido canonico de wiki.
- El contrato permite reemplazar o mover documentos manteniendo ids canonicos y relaciones estables.
- El contrato permite detectar documentos stale sin consultar el indice RAG.

## Fase 2: Dominio y casos de uso base

Objetivo: crear el nucleo estable del sistema.

Tareas:

- Crear modelos de dominio.
- Crear ports.
- Crear errores de dominio:
  - `InvalidMetadataError`
  - `DuplicateDocumentIdError`
  - `DocumentNotFoundError`
  - `IndexVersionMismatchError`
- Crear casos de uso:
  - `ValidateCorpus`
  - `IngestCorpus`
  - `SearchCorpus`
  - `FusionSearchCorpus`
  - `GetDocument`
  - `BuildCorpusManifest`

Signatures recomendadas:

```python
class ValidateCorpus:
    async def run(self, root: Path) -> "ValidationReport":
        ...

class IngestCorpus:
    async def run(self, root: Path, layer: str = "canonical") -> "IngestionReport":
        ...

class SearchCorpus:
    async def run(self, query: "RetrievalQuery") -> list["RetrievalResult"]:
        ...
```

Tests:

- Unit tests de modelos.
- Fakes de ports para casos de uso.
- Tests de errores esperados.

Criterios de aceptacion:

- Los casos de uso corren con fakes en memoria.
- No hay dependencia de FastMCP en `domain/` ni `application/`.

## Fase 3: Markdown parser e ingesta incremental

Objetivo: convertir Markdown canonico en documentos, secciones y chunks reproducibles.

Tareas:

- Implementar parser Markdown con frontmatter.
- Extraer headings `#`, `##`, `###`.
- Crear chunks:
  - documento completo;
  - secciones por heading;
  - prefijo contextual determinista desde metadata + heading path.
- Calcular:
  - `source_hash`;
  - `metadata_hash`;
  - `chunk_hash`;
  - `embedding_config_hash`.
- Crear `IngestionManifest` persistente en directorio de datos local, no en `content/`.
- Definir politica de reindex:
  - si cambia `source_hash`, regenerar chunks;
  - si cambia `metadata_hash`, actualizar filtros;
  - si cambia `embedding_config_hash`, recalcular embeddings;
  - si no cambia nada, saltar.

Ejemplo de prefijo contextual:

```text
[Book: Agentic Book | Layer: canonical | Type: concept | Title: Model Context Protocol | Heading: Transports]
```

Tests:

- Parser conserva frontmatter.
- Parser genera secciones estables.
- Hash no cambia si solo cambia whitespace irrelevante, si se normaliza.
- Hash cambia si cambia contenido semantico.
- Ingesta incremental salta documentos no modificados.

Criterios de aceptacion:

- Un cambio en un Markdown afecta solo a sus chunks.
- Los chunks tienen ids deterministas.

## Fase 4: Lexical retrieval baseline

Objetivo: tener busqueda util antes de embeddings.

Tareas:

- Implementar `LexicalIndex` local.
- Usar BM25 o algoritmo lexical simple inicialmente.
- Indexar texto enriquecido + metadata.
- Soportar filtros:
  - `type`
  - `domain`
  - `audience`
  - `maturity`
  - `status`
  - `tags`
  - `layer`
- Devolver resultados en el schema final.

Schema de respuesta:

```python
class RetrievalResult(BaseModel):
    result_id: str
    document_id: str
    chunk_id: str
    title: str
    score: float
    source_path: str
    section_heading: str | None = None
    text: str
    metadata: DocumentMetadata
    retrieval_mode: str
    why_retrieved: str | None = None
```

Tests:

- Encuentra siglas como MCP, A2A, RAG.
- Encuentra comandos o APIs exactas.
- Aplica filtros correctamente.
- Devuelve resultados ordenados por score.

Criterios de aceptacion:

- `SearchCorpus` funciona sin vector store.
- Las consultas exactas no dependen de embeddings.

## Fase 5: Vector retrieval

Objetivo: anadir busqueda semantica sin acoplar el core a un proveedor.

Tareas:

- Implementar `EmbeddingProvider`.
- Implementar primer `VectorStore`.
- Default recomendado: LanceDB local.
- Segundo adapter planificado: Qdrant local.
- Guardar metadata suficiente para reconstruir resultado sin leer todo el documento.
- Normalizar dimensiones y version de embedding en manifest.

Investigacion requerida:

- Antes de implementar LanceDB, ejecutar `chub get lancedb/package --lang py`.
- Antes de implementar Qdrant, ejecutar `chub get qdrant-client/package --lang py`.
- Antes de implementar embeddings concretos, verificar docs del proveedor con `chub`.

Tests:

- Upsert idempotente.
- Search devuelve chunks esperados con fake embeddings.
- Cambio de dimension falla con error claro.
- Vector store adapter pasa contract tests.

Criterios de aceptacion:

- El retrieval vectorial puede apagarse sin romper MCP.
- Cambiar LanceDB por Qdrant no cambia `application/`.

## Fase 6: Hybrid retrieval y Reciprocal Rank Fusion

Objetivo: combinar precision lexical con recall semantico.

Tareas:

- Implementar `retrieval_mode`:
  - `lexical`
  - `vector`
  - `hybrid`
- Implementar RRF para fusionar listas.
- Implementar `fusion_search` con subqueries provistas por el agente cliente.
- Colapsar duplicados por `chunk_id`.
- Registrar contribucion por subquery.

Formula RRF:

```python
def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return scores
```

Tests:

- RRF es determinista.
- Duplicados se fusionan.
- `hybrid` mejora o iguala lexical/vector en fixtures pequenas.
- `fusion_search` reporta que subqueries contribuyeron.

Criterios de aceptacion:

- Tools MCP pueden elegir `retrieval_mode`.
- `fusion_search` no requiere que el servidor genere subqueries.

## Fase 7: MCP server read-only

Objetivo: exponer el corpus a agentes por MCP.

Tareas:

- Crear `interfaces/mcp/server.py`.
- Crear factory que haga wiring de casos de uso.
- Exponer tools:
  - `search`
  - `fusion_search`
  - `get_document`
  - `get_related`
  - `answerability_check`
  - `corpus_manifest`
- Exponer resources:
  - `agentic-book://manifest`
  - `agentic-book://taxonomy`
  - `agentic-book://documents/{document_id}`
  - `agentic-book://wiki/index`
  - `agentic-book://schemas/frontmatter`
- Exponer prompts:
  - `compare_concepts`
  - `build_enterprise_playbook`
  - `audit_agentic_architecture`
  - `summarize_with_citations`
  - `generate_subqueries`

FastMCP snippet de referencia:

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="AgenticBook",
    instructions="Use this server to retrieve grounded context from Agentic Book.",
)

@mcp.tool
async def search(query: str, top_k: int = 8, retrieval_mode: str = "hybrid") -> dict:
    """Search the Agentic Book corpus."""
    result = await app.search.run_query(query=query, top_k=top_k, retrieval_mode=retrieval_mode)
    return result.model_dump()

@mcp.resource("agentic-book://manifest")
def manifest() -> dict:
    """Expose corpus capabilities and index metadata."""
    return app.manifest.current().model_dump()

@mcp.prompt
def compare_concepts(concept_a: str, concept_b: str, audience: str = "architect") -> str:
    return (
        f"Compare {concept_a} and {concept_b} for {audience}. "
        "Use search and get_document, cite document ids, and call out uncertainty."
    )
```

Transport rules:

- `mcp.run()` for stdio default.
- Streamable HTTP on `127.0.0.1:8000/mcp` for local endpoint.
- No auth required for stdio.
- Auth only belongs to HTTP deployment phase.

Tests:

- `fastmcp list` shows tools/resources/prompts.
- `fastmcp call` can run `corpus_manifest`.
- In-memory client smoke test can call `search`.
- HTTP path uses `/mcp`, not root.

Criterios de aceptacion:

- Un agente MCP puede discover -> search -> get_document.
- El servidor no modifica contenido ni indices.

## Fase 8: CLI de administracion

Objetivo: separar operaciones mutantes de ingestion/admin del MCP read-only.

Comandos:

```text
agentic-book validate-content
agentic-book ingest --layer canonical
agentic-book ingest --layer wiki
agentic-book build-index
agentic-book eval retrieval
agentic-book serve-mcp --transport stdio
agentic-book serve-mcp --transport http --host 127.0.0.1 --port 8000
```

Reglas:

- CLI puede escribir manifests e indices.
- MCP read-only no escribe.
- Comandos deben tener `--dry-run` donde aplique.

Tests:

- CLI valida corpus fixture.
- CLI dry-run no escribe.
- CLI ingest actualiza manifest temporal en tests.

Criterios de aceptacion:

- Un agente puede preparar el corpus por CLI y luego servirlo por MCP.

## Fase 9: Evaluation harness

Objetivo: evitar optimizar retrieval a ciegas.

Tareas:

- Crear dataset JSON de ground truth.
- Crear runner de evaluacion.
- Implementar metricas:
  - Recall@k;
  - MRR;
  - nDCG;
  - precision por filtro;
  - tasa de unanswerable correctamente detectado.
- Guardar reportes en `evals/reports/`.

Formato minimo:

```json
{
  "id": "mcp-transport-001",
  "query": "Que transporte MCP se recomienda para servidores remotos nuevos?",
  "expected_document_ids": ["concept.mcp"],
  "expected_keywords": ["Streamable HTTP", "stdio"],
  "forbidden_keywords": ["SSE como default"],
  "type": "direct"
}
```

Tests:

- Metricas calculan valores esperados sobre fixtures.
- Runner falla si el indice no existe.
- Reporte incluye config de retrieval.

Criterios de aceptacion:

- Antes de HyDE, GraphRAG o reranker, existe baseline medido.

## Fase 10: Freshness, reemplazo seguro y propuestas locales de actualizacion

Objetivo: hacer que el corpus pueda mantenerse al dia cuando protocolos, SDKs, estandares y practicas recomendadas cambian con frecuencia, sin convertir el MCP read-only en una superficie mutante.

Decisiones fijadas:

- El contenido sigue siendo Markdown curado y semanticamente separado.
- Reemplazar un documento debe ser barato si se conserva el `id` canonico.
- `related` y citas internas usan ids canonicos, no paths.
- El MCP principal sigue siendo read-only y no abre issues ni PRs.
- Las propuestas de actualizacion son artefactos locales versionables bajo `.proposals/`.
- GitHub issue/PR queda para un workflow admin posterior, siempre con aprobacion humana.

Metadata de frescura:

```yaml
source_urls:
  - "https://example.com/official-docs"
source_type: "official"
upstream_version: "2026-06-18"
last_checked: "2026-06-30"
review_after: "2026-09-30"
change_frequency: "high"
supersedes: []
superseded_by: null
```

Valores permitidos:

- `source_type`: `official`, `vendor`, `community`, `internal`, `derived`.
- `change_frequency`: `low`, `medium`, `high`, `volatile`.
- `supersedes`: lista de ids canonicos o versiones internas.
- `superseded_by`: id canonico, version futura o `null`.

Reglas:

- `last_reviewed` indica revision editorial.
- `last_checked` indica comprobacion contra fuente upstream.
- `review_after` alimenta stale detection.
- Si `change_frequency` es `high` o `volatile`, `review_after` no debe quedar indefinido.
- `source_urls` es obligatorio cuando `source_type` no es `internal`.
- Documentos nuevos deben incluir metadata de frescura.
- Documentos existentes se migran con defaults seguros y warnings hasta activar modo strict.

Comandos planificados:

```bash
agentic-book stale-report
agentic-book propose-doc-update concept.mcp --reason "MCP transport guidance may be outdated"
```

Artefactos locales:

```text
.proposals/
  documentation-updates/
    2026-06-30-concept.mcp.md
    2026-06-30-concept.mcp.json
```

Cada propuesta debe incluir:

- documento afectado;
- seccion o fragmento afectado, si se conoce;
- razon del cambio;
- fuente sugerida;
- urgencia;
- cambio propuesto en lenguaje natural;
- queries o retrieval results que llevaron a la sospecha;
- estado: `draft`, `needs-human-review`, `accepted`, `rejected`.

Tareas:

- Extender modelos y schema de metadata con campos de frescura.
- Implementar modo de validacion gradual y modo strict.
- Implementar reporte stale en Markdown y JSON.
- Implementar generacion de propuestas locales sin modificar `content/`.
- Excluir `.proposals/` de ingesta por defecto.
- Documentar que propuestas locales no equivalen a verdad canonica.
- Anadir skills operativas para evaluar frescura y redactar propuestas.

Tests:

- Acepta documentos nuevos con campos de frescura.
- Emite warning para documentos existentes sin frescura en modo gradual.
- Falla en modo strict si faltan `last_checked` o `review_after`.
- Marca stale cuando `review_after` es anterior a la fecha actual.
- Prioriza `high` y `volatile` en stale report.
- `propose-doc-update` crea artefacto local y no modifica `content/`.
- Rechaza document id inexistente.
- Reemplazar contenido manteniendo `id` regenera chunks sin romper `related`.
- MCP read-only no expone `stale-report`, `propose-doc-update`, GitHub issue ni PR.

Criterios de aceptacion:

- Un maintainer puede identificar documentos stale sin leer todo el corpus.
- Un agente puede proponer una actualizacion local estructurada durante una interaccion.
- Ninguna propuesta local modifica el contenido canonico sin revision humana.
- El futuro workflow GitHub puede construirse encima de propuestas locales sin cambiar MCP read-only.

## Fase 11: Wiki layer

Objetivo: anadir sintesis persistente sin romper trazabilidad canonica.

Tareas:

- Crear `wiki/index.md`.
- Crear `wiki/log.md`.
- Crear estructura de mapas, entidades y comparativas.
- Indexar wiki como `layer: wiki`.
- Modificar search para permitir `layers=["canonical"]` por defecto.
- Permitir `layers=["canonical", "wiki"]` para busquedas exploratorias.

Reglas:

- `content/` gana sobre `wiki/` en conflictos.
- Respuestas de alto riesgo deben citar `canonical`.
- Wiki puede resumir, comparar y senalar contradicciones, pero no ser unica evidencia.

Tests:

- Search default no devuelve wiki si no se pide.
- Search con layer wiki devuelve paginas sinteticas.
- Manifest reporta cantidad por layer.

Criterios de aceptacion:

- Un agente puede usar wiki para orientarse y content para evidenciar.

## Fase 12: Skills operativas

Objetivo: empaquetar procedimientos repetibles para agentes.

Skills iniciales:

- `ingest-book-source`
- `evaluate-document-freshness`
- `propose-documentation-update`
- `review-update-proposal`
- `maintain-agentic-wiki`
- `evaluate-rag-quality`
- `security-review-agentic-pattern`

Reglas:

- Cada skill tiene `SKILL.md`.
- Cada skill explica inputs, outputs, checks y comandos.
- Skills no contienen el libro.
- Skills pueden referenciar scripts o templates.

Ejemplo de estructura:

```text
skills/
  ingest-book-source/
    SKILL.md
    checklist.md
```

Criterios de aceptacion:

- Un agente puede seguir la skill de ingesta para anadir una pagina canonica.
- Un agente puede seguir la skill de frescura para detectar contenido stale.
- Un agente puede redactar una propuesta local sin modificar `content/`.
- Un agente puede seguir la skill de evaluacion para generar o actualizar ground truth.

## Fase 13: Answerability y corrective retrieval ligero

Objetivo: ayudar al agente cliente a no responder sin evidencia suficiente.

Tareas:

- Implementar `answerability_check`.
- Inputs:
  - query;
  - result ids;
  - strictness.
- Outputs:
  - `answerable`;
  - `confidence`;
  - `gaps`;
  - `suggested_queries`;
  - `warnings`.
- Mantenerlo como heuristica/evaluator, no como generador final.

Tests:

- Detecta lista vacia como no answerable.
- Detecta resultados sin keywords esperadas en fixtures.
- Sugiere query adicional cuando hay bajo recall.

Criterios de aceptacion:

- El MCP server ayuda a detectar evidencia insuficiente sin convertirse en chatbot.

## Fase 14: Observabilidad y seguridad

Objetivo: hacer el sistema depurable y seguro para entorno enterprise local.

Tareas:

- Logging estructurado JSON.
- Log por query:
  - query;
  - filters;
  - mode;
  - top_k;
  - result ids;
  - scores;
  - index version;
  - latency per stage.
- Sanitizar document ids y paths.
- Denegar path traversal.
- Separar config de secretos.
- Documentar que HTTP auth no aplica a stdio.

Tests:

- `../` en document id falla.
- Logs incluyen version de indice.
- MCP read-only no expone comandos de ingestion.

Criterios de aceptacion:

- Un fallo de retrieval se puede depurar con logs.
- El servidor read-only no modifica estado.

## Fase 15: Packaging y experiencia de agente

Objetivo: dejar el proyecto consumible.

Tareas:

- Crear README operativo.
- Crear `pyproject.toml`.
- Definir extras:
  - `mcp`;
  - `lancedb`;
  - `qdrant`;
  - `eval`;
  - `dev`.
- Documentar comandos:
  - instalar;
  - validar;
  - ingestar;
  - servir MCP;
  - correr tests;
  - correr evals.
- Crear ejemplo de configuracion para cliente MCP.

Ejemplo de config conceptual:

```json
{
  "mcpServers": {
    "agentic-book": {
      "command": "agentic-book",
      "args": ["serve-mcp", "--transport", "stdio"]
    }
  }
}
```

Tests:

- Instalacion editable funciona.
- Entry point CLI existe.
- MCP smoke test documentado funciona.

Criterios de aceptacion:

- Otro agente puede arrancar desde README y consumir el corpus.

## Fase 16: Imagen Docker y Docker Compose

Objetivo: disponer de un empaquetado reproducible que permita correr el MCP server localmente con Docker Compose y que sirva como base para ECR/Fargate en fases posteriores.

Tareas:

- Crear `Dockerfile` multi-stage o slim, sin credenciales embebidas.
- Crear `.dockerignore` para excluir `.git`, venvs, caches, indices locales pesados y documentos temporales no necesarios.
- Crear `docker-compose.yml` para desarrollo local.
- Exponer el MCP server por Streamable HTTP en `0.0.0.0:8000` dentro del contenedor y `/mcp` como path.
- Montar `content/`, `wiki/`, `evals/` y directorio de datos local como volumes en Compose.
- Mantener `stdio` como modo recomendado para integraciones locales de editor/desktop fuera de Docker.
- Permitir comandos CLI dentro de la imagen: validar, ingestar, evaluar y servir MCP.
- Documentar variables de entorno para backend local/cloud sin hardcodearlas.

Compose conceptual:

```yaml
services:
  agentic-book:
    build: .
    command: ["agentic-book", "serve-mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
    ports:
      - "8000:8000"
    volumes:
      - ./content:/app/content:ro
      - ./wiki:/app/wiki:ro
      - ./evals:/app/evals
      - ./.agentic-book-data:/app/.agentic-book-data
    environment:
      AGENTIC_BOOK_PROFILE: local
```

Tests:

- `docker build .` funciona sin secretos.
- `docker compose up` levanta HTTP MCP en `/mcp`.
- La imagen puede ejecutar `agentic-book validate-content`.
- El contenedor no necesita escribir en `content/` ni `wiki/` para servir MCP.

Criterios de aceptacion:

- Un usuario puede probar el servidor con Docker Compose sin instalar Python localmente.
- La misma imagen puede ser candidata a publicacion posterior en ECR.
- El modo contenedor no introduce dependencias en `domain/` ni `application/`.

## Fase 17: CI con GitHub Actions

Objetivo: asegurar que cada cambio mantiene calidad minima antes de avanzar a integraciones mas costosas.

Tareas:

- Crear `.github/workflows/ci.yml`.
- Ejecutar CI en `pull_request` y `push` a la rama principal.
- Construir la imagen Docker en CI sin publicarla por defecto.
- Usar una matriz pequena de Python, inicialmente la version minima soportada y la version estable usada por el proyecto.
- Instalar dependencias con extras de desarrollo.
- Ejecutar checks en orden:
  - formato en modo check;
  - lint;
  - type checking;
  - unit tests;
  - integration tests sin servicios externos;
  - validacion de contenido fixture;
  - MCP smoke test sin red cuando exista server;
  - `docker build .` sin push.
- Mantener tests que requieran cloud, OpenSearch, S3, ECR, Fargate o credenciales como jobs separados y manuales (`workflow_dispatch`) hasta tener infraestructura real.

Workflow minimo esperado:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: python -m pip install -e ".[dev,mcp,eval]"
      - name: Lint
        run: ruff check .
      - name: Format check
        run: ruff format --check .
      - name: Type check
        run: mypy src
      - name: Tests
        run: pytest
      - name: Docker build
        run: docker build .
```

Tests:

- El workflow no requiere secretos.
- El workflow no arranca servicios cloud.
- El workflow construye la imagen pero no publica en registry.
- Los tests de adapters cloud se marcan y quedan fuera del job default.

Criterios de aceptacion:

- Cualquier PR valida estilo, tipos, tests y contenido basico.
- CI detecta roturas del contrato de dominio antes de llegar a MCP o vector stores reales.
- Los jobs de cloud pueden anadirse sin mezclar credenciales con CI basico.

## Fase 18: Portabilidad cloud y despliegue AWS-ready

Objetivo: garantizar que pasar de local-first a AWS sea un cambio de adaptadores y configuracion, no una reescritura.

Diagnostico del roadmap original:

- La idea de ports para `VectorStore`, `EmbeddingProvider` y `DocumentRepository` facilitaba cambiar la BBDD vectorial.
- La firma original orientada a `Path` hacia mas dificil sustituir carpetas locales por S3.
- La mejora obligatoria es tratar el contenido como objetos (`ContentObjectStore`) y no como paths en `application/`.

Adapters cloud planificados:

- `S3ContentObjectStore`: lee Markdown canonico y wiki desde S3.
- `S3ManifestStore`: persiste manifests de ingesta y versiones de indice en S3 o DynamoDB, segun necesidades de concurrencia.
- `OpenSearchVectorStore`: implementa `VectorStore` con OpenSearch vector search.
- `OpenSearchLexicalIndex`: implementa `LexicalIndex` con BM25/OpenSearch.
- `BedrockEmbeddingProvider` u otro provider cloud: implementa `EmbeddingProvider`.
- `CloudWatchQueryLogger`: implementa logging estructurado para despliegues AWS.
- `EcrImagePublisher` no es un port de dominio; pertenece a CI/CD, no al runtime.

Reglas de diseno:

- `content/` local y S3 comparten el mismo modelo `ContentObject`.
- Los ids canonicos no deben depender de bucket, path absoluto ni URL.
- Los manifests deben incluir `storage_backend`, `index_backend`, region, version de schema y version de embedding.
- `application/` no debe importar `boto3`, `opensearch-py`, credenciales ni variables AWS.
- La seleccion local/cloud se hace por config y wiring en `interfaces/cli/` o composition root.
- El MCP server sigue siendo read-only tanto local como cloud.
- La imagen Docker debe poder ejecutarse localmente con filesystem/LanceDB y en AWS con S3/OpenSearch mediante variables de entorno y wiring distinto.

Investigacion requerida antes de implementar AWS:

- Verificar SDKs actuales de AWS/OpenSearch con fuentes oficiales o `chub` si estan disponibles.
- Confirmar API actual de OpenSearch vector search y filtros metadata.
- Confirmar autenticacion para OpenSearch Serverless o dominio gestionado.
- Confirmar estrategia de credenciales local: AWS profile, env vars o role.
- Confirmar si manifests requieren consistencia fuerte; si si, evaluar DynamoDB para locks/versiones.
- Confirmar estrategia ECR/Fargate: publicacion de imagen solo en tags/releases, task definition con secrets fuera de la imagen, healthcheck HTTP y logs a CloudWatch.

Tests:

- Contract tests comunes para `ContentObjectStore`, ejecutados contra fake local y fixture filesystem.
- Contract tests comunes para `VectorStore`, ejecutados contra fake y adapter local.
- Tests cloud marcados como `@pytest.mark.cloud` y excluidos por defecto.
- Test de configuracion que demuestra cambiar `local` a `aws` sin modificar casos de uso.

Criterios de aceptacion:

- Un mismo `IngestCorpus` funciona con filesystem local o S3 mediante wiring distinto.
- Un mismo `SearchCorpus` funciona con LanceDB/Qdrant local u OpenSearch mediante wiring distinto.
- El MCP server no cambia cuando cambia el backend.
- El README documenta un perfil local, un perfil Docker Compose y un perfil AWS-ready.
- La publicacion a ECR/Fargate esta definida como workflow separado o job manual, no como efecto automatico de cualquier PR.


## 6. Advanced retrieval backlog

No implementar hasta tener baseline.

### Reranking

- Adapter `Reranker`.
- Opciones:
  - local;
  - provider API;
  - none.
- Evaluar mejora contra baseline.

### HyDE

- Tool o caso de uso separado para generar query hipotetica.
- Requiere provider LLM.
- Solo activar por configuracion.

### GraphRAG

- Indice secundario.
- Extraer entidades, relaciones y claims.
- Mantener refresh incremental.
- Usar para multi-hop y mapas conceptuales, no para reemplazar RAG base.

### Late chunking/contextual retrieval con LLM

- Primero usar prefijos deterministas.
- LLM-generated contextual headers solo si eval demuestra necesidad.

## 7. Contratos MCP finales

## 7.1 Limite read-only del MCP

El MCP final de consumo no debe exponer comandos mutantes. En particular, no debe exponer:

- `stale-report`;
- `propose-doc-update`;
- creacion de GitHub issues;
- apertura de ramas o PRs;
- escritura en `content/`, `wiki/` o `.proposals/`.

Estas operaciones pertenecen a CLI/admin workflows y skills con aprobacion humana.


### `search`

Parametros:

```yaml
query: string
top_k: integer = 8
retrieval_mode: "hybrid" | "vector" | "lexical" = "hybrid"
reranker: "none" | "local" | "provider" = "none"
filters:
  type: list[string]
  domain: list[string]
  audience: list[string]
  maturity: list[string]
  status: list[string]
  tags: list[string]
  layer: list["canonical" | "wiki"]
return_mode: "snippets" | "sections" | "documents" = "sections"
include_metadata: boolean = true
```

### `fusion_search`

Parametros:

```yaml
queries: list[string]
top_k_per_query: integer = 8
final_top_k: integer = 10
retrieval_mode: "hybrid" | "vector" | "lexical" = "hybrid"
rrf_k: integer = 60
reranker: "none" | "local" | "provider" = "none"
filters: object
```

### `get_document`

Parametros:

```yaml
document_id: string
include_frontmatter: boolean = true
include_neighbors: boolean = true
```

### `corpus_manifest`

Parametros:

```yaml
include_taxonomy: boolean = true
include_index_stats: boolean = true
include_tool_guidance: boolean = true
```

## 8. Criterios globales de aceptacion

El proyecto esta listo para una primera version cuando:

- `agentic-book validate-content` valida fixtures canonicos.
- `agentic-book ingest` genera indices reproducibles.
- `agentic-book eval retrieval` produce reporte baseline.
- `agentic-book stale-report` identifica documentos vencidos o pendientes de revision.
- `agentic-book propose-doc-update` crea propuestas locales sin modificar `content/`.
- `agentic-book serve-mcp --transport stdio` arranca.
- `agentic-book serve-mcp --transport http` expone `/mcp`.
- `docker compose up` levanta el MCP server HTTP localmente.
- GitHub Actions ejecuta lint, format check, type check, tests y build Docker sin secretos.
- El wiring permite cambiar filesystem local por S3 y vector store local por OpenSearch sin tocar `application/`.
- MCP lista tools, resources y prompts.
- MCP read-only no expone comandos mutantes de actualizacion, issues ni PRs.
- `search`, `fusion_search`, `get_document` y `corpus_manifest` funcionan.
- El core puede testearse sin levantar MCP.
- El retrieval funciona con lexical-only aunque no haya vector store configurado.
- El README explica como un agente debe consumir el server.

## 9. Riesgos y mitigaciones

- Riesgo: sobreingenieria temprana.
  - Mitigacion: ports pequenos, un solo adapter inicial, tests con fakes.
- Riesgo: chunking demasiado simple.
  - Mitigacion: document + section chunks desde v1 y eval antes de optimizar.
- Riesgo: dependencia excesiva de un proveedor.
  - Mitigacion: adapters para embeddings, vector store y reranker.
- Riesgo: MCP server con demasiada logica.
  - Mitigacion: MCP solo llama casos de uso.
- Riesgo: wiki usada como fuente canonica.
  - Mitigacion: `layer` explicito y canonical default.
- Riesgo: herramientas mutantes expuestas a agentes.
  - Mitigacion: MCP read-only y CLI admin separado.
- Riesgo: documentacion stale en protocolos y SDKs cambiantes.
  - Mitigacion: metadata de frescura, stale reports y propuestas locales versionables.
- Riesgo: propuestas de actualizacion tratadas como fuente canonica.
  - Mitigacion: `.proposals/` queda fuera de ingesta y requiere revision humana antes de modificar `content/`.
- Riesgo: no saber si retrieval mejora.
  - Mitigacion: eval harness antes de advanced retrieval.
- Riesgo: CI demasiado tarde y deuda de calidad acumulada.
  - Mitigacion: GitHub Actions desde fases tempranas con checks baratos y sin secretos.
- Riesgo: imagen Docker acoplada a rutas locales o secretos.
  - Mitigacion: volumes/config externa, usuario no root y secrets solo por entorno/runtime.
- Riesgo: portabilidad cloud aparente pero acoplada a paths locales.
  - Mitigacion: `ContentObjectStore` como port obligatorio y `Path` solo en CLI/adapters.

## 10. Orden recomendado de ejecucion por agente

1. Leer `docs/architecture-recommendations.md`.
2. Leer este roadmap completo.
3. Ejecutar investigaciones de Fase 0 con `chub`.
4. Crear estructura minima de proyecto y packaging.
5. Implementar dominio y ports.
6. Implementar contrato de contenido y validacion.
7. Implementar parser e ingesta incremental.
8. Implementar lexical retrieval.
9. Implementar vector retrieval.
10. Implementar hybrid y RRF.
11. Implementar MCP read-only.
12. Implementar CLI admin.
13. Implementar eval harness.
14. Implementar frescura, stale report y propuestas locales.
15. Anadir wiki layer.
16. Anadir skills operativas.
17. Anadir observabilidad y seguridad.
18. Anadir imagen Docker y Docker Compose.
19. Anadir GitHub Actions CI con build Docker sin push.
20. Validar portabilidad AWS-ready con adapters contractuales.
21. Documentar consumo por agentes.

## 11. Fuentes de referencia usadas para este roadmap

- `docs/architecture-recommendations.md`
- FastMCP docs via `chub`: `fastmcp/package`, Python, version 3.1.0, updated 2026-03-12.
- MCP Python SDK docs via `chub`: `mcp/package`, Python, version 1.27.2, updated 2026-05-29.
- `chub search qdrant --json`, que muestra `qdrant-client/package` version 1.17.0 y `qdrant/vector-search` version 1.15.1.
- `chub search lancedb --json`, que muestra `lancedb/package` version 0.29.2.
