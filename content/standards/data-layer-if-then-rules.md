---
id: "standard.data-layer-if-then-rules"
title: "Reglas Si-Entonces para Data Layer de agentes IA"
type: "standard"
domain: ["agents", "data-layer", "standards", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "security", "agent"]
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
tags: ["rules", "standards", "if-then", "rag", "security"]
related:
  - "pattern.data-layer-decision-tree"
  - "pattern.data-layer-rag-pipeline"
  - "pattern.data-layer-access-security"
  - "checklist.data-layer-readiness"
---

# Reglas Si-Entonces para Data Layer de agentes IA

## Acceso al dato

- Si el dato es exacto, transaccional o fresco, entonces usar Tool/API con `as_of`.
- Si el dato es texto documental, entonces usar RAG tras validacion de fuente.
- Si el dato contiene relaciones multi-hop, entonces usar Knowledge Graph si existe, o RAG con metadata relacional y filtros.
- Si el dato es senal batch, entonces usar feature store o tabla versionada servida por tool.
- Si el dato contiene PII sin anonimizar, entonces usar indice por caso con AuthZ o no indexar.
- Si el usuario pide acceso directo a una tabla, entonces rechazar y rediseñar como capability gobernada.

## Pipeline RAG

- Si la fuente no esta aprobada, entonces parar en paso cero.
- Si el PDF es nativo con texto, entonces extraer directamente y validar estructura.
- Si el PDF es escaneado, entonces OCR + validacion.
- Si OCR no alcanza umbral, entonces HITL, re-OCR o bloqueo.
- Si la normativa tiene articulos, entonces chunking jerarquico + hybrid retrieval.
- Si el documento supera 100 paginas, entonces parent-child o map-reduce por capitulo.
- Si golden set falla, entonces no publicar indice.
- Si query no tiene resultado relevante, entonces abstenerse y loguear.

## Seguridad

- Si el corpus tiene tenant o roles, entonces aplicar filtros en retrieval, no en prompt.
- Si retrieval devuelve chunk de otro tenant, entonces parar despliegue y auditar.
- Si hay documento sospechoso de prompt injection, entonces cuarentena, borrar chunks y reingestar tras revision.
- Si el proveedor de embeddings no cumple soberania, entonces cambiar ruta o anonimizar antes.

## Operacion

- Si una nueva version degrada recall, latencia o permisos, entonces rollback.
- Si el indice esta en rebuilding, entonces servir vN-1 o declarar indisponibilidad controlada.
- Si un agente depende de tres o mas fuentes, entonces usar Agent Contract con versiones compatibles.
- Si una fuente cambia, entonces actualizar Data Contract y notificar consumidores.
