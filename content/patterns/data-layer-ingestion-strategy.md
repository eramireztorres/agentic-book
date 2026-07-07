---
id: "pattern.data-layer-ingestion-strategy"
title: "Estrategia corporativa de ingesta documental"
type: "pattern"
domain: ["agents", "data-layer", "ingestion", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "security"]
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
tags: ["ingestion", "medallion", "bronze", "silver", "gold", "ocr"]
related:
  - "pattern.data-layer-rag-pipeline"
  - "pattern.data-layer-data-quality"
  - "pattern.data-layer-catalog"
  - "checklist.data-layer-readiness"
---

# Estrategia corporativa de ingesta documental

La ingesta puede organizarse por compañia, por proyecto o de forma hibrida. La eleccion depende de escala, riesgo, autonomia de equipos y necesidad de reutilizacion.

## Modelo centralizado

Una plataforma comun define conectores, seguridad, catalogo, MCP, observabilidad y FinOps. Es adecuada para Enterprise, fuentes compartidas, regulacion y reutilizacion transversal.

## Modelo por proyecto

Cada equipo ingesta sus fuentes y ajusta chunking, retrieval y golden set a su caso. Es rapido, pero aumenta duplicidad, divergencia de politicas y riesgo de inconsistencia.

## Modelo hibrido

La opcion mas practica suele ser hub-and-spoke: plataforma central para seguridad, catalogo, MCP y estándares; autonomia del proyecto para estrategia de recuperacion, preguntas de negocio y criterios de aceptacion.

## Arquitectura Medallion

- Bronze: preserva raw data, origen, integridad, hash, version y trazabilidad.
- Silver: extrae texto, normaliza, detecta PII, limpia, enriquece metadata y valida OCR.
- Gold: publica chunks, embeddings, indices, permisos, manifest y controles de calidad para consumo por agentes.

## Paso cero

Antes de procesar, la fuente debe estar aprobada, tener owner, clasificacion, finalidad, politica de retencion y decision de mecanismo de acceso. Si la fuente no esta aprobada, la ingesta no debe empezar.

## Multimedia

Para imagen, audio y video se debe decidir si conviene preprocesar a texto o mantener procesamiento dinamico. La decision depende de golden questions, coste, auditabilidad, latencia y sensibilidad del contenido.
