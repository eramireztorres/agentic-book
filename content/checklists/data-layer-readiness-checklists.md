---
id: "checklist.data-layer-readiness"
title: "Checklists de readiness para Data Layer"
type: "checklist"
domain: ["agents", "data-layer", "operations", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "security", "executive"]
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
tags: ["checklist", "readiness", "pre-indexing", "handoff", "operations"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-ingestion-strategy"
  - "pattern.data-layer-production-operations"
  - "playbook.data-layer-handoff"
---

# Checklists de readiness para Data Layer

## Pre-indexacion

- [ ] Fuente en allowlist.
- [ ] Owner asignado.
- [ ] Finalidad documentada.
- [ ] Clasificacion definida.
- [ ] Soberania y region permitida declaradas.
- [ ] PII y sensibilidad evaluadas.
- [ ] Retencion y purga definidas.
- [ ] OCR validado si aplica.
- [ ] Metadatos obligatorios definidos.
- [ ] Golden set inicial creado.

## Pre-publicacion de indice

- [ ] Chunks tienen `chunk_id` y `document_id`.
- [ ] Version de documento e indice registrada.
- [ ] Filtros RBAC/ABAC probados.
- [ ] Retrieval no devuelve chunks de otro tenant o dominio prohibido.
- [ ] Golden set supera umbral acordado.
- [ ] Respuestas citan evidencia.
- [ ] Abstencion probada para preguntas sin contexto.
- [ ] Data Contract generado.

## Pre-handoff a Capa 2

- [ ] Data Contract firmado por owner.
- [ ] Agent Contract actualizado si hay varias fuentes.
- [ ] Limitaciones conocidas documentadas.
- [ ] Version del indice comunicada.
- [ ] Fallback y rollback definidos.
- [ ] Contacto operativo disponible.

## Re-indexacion

- [ ] Cambios detectados por hash o version.
- [ ] Solo se regenera lo afectado cuando sea posible.
- [ ] Golden set ejecutado sobre vN+1.
- [ ] Comparativa contra vN revisada.
- [ ] Rollback preparado.

## Operacion continua mensual

- [ ] Freshness revisado.
- [ ] Fuentes obsoletas retiradas o marcadas.
- [ ] Golden sets actualizados con preguntas reales.
- [ ] Costes revisados.
- [ ] Incidentes y abstenciones analizados.
- [ ] Owners y permisos vigentes.
