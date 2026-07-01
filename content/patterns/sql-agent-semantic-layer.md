---
id: "pattern.sql-agent-semantic-layer"
title: "Capa semantica para BI conversacional con agentes"
type: "pattern"
domain: ["agents", "sql", "analytics", "enterprise-data"]
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
tags: ["semantic-layer", "metrics", "bi", "analytics", "kpi"]
related:
  - "playbook.sql-agent-enterprise"
  - "pattern.sql-agent-access"
  - "pattern.sql-agent-observability"
---

# Capa semantica para BI conversacional con agentes

SQL sabe que columnas existen. La capa semantica sabe que significan. Para preguntas de negocio sobre KPIs, revenue, churn, margen, cohortes o comparativas, la interfaz del agente deberia ser semantica y no SQL libre.

## Problema que resuelve

Sin capa semantica, cada prompt puede reinterpretar metricas, joins, filtros temporales y exclusiones. Esto genera numeros plausibles pero inconsistentes con BI corporativo.

## Tools recomendadas

```text
list_metrics(domain?)
explain_metric(metric_name)
query_metric(metric, dimensions, filters, period, granularity?)
compare_metric(metric, period_a, period_b, dimensions?)
drill_down(metric, by_dimension, filters?)
```

## Contrato minimo de una metrica

Una metrica debe declarar nombre, definicion de negocio, formula, owner, fuente, dimensiones permitidas, filtros por defecto, granularidades, reglas de seguridad, freshness, ejemplos verificados y limitaciones.

## Implementaciones posibles

Puede apoyarse en dbt Semantic Layer, LookML/Looker, Cube, MetricFlow, Snowflake Semantic Views, Databricks Genie, APIs analiticas internas o un modelo semantico propio. La herramienta concreta importa menos que mantener definiciones versionadas, testeadas y aprobadas.

## Cuando no basta

Una capa semantica no reemplaza entity resolution, MDM, permisos, auditoria ni controles de exportacion. Tampoco resuelve preguntas operacionales detalladas que requieren APIs de negocio.

## Recomendacion practica

Para BI conversacional en produccion, empezar con pocas metricas de alto valor, owner claro, definiciones auditadas y un dataset de evaluacion que compare respuestas del agente contra dashboards o queries verificadas.
