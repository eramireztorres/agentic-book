---
id: "playbook.sql-agent-enterprise"
title: "Playbook empresarial para agentes sobre BBDD SQL"
type: "playbook"
domain: ["agents", "sql", "enterprise-data"]
audience: ["executive", "architect", "engineer", "data-scientist", "security", "agent"]
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
tags: ["sql", "enterprise", "governance", "mcp", "semantic-layer"]
related:
  - "pattern.sql-agent-access"
  - "pattern.sql-agent-security"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.sql-agent-observability"
  - "checklist.sql-agent-readiness"
---

# Playbook empresarial para agentes sobre BBDD SQL

La decision critica no es que framework de agentes se usa, sino que superficie de datos se expone. Una empresa no deberia disenar acceso directo a SQL para un LLM; deberia disenar capacidades de datos gobernadas para agentes.

## Principio central

```text
No exponer tablas por comodidad.
Exponer capacidades de negocio con permisos, contratos, observabilidad y evaluacion.
```

Un agente puede consumir una BBDD SQL mediante SQL readonly, tools parametrizadas, APIs internas, capa semantica, MCP servers de dominio o empresa, sandboxes tabulares y fachadas multi-sistema. La eleccion depende del riesgo, la repetibilidad, el tipo de usuario y si ya existen controles corporativos.

## Arbol de decision

Si ya existe una API interna que aplica reglas de negocio, identidad y permisos, el agente debe consumir esa API mediante una tool o un MCP server. Saltarse la API para consultar SQL duplica logica y debilita gobierno.

Si el caso de uso es repetible, como pedidos, facturas, inventario, contratos, tickets o estado de cliente, se recomiendan tools parametrizadas. Si el caso es exploratorio y el usuario es tecnico, puede permitirse SQL readonly con restricciones fuertes.

Si la pregunta es analitica, como revenue, churn, margen, cohortes o forecast, la interfaz correcta suele ser una capa semantica. Si la pregunta es operacional, conviene API o tool de negocio.

Si la respuesta requiere varios sistemas, como SQL Server, SAP, Salesforce, billing y soporte, el agente no deberia integrar todo por su cuenta. Hace falta una fachada: MCP empresarial, API agregadora, data product platform, data virtualization o micro-BBDD por entidad.

## Criterios de exito empresarial

- Los permisos se aplican en backend, no solo en prompt.
- Las tools exponen capacidades de negocio, no tablas fisicas sin contexto.
- Las metricas, joins y definiciones viven fuera del prompt.
- Los datos sensibles se minimizan, agregan, enmascaran o bloquean.
- Cada llamada registra actor, tool, parametros, tablas, filas, latencia, coste y decision de politica.
- Existen datasets de evaluacion con casos reales, permisos, prompt injection, agregaciones y preguntas sin respuesta.

## Modelo operativo

Direccion prioriza casos de uso con valor medible y riesgo aceptable. Data owners definen semantica, calidad, clasificacion y ownership. Ingenieria implementa APIs, MCP servers, validadores, despliegue y observabilidad. Seguridad define politicas, auditoria, masking, HITL y revision de riesgos. Los consumidores validan respuestas, limites y flujo de trabajo.

## Regla final

El exito no es que el agente pueda consultar SQL. El exito es que conteste preguntas utiles, autorizadas, trazables y mantenibles sin convertir la BBDD en una superficie de exfiltracion o en una fuente de numeros plausibles pero incorrectos.
