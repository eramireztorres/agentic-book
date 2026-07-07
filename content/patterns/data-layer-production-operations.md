---
id: "pattern.data-layer-production-operations"
title: "Operacion en produccion de indices y pipelines Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "operations", "enterprise-data"]
audience: ["engineer", "architect", "data-scientist", "security", "agent"]
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
tags: ["operations", "cdc", "ci-cd", "metrics", "rollback", "golden-set"]
related:
  - "pattern.data-layer-rag-pipeline"
  - "pattern.data-layer-data-quality"
  - "playbook.data-layer-handoff"
  - "checklist.data-layer-readiness"
---

# Operacion en produccion de indices y pipelines Data Layer

La Capa 1 debe operarse como software y como producto de datos. Un indice publicado a agentes necesita versionado, pruebas, metricas, rollback y comunicacion a consumidores.

## CDC

Cada fuente debe tener deteccion de cambios mediante hash, version, timestamp o eventos. Si cambia el contenido, debe regenerarse la parte afectada, conservar linaje y actualizar manifest.

## CI/CD de datos

Un pipeline de datos debe ejecutar validaciones antes de publicar:

- fuente aprobada;
- metadata obligatoria;
- OCR PASS o HITL resuelto;
- permisos completos;
- golden set superado;
- regresiones de retrieval aceptables;
- Data Contract actualizado.

## Degradacion graceful

Si retrieval no encuentra evidencia, el agente debe abstenerse. Si el indice se esta reconstruyendo, puede servir vN-1 hasta que vN+1 pase gates. Si una fuente falla, la respuesta debe declarar limitacion en vez de inventar.

## Metricas

Medir latencia, coste, errores, recall@k, MRR, tasa de abstencion, chunks recuperados, freshness, OCR HITL, fallos de permisos y regresiones por version.

## Golden sets en produccion

Los golden sets no son solo preproduccion. Deben ejecutarse de forma recurrente y al cambiar documentos, chunking, embeddings, retriever, reranker o prompts de respuesta.

## Rollback

La publicacion de un indice nuevo debe ser reversible. Los agentes deben consumir un manifest o Agent Contract que indique version compatible, estado y triggers de rollback.
