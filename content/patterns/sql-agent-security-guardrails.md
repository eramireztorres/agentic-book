---
id: "pattern.sql-agent-security"
title: "Seguridad y guardarrailes para agentes sobre SQL"
type: "pattern"
domain: ["agents", "sql", "security", "enterprise-data"]
audience: ["security", "architect", "engineer", "executive", "agent"]
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
tags: ["security", "governance", "pii", "prompt-injection", "authorization"]
related:
  - "playbook.sql-agent-enterprise"
  - "risk.sql-agent-risk-register"
  - "checklist.sql-agent-readiness"
---

# Seguridad y guardarrailes para agentes sobre SQL

Los guardarrailes no deben vivir solo en el agente. Deben estar en identidad, backend, MCP server, APIs, capa semantica, base de datos y observabilidad.

## Principios no negociables

- Minimo privilegio para usuarios y service accounts.
- Autorizacion por identidad real del usuario, no credenciales compartidas amplias.
- Row-level security, column-level security, masking y vistas curadas cuando aplique.
- Separacion entre instrucciones del sistema y datos recuperados.
- Bloqueo de DDL, DML, multi-statement y funciones peligrosas para SQL exploratorio.
- Limites de filas, tiempo, coste, concurrencia y tamaño de respuesta.
- Auditoria de tool, actor, parametros, SQL, tablas, filas, politica aplicada y resultado resumido.

## Prompt injection directa e indirecta

Los valores almacenados en la BBDD pueden contener texto malicioso. El agente debe tratarlos como datos, no como instrucciones. El backend debe minimizar campos de texto libre, marcar procedencia, aplicar filtros y evitar que resultados de DB modifiquen politicas de ejecucion.

## Exfiltracion por agregaciones

Aunque no se devuelvan filas individuales, consultas repetidas sobre cohortes pequenas pueden revelar informacion sensible. Usar thresholds de k-anonimato, suppression de celdas pequenas, rate limits, deteccion de patrones y revision humana en dominios regulados.

## SQL validator minimo

Un validador de SQL exploratorio debe aceptar solo una sentencia, permitir solo `SELECT` o dialecto equivalente, bloquear DDL/DML, bloquear tablas fuera de allowlist, inyectar limites si faltan, ejecutar `EXPLAIN` o dry-run y rechazar consultas con coste excesivo.

## HITL

Usar aprobacion humana para dominios sensibles, acciones con impacto economico, exportaciones grandes, cohortes pequenas, consultas de empleados, salud, legal, pagos o cualquier resultado que pueda afectar a clientes.
