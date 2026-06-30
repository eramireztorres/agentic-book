---
title: "Recomendaciones de arquitectura para Agentic Book"
status: "draft"
created: "2026-06-29"
audience:
  - "maintainers"
  - "LLM agents"
  - "enterprise AI architects"
scope:
  - "RAG"
  - "MCP"
  - "LLM wiki"
  - "skills"
  - "agentic knowledge delivery"
---

# Recomendaciones de arquitectura para Agentic Book

## Resumen ejecutivo

El approach propuesto es correcto como base, pero conviene ampliarlo en tres puntos:

1. No hacer que "un archivo Markdown = un chunk" sea una regla tecnica absoluta. Debe ser una regla editorial fuerte, pero el sistema deberia distinguir entre `source document`, `retrieval unit` y `delivery unit`.
2. No limitar el MCP server a tools de busqueda. MCP tambien tiene `resources` y `prompts`; para un libro agent-friendly son tan importantes como las tools.
3. Complementar RAG con una capa tipo LLM Wiki y con skills, pero no sustituirlo. Cada mecanismo resuelve un problema distinto:
   - RAG: recuperacion fiel desde fuentes atomicas.
   - LLM Wiki: sintesis persistente, interlinks, contradicciones, paginas de concepto.
   - Skills: procedimientos ejecutables que ensenan a un agente como hacer una tarea recurrente.

La arquitectura recomendada es:

```text
raw sources / book markdown
        |
        v
validation + metadata normalization
        |
        v
canonical content store  --------------------------+
        |                                          |
        v                                          v
retrieval index: vector + lexical + metadata     generated wiki
        |                                          |
        +------------------+-----------------------+
                           v
                  MCP server facade
      tools + resources + prompts + manifest/capabilities
```

## Evaluacion de la idea inicial

### 1. Markdown semantico como unidad editorial

La idea de subir el libro en Markdown con frontmatter bien configurado es excelente. Es la decision que mas reducira complejidad downstream. Para este dominio, la calidad de recuperacion dependera mas de una buena autoria de contenido y metadata que de un chunker sofisticado.

La matizacion importante: cada archivo Markdown deberia ser una unidad semantica autocontenida, pero no necesariamente el unico chunk indexado.

Ejemplo:

- Un archivo `mcp/transports-streamable-http.md` puede ser una unidad autoral.
- Dentro puede haber secciones `Overview`, `When to use`, `Security considerations`, `Implementation notes`.
- El indice puede guardar:
  - el documento completo como unidad de entrega;
  - secciones como unidades de recuperacion fina;
  - metadata y enlaces como filtros;
  - opcionalmente summaries o contextual headers como campos adicionales.

Esto evita dos fallos:

- Archivos demasiado largos que recuperan mucho ruido.
- Archivos demasiado cortos que pierden contexto de libro, capitulo, version, proveedor o audiencia.

### 2. Ingesta incremental

La ingesta incremental por cambios de Markdown es la direccion correcta. Debe estar disenada desde el inicio como pipeline reproducible, no como script ad hoc.

Recomendacion:

- Calcular `content_hash` por archivo normalizado.
- Guardar un `document_id` estable que no dependa del path si el archivo se mueve.
- Separar `source_hash`, `metadata_hash` y `embedding_hash`.
- Reindexar solo cuando cambie contenido, metadata relevante, modelo de embedding o estrategia de parsing.
- Mantener un manifest de ingestion con version de schema, version del embedding model y fecha.

### 3. Vector DB para RAG

El vector DB es necesario, pero no deberia ser la unica superficie de recuperacion.

Para este proyecto, el retrieval minimo viable deberia ser hibrido:

- Dense vector search para similitud semantica.
- BM25 o busqueda lexical para nombres exactos, APIs, siglas, versiones, errores, vendors, standards y comandos.
- Metadata filtering para dominio, madurez, stack, riesgo, fecha, fuente, audiencia y tipo de artefacto.
- Reranking opcional sobre los candidatos.

