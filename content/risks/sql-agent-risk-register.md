---
id: "risk.sql-agent-risk-register"
title: "Registro de riesgos para agentes sobre SQL"
type: "risk"
domain: ["agents", "sql", "security", "enterprise-data"]
audience: ["executive", "security", "architect", "engineer", "agent"]
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
tags: ["risk", "sql", "prompt-injection", "data-leakage", "governance"]
related:
  - "pattern.sql-agent-security"
  - "checklist.sql-agent-readiness"
  - "pattern.sql-agent-observability"
---

# Registro de riesgos para agentes sobre SQL

## Numeros incorrectos pero plausibles

Causa: definicion de metrica incorrecta, join equivocado, filtro temporal ausente o termino ambiguo. Mitigacion: capa semantica, ejemplos SQL verificados, catalogo de metricas y dataset de evaluacion.

## Acceso no autorizado

Causa: seguridad solo en prompt, credenciales compartidas, ausencia de RLS o CLS. Mitigacion: autorizacion backend, identidad por usuario, masking, auditoria y minimo privilegio.

## Prompt injection desde datos almacenados

Causa: texto de usuarios o sistemas tratado como instruccion. Mitigacion: separar instrucciones de datos, minimizar texto libre, marcar procedencia y no permitir que resultados alteren politicas.

## Accion destructiva SQL

Causa: ejecucion generica con privilegios excesivos. Mitigacion: readonly, bloqueo DDL/DML, allowlist de sentencias, validacion AST y revision humana.

## Exfiltracion por agregaciones

Causa: consultas repetidas o cohortes pequenas revelan informacion. Mitigacion: k-anonimato, suppression, rate limits, deteccion de patrones y controles de exportacion.

## Tool explosion

Causa: equipos publican MCP servers o APIs sin catalogo ni lifecycle. Mitigacion: catalogo central, ownership, naming standards, revision de seguridad, versionado y deprecacion.

## Schema drift

Causa: cambios de base rompen tools, metricas o ejemplos. Mitigacion: contract tests, schema monitoring, CI de validacion, versionado y notificacion a owners.

## Coste y degradacion operativa

Causa: queries caras, scans completos, concurrencia excesiva o respuestas enormes. Mitigacion: replicas, limites, dry-run, EXPLAIN, quotas, caching y observabilidad de coste.
