# Curación e ingesta de contenido

`docs/` conserva fuentes originales y material humano. Solo los Markdown situados bajo `content/` forman el corpus canónico que valida e ingiere Agentic Book.

## Organización recomendada

| Directorio | Uso |
|---|---|
| `content/playbooks/` | Guías end-to-end, modelos operativos y roadmaps. |
| `content/patterns/` | Patrones reutilizables de arquitectura, seguridad, ingesta o despliegue. |
| `content/checklists/` | Comprobaciones de readiness, lanzamiento u operación. |
| `content/risks/` | Riesgos, fallos, mitigaciones y controles. |
| `content/case-studies/` | Casos concretos y recorridos de referencia. |
| `content/concepts/` | Definiciones fundamentales. |
| `content/platforms/` | Frameworks, SDK, runtimes o proveedores. |
| `content/glossary/` | Términos y definiciones breves. |
| `content/standards/` | Reglas, políticas y criterios normativos. |
| `content/tools/` | Contratos de tools, MCP o wrappers de API. |

Los subdirectorios ayudan a mantener el corpus. El retrieval depende principalmente del frontmatter y del texto, por lo que `type`, `domain`, `tags` y la carpeta deben ser coherentes.

## División semántica

Un archivo debe cubrir una unidad que un agente pueda recuperar y entender de forma independiente. Como orientación, suele funcionar bien un documento de 500 a 1.500 palabras, pero la frontera semántica tiene prioridad sobre la longitud.

No dividas una fuente por páginas:

```text
content/playbooks/fuente-paginas-1-5.md
content/playbooks/fuente-paginas-6-10.md
```

Divídela por responsabilidad:

```text
content/playbooks/fuente-overview.md
content/patterns/fuente-ingestion.md
content/patterns/fuente-security.md
content/checklists/fuente-readiness.md
content/risks/fuente-risk-register.md
content/glossary/fuente-glossary.md
```

Antes de crear un documento, busca conceptos equivalentes en `content/`. Amplía o enlaza el documento canónico cuando ya exista; no copies grandes bloques entre chunks.

## Frontmatter requerido

```markdown
---
id: "pattern.example"
title: "Patrón de ejemplo"
type: "pattern"
domain: ["agents", "mcp", "enterprise-data"]
audience: ["architect", "engineer", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-07-13"
source_quality: "curated"
source_urls:
  - "docs/ruta/a/la/fuente.md"
source_type: "derived"
upstream_version: "2026-07-13"
last_checked: "2026-07-13"
review_after: "2026-10-13"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["mcp", "agents"]
related:
  - "concept.mcp"
---

# Patrón de ejemplo

Contenido coherente y autosuficiente.
```

La validación exige identificadores únicos, referencias `related` existentes, valores admitidos para los campos enumerados y metadata de freshness. Las fuentes no internas deben declarar `source_urls`.

## Flujo de actualización

Con Docker:

```bash
docker compose restart agentic-book-mcp
docker compose logs -f agentic-book-mcp
```

Con instalación nativa en Unix:

```bash
.venv/bin/agentic-book --content-root content validate-content --strict-freshness
.venv/bin/agentic-book --content-root content ingest --dry-run
.venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
.venv/bin/agentic-book --data-dir .agentic-book-data eval-matrix
```

En Windows sustituye `.venv/bin/agentic-book` por `.\.venv\Scripts\agentic-book.exe`.

Si la actualización cambia rankings de manera intencionada, revisa `evals/retrieval/ground_truth.json` y `evals/retrieval/fusion_ground_truth.json`. No adaptes el ground truth para ocultar una regresión.

## Freshness y propuestas

```bash
.venv/bin/agentic-book --data-dir .agentic-book-data stale-report
.venv/bin/agentic-book --data-dir .agentic-book-data propose-doc-update concept.mcp --reason "Posible cambio del protocolo upstream"
```

Las propuestas se guardan en `.proposals/documentation-updates/` para revisión humana. No modifican automáticamente el contenido canónico ni crean issues o pull requests.