Para un scaffold local y portable, las mejores opciones iniciales son:

- `Qdrant`: buena opcion local/production, filtros fuertes, despliegue claro.
- `LanceDB`: muy buena opcion embebida/local si quieres simplicidad y portabilidad.
- `Chroma`: util para prototipo, pero probablemente lo cambiaria antes de convertirlo en arquitectura base.
- `Weaviate`: fuerte si quieres hybrid search nativo y despliegue mas enterprise.

Mi recomendacion inicial: disenar una interfaz `RetrieverStore` y empezar con Qdrant o LanceDB. Evitaria Pinecone al inicio porque el valor principal de este repo parece ser un scaffold reproducible y local-first.

### 4. MCP server con FastMCP

FastMCP encaja bien. La recomendacion es exponer tres tipos de capacidades:

- `tools`: operaciones parametrizables.
- `resources`: documentos, manifests, paginas o indices leibles por URI.
- `prompts`: plantillas para tareas recurrentes de lectura, comparacion, auditoria y sintesis.

No conviene convertir todo en tools. Si un agente solo necesita leer un manifiesto, una pagina canonica o un documento recuperado, `resource` es una abstraccion mas natural.

### 5. Endpoint local y otras opciones

Debes soportar dos transports desde el principio:

- `stdio`: default para integraciones locales con clientes MCP, IDEs y agentes que lanzan el server como subprocess.
- `Streamable HTTP`: para endpoint local persistente, despliegue remoto, containers, gateway, autenticacion y observabilidad.

SSE solo lo consideraria por compatibilidad con clientes antiguos. Para trabajo nuevo, Streamable HTTP es la opcion de red.

## Arquitectura recomendada

## Capas de contenido

### 1. `content/`: fuente canonica del libro

Directorio de Markdown escrito o curado por humanos.

Ejemplo:

```text
content/
  concepts/
    mcp.md
    agentic-rag.md
    skills.md
  platforms/
    openai-agents-sdk.md
    google-adk.md
    langgraph.md
  patterns/
    rag-hybrid-search.md
    corrective-rag.md
    graphrag.md
  enterprise/
    governance.md
    observability.md
    security.md
```

Cada archivo deberia tener frontmatter obligatorio.

```yaml
---
id: "concept.mcp"
title: "Model Context Protocol"
type: "concept"
domain: ["agents", "mcp"]
audience: ["engineer", "architect"]
maturity: "production"
last_reviewed: "2026-06-29"
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
canonical: true
tags: ["tools", "resources", "prompts", "stdio", "streamable-http"]
related:
  - "pattern.agentic-resource-discovery"
  - "platform.fastmcp"
---
```

Campos recomendados:

- `id`: estable y unico.
- `title`: titulo humano.
- `type`: `concept`, `pattern`, `platform`, `playbook`, `case-study`, `checklist`, `risk`, `tool`, `standard`, `glossary`.
- `domain`: taxonomia de alto nivel.
- `audience`: `developer`, `architect`, `security`, `platform`, `executive`, `agent`.
- `maturity`: `experimental`, `emerging`, `production`, `legacy`.
- `last_reviewed`: fecha concreta de revision editorial.
- `source_quality`: `primary`, `curated`, `community`, `vendor`, `internal`.
- `source_urls`: fuentes upstream usadas para verificar o actualizar el documento.
- `source_type`: `official`, `vendor`, `community`, `internal`, `derived`.
- `upstream_version`: version, fecha o revision upstream cuando exista.
- `last_checked`: ultima comprobacion contra fuentes upstream.
- `review_after`: fecha a partir de la cual el documento debe considerarse candidato a revision.
- `change_frequency`: `low`, `medium`, `high`, `volatile`.
- `supersedes` / `superseded_by`: trazabilidad de reemplazo sin romper ids canonicos.
- `related`: ids canonicos.
- `claims`: opcional, para afirmaciones importantes que requieran evidencia.

### 2. `wiki/`: sintesis mantenida por agentes

Esta es la capa tipo LLM Wiki. No sustituye a `content/`; se genera o mantiene a partir de ella.

