---
id: "case-study.sql-agent-use-cases"
title: "Casos de uso para agentes sobre BBDD SQL empresariales"
type: "case-study"
domain: ["agents", "sql", "enterprise-data"]
audience: ["executive", "architect", "engineer", "data-scientist", "agent"]
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
tags: ["use-cases", "customer-service", "finance", "analytics", "legacy"]
related:
  - "playbook.sql-agent-enterprise"
  - "pattern.sql-agent-access"
  - "pattern.sql-agent-mcp-serving"
---

# Casos de uso para agentes sobre BBDD SQL empresariales

## Atencion al cliente con API existente

El agente debe llamar tools que envuelven APIs internas: perfil de cliente, pedidos, facturas y casos abiertos. No debe consultar tablas operacionales directamente. La API conserva permisos, reglas de negocio y consistencia con canales existentes.

## Finanzas con BI semantico

Para revenue, margen, forecast o comparativas, el agente debe usar `query_metric` sobre una capa semantica. Los resultados deben citar metrica, periodo, filtros, owner y freshness. Evitar formulas de KPI en prompts.

## Copiloto de analistas con catalogo grande

Usuarios tecnicos pueden usar discovery, schema y SQL readonly restringido. El entorno debe tener replica, allowlists, limites de coste, dry-run, auditoria y ejemplos verificados. Es aceptable permitir exploracion, pero no como interfaz para negocio general.

## Legacy SQL Server sin API

Primer paso: vistas curadas y usuario readonly. Segundo paso: tools parametrizadas para casos repetibles. Tercer paso: API o MCP de dominio. Evitar exponer todas las tablas legacy directamente; suelen contener nombres opacos, datos sensibles y reglas embebidas.

## Customer 360 multi-sistema

Cuando la respuesta combina CRM, SAP, billing, soporte y SQL operacional, la empresa necesita entity resolution y fachada agregadora. El agente no debe resolver identidades por heuristicas libres ni fusionar sistemas sin ownership.

## Datos regulados

En salud, banca, empleados, pagos, legal o seguridad, empezar con tools de negocio, agregaciones seguras, HITL y minimo privilegio. SQL libre solo en entornos tecnicos muy controlados.
