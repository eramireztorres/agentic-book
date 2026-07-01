---
id: "pattern.sql-agent-context-engineering"
title: "Context engineering para bases SQL consumidas por agentes"
type: "pattern"
domain: ["agents", "sql", "context-engineering", "enterprise-data"]
audience: ["engineer", "data-scientist", "architect", "agent"]
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
tags: ["context-engineering", "schema", "rag", "skills", "metadata"]
related:
  - "pattern.sql-agent-consumption"
  - "pattern.sql-agent-semantic-layer"
  - "pattern.sql-agent-mcp-serving"
---

# Context engineering para bases SQL consumidas por agentes

No se debe meter todo el esquema en el prompt. En bases empresariales grandes, el contexto debe descubrirse progresivamente y estar separado de las instrucciones.

## Discovery progresivo

El agente deberia empezar por catalogo de dominios, data products o tools disponibles. Solo despues debe solicitar schema, ejemplos o metricas concretas. Esto reduce ruido, fuga de informacion y coste.

## RAG sobre metadatos

Conviene indexar documentacion de tablas, columnas, metricas, owners, ejemplos verificados, reglas de join, politicas y limitaciones. El RAG debe recuperar contexto semantico antes de ejecutar tools o SQL.

## Skills por dominio

Para dominios complejos, una skill puede incluir glosario, pasos de razonamiento permitidos, tools preferidas, ejemplos y restricciones. La skill no sustituye permisos ni validacion backend; solo mejora el uso correcto de capacidades.

## Separar datos de instrucciones

Los datos devueltos por SQL, APIs o resources nunca deben tener autoridad para cambiar el comportamiento del agente. El prompt debe marcar resultados como datos no confiables y el backend debe impedir que esos resultados influyan en politicas de acceso.

## Ejemplos verificados

Los ejemplos de queries, metricas y casos deben estar versionados y probados. Son mas utiles que schemas gigantes porque muestran joins correctos, filtros por defecto y definiciones de negocio.