Ejemplo:

```text
wiki/
  index.md
  log.md
  maps/
    agent-platforms.md
    rag-techniques.md
  entities/
    fastmcp.md
    google-adk.md
    langgraph.md
  comparisons/
    mcp-vs-a2a.md
    langgraph-vs-google-adk-vs-openai-agents-sdk.md
  contradictions/
    retrieval-pattern-tradeoffs.md
```

Uso recomendado:

- Paginas de sintesis transversal.
- Comparativas entre vendors/patrones.
- Contradicciones o tensiones entre fuentes.
- Mapas conceptuales.
- Preguntas frecuentes que agregan multiples fuentes.
- Respuestas valiosas generadas durante consultas y luego archivadas.

Regla clave: `content/` es fuente canonica; `wiki/` es artefacto compilado. Si hay conflicto, gana `content/` o la fuente primaria referenciada.

### 3. `skills/`: procedimientos para agentes

Las skills no deben ser el repositorio principal de conocimiento. Deben empaquetar procedimientos reutilizables.

Ejemplos utiles para este repo:

```text
skills/
  ingest-book-source/
    SKILL.md
    checklist.md
  evaluate-rag-quality/
    SKILL.md
    eval-template.json
  maintain-agentic-wiki/
    SKILL.md
  create-enterprise-playbook/
    SKILL.md
    templates/
      playbook.md
```

Skills candidatas:

- `ingest-book-source`: validar frontmatter, resumir documento, detectar links, proponer ids relacionados.
- `maintain-agentic-wiki`: actualizar `wiki/index.md`, paginas de entidades, comparativas y `wiki/log.md`.
- `evaluate-rag-quality`: generar y correr evaluaciones de retrieval.
- `write-agent-facing-page`: convertir una explicacion humana en una pagina optimizada para agentes.
- `security-review-agentic-pattern`: revisar riesgos de MCP/tools/RAG/agents.

Las skills son especialmente valiosas si quieres que otros agentes o contribuidores mantengan el repo con disciplina. No son una alternativa a MCP; son instrucciones portables para operar el repo.

## Estrategia de chunking

La mejor estrategia inicial no es un chunker complejo, sino un contrato editorial estricto mas parsing estructural.

Recomendacion por fases:

### Fase 1: document-as-unit + section-aware

Indexar:

- Archivo completo como `document`.
- Secciones Markdown por headings como `section`.

Entregar al LLM:

- Secciones si la consulta es precisa.
- Documento completo si varias secciones del mismo archivo aparecen en el top-k.

Esto implementa una forma simple de hierarchical retrieval / auto-merge.

### Fase 2: contextual retrieval

Para cada section chunk, enriquecer el texto indexado con un prefijo generado o derivado:

```text
[Book: Agentic Book | Chapter: MCP | Topic: Transports | Audience: platform engineer | Version context: 2026]
```

Primero intentaria prefijos deterministas desde metadata y headings. Solo usaria LLM-generated contextual headers cuando el corpus crezca y los errores de recuperacion lo justifiquen.

### Fase 3: advanced retrieval opcional

Anadir solo con evaluacion:

- Multi-query fusion con Reciprocal Rank Fusion.
- HyDE para preguntas vagas o mal formuladas.
- Corrective RAG para validar si el contexto recuperado es suficiente.
- GraphRAG para relaciones entre vendors, protocolos, riesgos, patrones y casos de uso.

No empezaria con GraphRAG como dependencia central. Lo prepararia como indice secundario cuando exista suficiente contenido relacionado.

## Tools MCP recomendadas

### Tool 1: `search`

Retrieval convencional.

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
  tags: list[string]
