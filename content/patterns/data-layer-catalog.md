---
id: "pattern.data-layer-catalog"
title: "Catalogo tecnico y semantico para Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "catalog", "enterprise-data"]
audience: ["architect", "data-scientist", "engineer", "executive", "agent"]
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
tags: ["catalog", "metadata", "taxonomy", "lineage", "semantic-layer"]
related:
  - "pattern.data-layer-governance-compliance"
  - "pattern.data-layer-classification-mcp"
  - "playbook.data-layer-handoff"
  - "glossary.data-layer"
---

# Catalogo tecnico y semantico para Data Layer

El catalogo convierte fuentes dispersas en conocimiento institucional descubrible, trazable y gobernable. No es solo inventario; es la capa que permite saber que informacion existe, que significa, quien la gobierna y que agentes dependen de ella.

## Cuando es necesario

El catalogo se vuelve critico cuando hay multiples dominios, fuentes compartidas, agentes que reutilizan capacidades, requisitos de compliance o necesidad de explicar linaje y freshness.

## Capa tecnica

La capa tecnica debe describir fuente, ubicacion, formato, owner, version, hash, pipeline, indice, permisos, estado de sincronizacion, freshness, clasificacion y dependencia de agentes.

## Capa semantica

La capa semantica define significado de dominios, taxonomias, sinonimos, entidades, terminos de negocio, relaciones y ejemplos. Permite que agentes no dependan de nombres fisicos de sistemas.

## Granularidad

La granularidad puede evolucionar:

1. metadatos basicos por fuente;
2. taxonomia por dominio y tipo documental;
3. relaciones entre entidades, documentos y capacidades;
4. grafo de conocimiento o catalogo de gobierno.

## Gobierno

Cada entrada del catalogo debe tener owner, estado, fecha de revision, politica de retencion, permisos, calidad y consumidores conocidos. Si un agente depende de una fuente, esa dependencia debe figurar en el Agent Contract.

## Riesgo mitigado

Sin catalogo, cada proyecto construye su propio RAG aislado, duplica contenido, pierde linaje y acaba con respuestas divergentes para la misma pregunta empresarial.
