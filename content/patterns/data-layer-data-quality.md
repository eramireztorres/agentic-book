---
id: "pattern.data-layer-data-quality"
title: "Calidad, OCR e higiene del conocimiento en Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "quality", "enterprise-data"]
audience: ["engineer", "data-scientist", "architect", "security"]
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
tags: ["quality", "ocr", "hygiene", "deduplication", "golden-set"]
related:
  - "pattern.data-layer-ingestion-strategy"
  - "pattern.data-layer-rag-pipeline"
  - "pattern.data-layer-production-operations"
  - "checklist.data-layer-readiness"
---

# Calidad, OCR e higiene del conocimiento en Data Layer

La calidad de la Capa 1 determina si el agente responde con evidencia o alucina con confianza. La higiene del conocimiento es un control de seguridad y fiabilidad, no solo una mejora tecnica.

## Controles de higiene

- eliminar duplicados y versiones obsoletas;
- detectar contradicciones entre fuentes;
- declarar vigencia y fecha de revision;
- normalizar titulos, secciones y metadata;
- mantener owner y fuente de verdad;
- conservar hashes para CDC;
- separar fuentes aprobadas de borradores.

## OCR

Los PDFs escaneados, imagenes y documentos con baja calidad requieren OCR con umbral. Si la confianza baja del umbral, el documento debe ir a HITL, re-OCR o bloqueo segun criticidad.

Regla practica:

```text
OCR PASS -> indexar
OCR HITL -> revision humana antes de publicar
OCR BLOCK -> no publicar en indice de produccion
```

## Golden sets

Un golden set es un conjunto de preguntas esperadas con respuestas, chunks o documentos correctos. Debe ejecutarse antes de publicar una nueva version del indice y despues de cambios en chunking, embeddings, filtros o rerank.

## Calidad de salida

No basta con medir recuperacion. Tambien hay que medir si el agente usa el contexto, cita correctamente, evita responder sin evidencia y respeta permisos.

## Fallos tipicos

- documento incompleto indexado como si estuviera completo;
- versiones antiguas conviven con nuevas sin vigencia;
- OCR pierde tablas o paginas;
- chunking mezcla temas;
- metadata de permisos falta o es inconsistente;
- golden set no cubre preguntas reales.