return_mode: "snippets" | "sections" | "documents" = "sections"
include_metadata: boolean = true
```

Debe devolver:

- `result_id`
- `document_id`
- `title`
- `score`
- `source_path`
- `section_heading`
- `text`
- `metadata`
- `why_retrieved` cuando sea posible

### Tool 2: `fusion_search`

Multi-query retrieval con Reciprocal Rank Fusion.

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

Debe devolver:

- resultados fusionados;
- contribucion por subquery;
- ranking antes/despues de fusion;
- duplicados colapsados.

### Tool 3: `get_document`

Recuperar una unidad canonica completa por id o path.

Parametros:

```yaml
document_id: string
include_frontmatter: boolean = true
include_neighbors: boolean = true
```

Esto evita que el agente dependa de snippets cuando necesita contexto completo.

### Tool 4: `get_related`

Explorar relaciones semanticas y editoriales.

Parametros:

```yaml
document_id: string
relation_types: list[string] = ["frontmatter", "semantic", "wiki_links"]
depth: integer = 1
top_k: integer = 10
```

Util para agentes que investigan un tema y necesitan seguir conexiones.

### Tool 5: `answerability_check`

Validador ligero antes de responder.

Parametros:

```yaml
query: string
result_ids: list[string]
strictness: "low" | "medium" | "high" = "medium"
```

Devuelve:

- si el contexto parece suficiente;
- gaps;
- queries adicionales sugeridas;
- advertencias de contradiccion o baja evidencia.

Esto implementa una version practica de Corrective RAG sin convertir el MCP server en un agente completo.

### Tool 6: `corpus_manifest`

Devuelve capacidades, taxonomia, versiones de indices y estadisticas.

Parametros:

```yaml
include_taxonomy: boolean = true
include_index_stats: boolean = true
include_tool_guidance: boolean = true
```

Esto es importante para agentic resource discovery: un agente debe poder descubrir que hay, como buscarlo y que filtros son validos.

## Resources MCP recomendados

Exponer como `resources`:

```text
agentic-book://manifest
agentic-book://taxonomy
agentic-book://documents/{document_id}
agentic-book://wiki/index
agentic-book://wiki/{page_id}
agentic-book://schemas/frontmatter
agentic-book://evals/retrieval-report/latest
```

Esto da a los agentes rutas estables y legibles sin invocar tools para contenido estatico.

## Prompts MCP recomendados

Prompts utiles:

- `compare_concepts(concept_a, concept_b, audience)`
- `build_enterprise_playbook(topic, constraints)`
- `audit_agentic_architecture(description)`
- `summarize_with_citations(document_ids)`
- `generate_subqueries(query, intent)`
- `maintain_wiki_after_ingest(document_id)`

Los prompts deben ser plantillas estrechas, no ensayos largos. Su valor esta en estandarizar outputs y reducir ambiguedad.

## LLM Wiki: sustituir o complementar

Recomendacion: complementar.

LLM Wiki resuelve un problema que RAG no resuelve bien: la acumulacion de sintesis. En RAG puro, cada pregunta reconstruye conexiones desde fragmentos. En una wiki mantenida por LLM, las conexiones, contradicciones y comparativas se conservan como artefactos.

Donde LLM Wiki gana:

- Synthesis pages.
- Comparativas entre plataformas.
- Mapas de conceptos.
- Contradicciones entre fuentes.
- Evolucion de tesis del libro.
- Onboarding humano.
- Navegacion tipo Obsidian.

Donde RAG gana:

- Citas fieles a fuente.
- Respuestas sobre detalles concretos.
- Actualizacion incremental objetiva.
- Recuperacion parametrizable por agente.
- Filtrado por metadata.
- Evaluacion automatica.

Decision recomendada:

- Mantener `content/` como canon.
- Generar/mantener `wiki/` como knowledge layer compilada.
- Indexar ambos, pero distinguirlos con `layer: canonical | wiki`.
- Por defecto, retrieval sobre `canonical`.
- Para preguntas exploratorias o comparativas, incluir `wiki`.
- En respuestas con riesgo alto, exigir evidencia desde `canonical`, no solo desde `wiki`.

## Frescura y actualizaciones frecuentes

Recomendacion: tratar la frescura como parte del contrato documental, no como una tarea manual externa.

Para protocolos, SDKs y practicas cambiantes, cada documento canonico debe poder responder:

- de donde salio la informacion;
- cuando se comprobo por ultima vez;
- cuando debe revisarse otra vez;
- si reemplaza o fue reemplazado por otra version;
- que tan probable es que cambie pronto.

El flujo recomendado es:

1. `stale-report` detecta documentos vencidos o de alta volatilidad.
2. Un agente redacta una propuesta local estructurada en `.proposals/`.
3. Un maintainer revisa la propuesta.
4. Solo tras aprobacion se modifica `content/`.
5. Ingesta y evaluaciones verifican que el reemplazo no rompio retrieval ni relaciones.

El MCP de lectura no debe abrir PRs, issues ni modificar archivos. Si se anade integracion GitHub, debe vivir en un workflow admin separado, con aprobacion humana y permisos acotados.

## Anthropic/Claude skills: sustituir o complementar

Recomendacion: complementar, no sustituir.

Las skills son mejores para procedimientos que para conocimiento amplio. Una skill debe responder a "como debe actuar el agente en esta tarea", no a "que sabe el libro sobre todo el dominio".

Buenos usos:

- Ingestar una nueva fuente.
- Mantener la wiki.
- Crear una pagina de playbook con formato consistente.
- Evaluar retrieval.
- Revisar seguridad/gobernanza.
- Generar ground truth para RAG.
- Ejecutar una checklist de calidad editorial.

Malos usos:

- Meter todo el libro dentro de skills.
- Crear cientos de skills de conceptos.
- Usar skills como sustituto de busqueda.
- Depender de skills especificas de un proveedor para servir conocimiento a cualquier agente.

Si quieres que el proyecto sea vendor-neutral, define skills en un formato simple y portable (`SKILL.md` + assets), pero no hagas que el runtime dependa de Claude. El MCP server debe seguir siendo la interfaz comun para agentes.

## Evaluacion y calidad

No deberias avanzar a retrieval avanzado sin eval harness.

Crear:

```text
evals/
  retrieval/
    ground_truth.json
    queries.basic.json
    queries.multi_hop.json
    queries.unanswerable.json
  reports/
