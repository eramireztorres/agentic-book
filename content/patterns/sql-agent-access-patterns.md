---
id: "pattern.sql-agent-access"
title: "Patrones de acceso a SQL para agentes"
type: "pattern"
domain: ["agents", "sql", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "agent"]
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
tags: ["sql", "api", "tools", "readonly", "duckdb"]
related:
  - "playbook.sql-agent-enterprise"
  - "pattern.sql-agent-api-wrappers"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.sql-agent-semantic-layer"
---

# Patrones de acceso a SQL para agentes

El patron de acceso debe elegirse por riesgo y caso de uso, no por facilidad tecnica. Las opciones principales son SQL readonly, tools parametrizadas, APIs internas, capa semantica, MCP server y sandbox tabular.

## SQL readonly controlado

Usar solo para PoC internas, analistas, data engineers y exploracion tecnica acotada. Debe operar sobre replica o vistas curadas, con credenciales readonly, allowlist de esquemas, bloqueo de DDL/DML, limites de filas, timeout, coste maximo y logging completo.

La tool no deberia llamarse `run_query`. Un nombre como `run_readonly_analyst_query` comunica que es una capacidad tecnica, no una tool de negocio para usuarios finales.

## Tools parametrizadas

Usar para produccion operacional: pedidos, facturas, tickets, inventario, contratos, clientes y cuentas. La SQL queda revisada por ingenieria y el agente solo rellena parametros tipados.

Ejemplos:

```text
get_customer_profile(customer_id)
get_customer_orders(customer_id, start_date, end_date, status?)
get_invoice_status(invoice_id)
get_product_inventory(product_id, location?)
```

Este patron reduce errores de joins, evita SQL inventado y permite autorizacion por tool y por entidad.

## APIs internas existentes

Si la empresa ya tiene APIs internas con reglas de negocio, permisos y validaciones, envolver esas APIs es preferible a consultar SQL directamente. El agente debe respetar los mismos contratos que las aplicaciones corporativas.

## Capa semantica

Para preguntas de BI o KPI, usar tools como `list_metrics`, `explain_metric`, `query_metric` y `drill_down`. Las definiciones de revenue, churn, margen y periodos no deben vivir en prompts.

## Sandbox tabular

Para CSV y Excel, usar DuckDB o Python sandbox con limites. No meter tablas completas en el prompt. La ejecucion debe inspeccionar schema, muestrear de forma segura, ejecutar consultas acotadas y exportar resultados grandes fuera del contexto conversacional.

## Antipatron principal

No usar un unico `execute_sql` para todos. Mezcla usuarios tecnicos con usuarios de negocio, aumenta fugas, eleva coste y convierte el prompt en el principal control de seguridad.
