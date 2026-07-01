---
id: "pattern.sql-agent-entity-resolution"
title: "Entity resolution y MDM para agentes sobre datos SQL"
type: "pattern"
domain: ["agents", "sql", "mdm", "enterprise-data"]
audience: ["architect", "data-scientist", "engineer", "executive", "agent"]
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
tags: ["entity-resolution", "mdm", "customer-360", "multi-system", "identity"]
related:
  - "case-study.sql-agent-use-cases"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.sql-agent-security"
---

# Entity resolution y MDM para agentes sobre datos SQL

Cuando una respuesta requiere varios sistemas, el principal problema no es SQL sino identidad. El agente no deberia decidir libremente que un cliente, cuenta, proveedor o empleado en dos sistemas son la misma entidad.

## Cuando hace falta

Entity resolution es necesaria para customer 360, soporte + billing, CRM + ERP, fraude, riesgo, compliance, marketing cross-channel y cualquier caso donde varias fuentes representen la misma entidad con IDs distintos.

## Estrategias

- MDM formal con golden record.
- Tabla de correspondencias entre sistemas.
- Servicio de resolucion de entidades.
- Data product por entidad.
- Matching probabilistico con revision humana.
- Reglas deterministas para casos simples.

## Tool recomendada

```text
resolve_customer(name_or_id, source_system?, confidence_threshold?)
```

La respuesta debe incluir candidatos, confianza, sistemas fuente, razon de match y si requiere aprobacion humana.

## Recomendacion practica

No dejar que el agente haga joins cross-system por heuristica. Crear una fachada o tool de resolucion y obligar al agente a usarla antes de consultar datos de varios sistemas.
