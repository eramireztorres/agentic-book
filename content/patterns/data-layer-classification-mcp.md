---
id: "pattern.data-layer-classification-mcp"
title: "Clasificacion de datos y consumo mediante MCP"
type: "pattern"
domain: ["agents", "data-layer", "mcp", "enterprise-data"]
audience: ["architect", "engineer", "security", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-07-07"
source_quality: "curated"
source_urls:
  - "docs/Playbook_capa_1/Playbook_Capa1_DataLayer_v3.docx"
  - "docs/Playbook_capa_1/Playbook_Capa1_DataLayer_v2_reducida .docx"
source_type: "derived"
upstream_version: "2026-05-v3"
last_checked: "2026-07-07"
review_after: "2026-10-07"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["classification", "mcp", "data-access", "tools", "resources"]
related:
  - "concept.mcp"
  - "pattern.sql-agent-mcp-serving"
  - "pattern.data-layer-decision-tree"
  - "pattern.data-layer-access-security"
---

# Clasificacion de datos y consumo mediante MCP

La Capa 1 debe clasificar el dato antes de exponerlo a agentes. El mecanismo de consumo depende de si el dato es transaccional, documental, relacional, batch, semiestructurado, sensible o multimodal.

## Tipologias principales

- Datos exactos o transaccionales: Tool/API con freshness declarada.
- Texto documental: RAG con citas y metadata.
- Relaciones entre entidades: Knowledge Graph o RAG con relaciones explicitas.
- Señales batch: feature store o tabla versionada servida por tool.
- Datos semiestructurados: JSON Schema, parser y tool tipada.
- PII o datos sensibles: particion por caso, masking, anonimizacion o no indexacion.
- Multimedia: transcripcion preindexada o procesamiento dinamico segun golden questions.

## MCP como capa comun

MCP permite publicar todos los canales bajo una interfaz comun de capabilities: tools, resources y prompts. El agente no necesita saber si una capability consulta API, indice vectorial, feature store o catalogo; ve un contrato tipado con permisos y descripcion.

## Ventajas corporativas

- desacopla fuentes de modelos y aplicaciones;
- centraliza politicas de RBAC/ABAC;
- permite cambiar proveedor LLM sin reescribir conectores;
- estandariza prompts, resources y tools;
- facilita auditoria y catalogacion de capacidades.

## Reglas de exposicion

No exponer APIs externas directamente al agente sin wrapper. No exponer datos sensibles como resources globales. No publicar tools sin owner, contrato, rate limit, politica de autenticacion y logging.

## Resultado esperado

Cada fuente debe convertirse en una capability gobernada. La Capa 1 decide que canal usa; la Capa 2 consume el contrato.