```

Metricas:

- Recall@k por documento esperado.
- MRR / nDCG.
- Precision de metadata filters.
- Tasa de respuestas "unanswerable" correctamente detectadas.
- Faithfulness si se anade generacion.
- Latencia p50/p95.
- Coste por ingesta y por consulta.

Tipos de queries necesarios:

- Directas: "Que es MCP?"
- Exact match: "Que transporte recomienda MCP para HTTP nuevo?"
- Multi-hop: "Compara MCP resources con Agentic Resource Discovery."
- Comparativas: "LangGraph vs Google ADK para enterprise workflows."
- Playbook: "Como gobernar tools MCP en una empresa?"
- Unanswerable: preguntas que el corpus aun no cubre.
- Fecha/version: preguntas donde `last_reviewed` y fecha de fuente importan.

## Gobernabilidad, seguridad y observabilidad

Para el tema del libro, el scaffold debe demostrar buenas practicas enterprise desde el inicio.

### Seguridad

- No exponer tools que ejecuten acciones externas desde el MCP de lectura.
- Separar `read-only MCP server` de cualquier `admin/ingest MCP server`.
- Sanitizar paths e ids.
- No devolver secretos ni variables de entorno.
- Registrar origen de cada respuesta.
- Soportar auth solo en HTTP; `stdio` debe asumirse local.
- Permitir allowlist de capas: `canonical`, `wiki`, `draft`.

### Gobernabilidad

- Frontmatter obligatorio y validado.
- Estados de contenido: `draft`, `reviewed`, `deprecated`.
- `last_reviewed` y `review_owner`.
- Registro de fuentes primarias vs secundarias.
- Politica de stale content basada en `last_checked`, `review_after` y `change_frequency`.
- Flujo de propuestas locales en `.proposals/` para cambios sugeridos por agentes, fuera de la ingesta canonica.
- PRs o issues automatizados solo como workflow admin posterior y con aprobacion humana; nunca desde el MCP read-only.
- ADRs para decisiones de arquitectura.

### Observabilidad

Registrar por query:

- query original;
- subqueries;
- filtros;
- retrieval mode;
- top-k bruto;
- top-k reranked;
- documentos usados;
- latencia por etapa;
- version de indice;
- modelo de embedding;
- errores y fallbacks.

Esto permite depurar por que un agente recibio cierto contexto.

## Roadmap recomendado

### Milestone 1: contrato de contenido

- Crear `content/`.
- Definir schema de frontmatter.
- Crear validador.
- Crear ejemplos canonicos de paginas.
- Crear `wiki/index.md` y `wiki/log.md`.

### Milestone 2: ingestion local

- Parser Markdown con frontmatter.
- Extraccion de headings.
- Content hashing.
- Manifest de ingestion.
- Store local inicial.

### Milestone 3: retrieval hibrido

- Vector search.
- Lexical search.
- Fusion simple.
- Metadata filters.
- Result schema estable.

### Milestone 4: MCP read-only

- FastMCP server.
- `stdio` como default.
- Streamable HTTP para endpoint local.
- Tools: `search`, `fusion_search`, `get_document`, `corpus_manifest`.
- Resources: manifest, taxonomy, documents, wiki index.

### Milestone 5: eval harness

- Ground truth.
- Metricas de retrieval.
- Regression tests para cambios de chunking, embedding y reranker.

### Milestone 6: wiki + skills

- Skill/procedimiento de ingesta.
- Skill/procedimiento de mantenimiento de wiki.
- Indexar `wiki/` como capa separada.
- Prompts MCP para comparativas y playbooks.

### Milestone 7: advanced retrieval

- Reranker.
- Corrective RAG.
- HyDE opcional.
- GraphRAG opcional para relaciones maduras.

## Decisiones iniciales recomendadas

1. Usar Markdown + YAML frontmatter como contrato principal.
2. Mantener `content/` canonico y `wiki/` generado.
3. Indexar por documento y por seccion desde el inicio.
4. Implementar retrieval hibrido antes que GraphRAG.
5. Implementar MCP con `tools`, `resources` y `prompts`, no solo tools.
6. Soportar `stdio` y Streamable HTTP.
7. Separar read-only server de ingestion/admin server.
8. Evaluar retrieval con ground truth antes de optimizar chunking.
9. Usar skills para workflows, no para almacenar el libro.
10. Disenar toda respuesta del MCP con ids, metadata, version de indice y trazabilidad.

## Preguntas abiertas

- Quieres que el scaffold sea 100% local-first o aceptara proveedores externos para embeddings/reranking?
- El publico principal es humano, agente, o ambos?
- El contenido sera versionado por fecha/proveedor o sera una fotografia "latest known"?
- Se permitiran fuentes no Markdown como PDF/web, o el repo solo acepta Markdown ya curado?
- El MCP server debe generar respuestas, o solo recuperar evidencia para que el agente cliente responda?

Mi recomendacion es que el MCP server sea principalmente retrieval/evidence server, no answer server. Deja que el agente cliente genere la respuesta, pero dale suficiente estructura para citar, verificar y seguir investigando.

## Fuentes consultadas

- `docs/8 Best RAG Tools Ranked for 2026 _ TECHSY.pdf`
- `docs/9 RAG Architectures Every AI Engineer Should Actually Understand.pdf`
- `docs/Beyond Vector Search_ 5 Next-Gen RAG Retrieval Strategies - MachineLearningMastery.com.pdf`
- `docs/The RAG Chunking Strategies that can actually surv... - SAP Community.pdf`
- Karpathy, "LLM Wiki": https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- FastMCP docs via `chub`: `fastmcp/package`, Python docs, version 3.1.0, updated 2026-03-12.
- MCP Python SDK docs via `chub`: `mcp/package`, Python docs, version 1.27.2, updated 2026-05-29.
- Claude Code skills docs: https://code.claude.com/docs/en/skills
