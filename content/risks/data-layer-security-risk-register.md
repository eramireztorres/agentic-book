---
id: "risk.data-layer-security-risk-register"
title: "Registro de riesgos de Data Layer para agentes IA"
type: "risk"
domain: ["agents", "data-layer", "security", "enterprise-data"]
audience: ["security", "architect", "executive", "engineer", "agent"]
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
tags: ["risk", "pii", "prompt-injection", "exfiltration", "governance"]
related:
  - "pattern.data-layer-access-security"
  - "pattern.data-layer-governance-compliance"
  - "checklist.data-layer-readiness"
  - "pattern.data-layer-production-operations"
---

# Registro de riesgos de Data Layer para agentes IA

## Vectorizar datos transaccionales core

Riesgo: respuestas obsoletas, saldos incorrectos o decisiones basadas en datos no frescos. Mitigacion: Tool/API con `as_of`, permisos y fuente de verdad operacional.

## PII en corpus global

Riesgo: usuarios no autorizados recuperan informacion personal por similitud. Mitigacion: indice por `case_id`, AuthZ, masking, anonimizacion o prohibicion de indexacion.

## Prompt injection indirecta

Riesgo: un documento recuperado instruye al agente para ignorar politicas, revelar secretos o ejecutar tools. Mitigacion: separacion dato/instruccion, delimitadores, hardening, validacion de tool calls y HITL.

## Fallo OCR o paginas faltantes

Riesgo: alucinaciones por informacion no indexada o incompleta. Mitigacion: validacion OCR, umbral de confianza, cola HITL y bloqueo de publicacion si faltan paginas criticas.

## Retrieval sin resultado relevante

Riesgo: el agente inventa respuesta. Mitigacion: abstencion obligatoria, logging, mensaje seguro y escalado a owner.

## Fragmentos sin `chunk_id`

Riesgo: no hay auditoria ni capacidad de explicar o borrar respuesta. Mitigacion: `chunk_id`, version de documento, version de indice y linaje por respuesta.

## Filtros de permisos tardios

Riesgo: datos sensibles llegan al LLM y se confia en el prompt para ocultarlos. Mitigacion: Early-Binding Guard en retrieval.

## Golden set insuficiente

Riesgo: degradaciones del indice llegan a produccion. Mitigacion: golden set por corpus, recall@k minimo, pruebas en CI y rollback.

## Costes no gobernados

Riesgo: embeddings, rerankers y procesamiento multimodal escalan sin control. Mitigacion: FinOps, caching, limites, modelos adecuados y decision explicita por caso.
