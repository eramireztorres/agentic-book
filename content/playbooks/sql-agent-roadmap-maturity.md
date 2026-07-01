---
id: "playbook.sql-agent-roadmap-maturity"
title: "Roadmap y modelo de madurez para agentes sobre SQL"
type: "playbook"
domain: ["agents", "sql", "roadmap", "enterprise-data"]
audience: ["executive", "architect", "engineer", "security", "data-scientist"]
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
tags: ["roadmap", "maturity", "implementation", "governance", "production"]
related:
  - "playbook.sql-agent-enterprise"
  - "checklist.sql-agent-readiness"
  - "pattern.sql-agent-observability"
---

# Roadmap y modelo de madurez para agentes sobre SQL

## Primeros 30 dias

Seleccionar uno o dos casos de uso, clasificar datos, identificar owners, revisar APIs existentes, crear vistas curadas o wrappers, definir permisos, preparar logging y construir un dataset inicial de evaluacion.

## Dias 31-60

Implementar tools parametrizadas, validar SQL readonly si aplica, incorporar capa semantica para metricas, crear tests de permisos y prompt injection, revisar casos adversariales y documentar limitaciones.

## Dias 61-90

Publicar MCP server de dominio o toolset estable, anadir catalogo o resources MCP, versionar tools, automatizar evaluaciones, crear dashboard de observabilidad y ejecutar piloto con usuarios reales.

## Despues de 90 dias

Escalar a varios dominios, integrar entity resolution, mejorar MDM, formalizar gobierno de MCP servers, definir lifecycle de tools, incorporar HITL para alto riesgo y crear proceso de revision continua.

## Modelo de madurez

- Nivel 0: acceso manual y sin agente.
- Nivel 1: SQL readonly PoC para tecnicos.
- Nivel 2: tools parametrizadas para casos repetibles.
- Nivel 3: capa semantica y APIs gobernadas.
- Nivel 4: MCP de dominio con tools, resources y prompts.
- Nivel 5: MCP empresarial gobernado, multi-dominio, con politicas, evals, observabilidad y entity resolution.

La mayoria de organizaciones deberian pasar por niveles 1 a 3 antes de intentar un MCP empresarial de nivel 5.
