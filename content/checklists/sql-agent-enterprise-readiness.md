---
id: "checklist.sql-agent-readiness"
title: "Checklist de readiness para agentes sobre SQL"
type: "checklist"
domain: ["agents", "sql", "governance", "enterprise-data"]
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
tags: ["checklist", "readiness", "security", "governance", "production"]
related:
  - "playbook.sql-agent-enterprise"
  - "pattern.sql-agent-security"
  - "risk.sql-agent-risk-register"
---

# Checklist de readiness para agentes sobre SQL

## Antes de exponer SQL readonly

- [ ] Caso de uso tecnico justificado.
- [ ] Usuario o service account readonly.
- [ ] Replica, vista curada o entorno aislado.
- [ ] Parser SQL o validacion por AST.
- [ ] DDL, DML y multi-statement bloqueados.
- [ ] Allowlist de tablas, columnas y funciones.
- [ ] Limites de filas, timeout, coste y concurrencia.
- [ ] Logging de SQL, actor, tablas, filas y latencia.
- [ ] Pruebas adversariales y de exfiltracion.

## Antes de exponer tools parametrizadas

- [ ] Owner de negocio y owner tecnico.
- [ ] Input schema tipado.
- [ ] Validacion y autorizacion por parametro.
- [ ] SQL o API revisada por ingenieria.
- [ ] Errores seguros y no reveladores.
- [ ] Versionado de contrato.
- [ ] Tests de permisos, datos vacios y limites.
- [ ] Observabilidad por tool.

## Antes de exponer una capa semantica

- [ ] Metricas con definicion, formula y owner.
- [ ] Dimensiones y filtros permitidos.
- [ ] Freshness y limitaciones documentadas.
- [ ] Ejemplos verificados.
- [ ] Comparacion contra dashboards existentes.
- [ ] Dataset de evaluacion con preguntas reales.

## Antes de lanzar un MCP server empresarial

- [ ] Catalogo de tools y resources.
- [ ] Autenticacion y autorizacion por usuario.
- [ ] Politicas por dominio, tool y sensibilidad.
- [ ] Rate limiting y quotas.
- [ ] Auditoria centralizada.
- [ ] Revision de seguridad.
- [ ] Versionado y deprecacion de tools.
- [ ] SLOs y tablero de observabilidad.
