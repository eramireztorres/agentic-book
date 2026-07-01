---
id: "platform.sql-agent-framework-guidance"
title: "Recomendaciones por framework para agentes sobre SQL"
type: "platform"
domain: ["agents", "sql", "frameworks", "enterprise-data"]
audience: ["engineer", "architect", "data-scientist", "agent"]
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
tags: ["langgraph", "openai-agents", "google-adk", "multi-agent", "frameworks"]
related:
  - "pattern.sql-agent-consumption"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.sql-agent-observability"
---

# Recomendaciones por framework para agentes sobre SQL

El framework no elimina la necesidad de disenar una superficie de datos segura. LangGraph, OpenAI Agents SDK, Google ADK u otros deben consumir las mismas tools gobernadas.

## LangGraph

Usar grafos explicitos para separar planificacion, acceso a datos, validacion y respuesta. Incluir nodos de SQL checker, policy check, human review y evaluacion. Persistir estado solo con datos necesarios.

## OpenAI Agents SDK

Usar function tools o MCP remoto para capacidades gobernadas. Definir schemas estrictos, instrucciones de abstencion y trazas. Evitar tools genericas que permitan saltarse APIs internas.

## Google ADK

Aprovechar agentes especializados y toolsets controlados. Si se integra con MCP Toolbox o servidores MCP, mantener permisos en backend y no en la descripcion de la tool.

## Multiagente

Separar agentes no significa multiplicar permisos. Solo el componente de acceso a datos deberia tener credenciales. El planner y el redactor pueden operar sobre resultados ya filtrados y auditados.

## Regla comun

Cualquier framework debe respetar catalogo, autorizacion, limites, logging, evaluaciones y HITL. Cambiar de framework no debe cambiar las politicas de datos.
