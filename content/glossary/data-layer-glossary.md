---
id: "glossary.data-layer"
title: "Glosario de Capa 1 Data Layer para agentes IA"
type: "glossary"
domain: ["agents", "data-layer", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "agent", "executive"]
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
tags: ["glossary", "data-contract", "mcp", "rag", "governance"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-catalog"
  - "playbook.data-layer-handoff"
  - "concept.mcp"
---

# Glosario de Capa 1 Data Layer para agentes IA

## Agent Contract

Manifest versionado que declara que combinacion de fuentes, tools e indices puede consumir un agente en produccion.

## AuthN / AuthZ

Autenticacion y autorizacion. AuthN identifica al usuario o sistema; AuthZ decide que puede consultar.

## Chunk

Unidad minima recuperable por un sistema RAG. Debe tener identificador, fuente, version, metadata y sentido semantico suficiente.

## Data Contract

Contrato versionado publicado por la Capa 1 para una fuente, indice o capability. Declara calidad, permisos, freshness, limitaciones y criterios de publicacion.

## Data Steward

Rol que mantiene metadata, calidad, freshness, golden sets y gobierno operativo de una fuente.

## Early-Binding Guard

Aplicacion de filtros de permisos antes o durante retrieval, de forma que chunks no autorizados nunca llegan al LLM.

## Golden set

Conjunto de preguntas y evidencia esperada usado para evaluar retrieval y regresiones antes de publicar un indice.

## Grounding

Capacidad de anclar una respuesta a evidencia recuperada. Fallo tipico: el LLM ignora chunks y responde desde su entrenamiento.

## MCP

Model Context Protocol. Estandar para exponer tools, resources y prompts a agentes de forma interoperable.

## RAG

Retrieval-Augmented Generation. Patron en el que el LLM responde usando fragmentos recuperados de una fuente externa.

## Retrieval hibrido

Combinacion de busqueda lexical, como BM25, y busqueda vectorial. Es especialmente util para normativa, articulos, codigos y terminos exactos.

## Soberania del dato

Restricciones de ubicacion, jurisdiccion, proveedor, region y ruta de procesamiento que aplican a una fuente.

## Spotlighting

Tecnica para delimitar claramente contenido recuperado y reducir que el modelo lo interprete como instrucciones.
