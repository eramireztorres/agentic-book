---
id: "pattern.sql-agent-observability"
title: "Observabilidad y evaluacion para agentes sobre SQL"
type: "pattern"
domain: ["agents", "sql", "observability", "evaluation", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "security", "executive"]
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
tags: ["observability", "evaluation", "audit", "metrics", "quality"]
related:
  - "playbook.sql-agent-enterprise"
  - "risk.sql-agent-risk-register"
  - "checklist.sql-agent-readiness"
---

# Observabilidad y evaluacion para agentes sobre SQL

Un agente que consulta datos empresariales debe ser observable antes de entrar en produccion. No basta con saber si respondio; hay que saber que tool uso, con que parametros, que datos recupero y si la respuesta fue correcta y autorizada.

## Metricas operativas

- Latencia por tool.
- Errores por tool y tipo de error.
- Filas devueltas y bytes transferidos.
- Coste SQL o warehouse.
- Timeouts, retries y circuit breakers.
- Frecuencia de abstenciones y escalados.

## Metricas de calidad

- Exactitud de parametros o SQL.
- Exactitud de metricas y agregaciones.
- Groundedness frente a resultados recuperados.
- Uso correcto de permisos.
- Tasa de aclaraciones cuando la pregunta es ambigua.
- Tasa de respuestas sin suficiente evidencia.

## Dataset de evaluacion

Debe incluir preguntas frecuentes, edge cases, permisos denegados, datos inexistentes, terminos ambiguos, prompt injection almacenada, consultas caras, agregaciones pequenas y comparacion con dashboards o respuestas verificadas.

## Auditoria minima

Registrar usuario, tenant, tool, parametros, SQL si existe, tablas, columnas sensibles, filas, latencia, coste, decision de politica, version de tool, version de prompt y resumen del resultado. Los logs no deben almacenar PII innecesaria.
