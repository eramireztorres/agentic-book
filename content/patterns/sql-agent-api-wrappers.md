---
id: "pattern.sql-agent-api-wrappers"
title: "APIs internas como tools para agentes"
type: "pattern"
domain: ["agents", "apis", "sql", "enterprise-data"]
audience: ["architect", "engineer", "security", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-07-01"
source_quality: "curated"
source_urls:
  - "docs/LLM_SQL/playbook_sql_agents_mcp_accionable_v2.md"
source_type: "derived"
upstream_version: "2026-07-01-v2"
last_checked: "2026-07-01"
review_after: "2026-10-01"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["api", "tools", "openapi", "business-rules", "governance"]
related:
  - "pattern.sql-agent-access"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.sql-agent-security"
---

# APIs internas como tools para agentes

Si una API interna ya contiene reglas de negocio, permisos, validacion y trazabilidad, el agente deberia consumir esa API. Consultar SQL directamente suele duplicar logica y crear respuestas inconsistentes con las aplicaciones corporativas.

## Patron recomendado

```text
Agente -> tool o MCP tool -> API interna -> sistema de negocio o BBDD
```

El wrapper debe convertir una operacion corporativa en una tool clara, tipada y documentada. No debe exponer toda la API sin curacion.

## Diseno de wrapper

Una tool sobre API debe tener nombre de negocio, descripcion operativa, input schema estricto, validacion local, propagacion de identidad, manejo seguro de errores, timeouts, retries controlados y logging.

Ejemplo:

```text
get_invoice_status(invoice_id)
```

mejor que:

```text
call_billing_api(path, method, body)
```

## Curacion de OpenAPI

Si se parte de OpenAPI, eliminar endpoints administrativos, operaciones destructivas, campos internos, parametros ambiguos y respuestas demasiado grandes. Agrupar endpoints en pocas tools de negocio y documentar ejemplos de uso.

## Evitar tool explosion

No publicar cientos de endpoints como tools. El agente necesita capacidades comprensibles, no un mapa completo de microservicios. Priorizar las operaciones con valor, owner, contrato estable y controles claros.
