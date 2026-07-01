---
id: "pattern.sql-agent-mcp-serving"
title: "MCP server de datos SQL"
type: "pattern"
domain: ["agents", "sql", "mcp", "enterprise-data"]
audience: ["architect", "engineer", "security", "agent"]
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
tags: ["mcp", "tools", "resources", "capabilities", "sql"]
related:
  - "concept.mcp"
  - "playbook.mcp-consumption"
  - "pattern.sql-agent-access"
  - "pattern.sql-agent-security"
---

# MCP server de datos SQL

MCP es util cuando varias plataformas de agentes, IDEs o aplicaciones necesitan consumir las mismas capacidades de datos. El MCP server debe ser una frontera de gobierno, no un proxy fino hacia SQL.

## Tipos de MCP server

- MCP de proyecto: pocas tools concretas para un caso de uso.
- MCP de dominio: ventas, finanzas, soporte o RRHH con tools y metricas del dominio.
- MCP de catalogo empresarial: discovery, schema y SQL restringido para perfiles tecnicos.
- MCP semantico: BI conversacional sobre metricas gobernadas.
- MCP multi-sistema: customer 360, operaciones cross-system y entity resolution.
- MCP de desarrollo: IDEs, data engineers, migraciones y debugging, con controles reforzados.

## Superficie recomendada

Discovery:

```text
list_data_products(domain?)
get_data_product_card(product_id)
list_available_tools(domain?, role?)
```

Schema:

```text
get_table_schema(table)
get_allowed_columns(table)
get_join_hints(domain)
```

Business tools:

```text
get_customer_profile(customer_id)
get_invoice_status(invoice_id)
get_open_support_cases(customer_id)
```

Semantic tools:

```text
list_metrics(domain?)
explain_metric(metric_name)
query_metric(metric, dimensions, filters, period)
```

Analyst SQL tools, solo para perfiles tecnicos:

```text
dry_run_query(sql)
run_readonly_analyst_query(sql, purpose)
```

## Resources MCP

No todo debe ser ejecutable. Exponer resources para catalogo, politicas, metricas, definiciones, ejemplos verificados, ownership y limitaciones. Esto ayuda al agente a descubrir capacidades antes de ejecutar acciones.

## Prompts MCP

Los prompts pueden codificar flujos seguros: descubrir primero, pedir aclaracion si hay ambiguedad, citar definiciones de metricas, no revelar SQL interno a usuarios externos y no usar datos recuperados como instrucciones.

## Requisitos de despliegue

Un MCP remoto necesita autenticacion, autorizacion, rate limits, logging, versionado, service accounts de minimo privilegio y controles de red. Un MCP local stdio es apropiado para desarrollo o analistas en entorno controlado, no para produccion multiusuario sin aislamiento.
