---
id: "playbook.data-layer-handoff"
title: "Handoff de Data Layer a agentes: Data Contract y Agent Contract"
type: "playbook"
domain: ["agents", "data-layer", "contracts", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "agent", "security"]
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
tags: ["data-contract", "agent-contract", "handoff", "rollout", "manifest"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-production-operations"
  - "pattern.data-layer-catalog"
  - "checklist.data-layer-readiness"
---

# Handoff de Data Layer a agentes: Data Contract y Agent Contract

La Capa 1 no publica datos de forma informal. Publica contratos. Sin Data Contract y Agent Contract, la Capa 2 no sabe que consume, con que version, bajo que permisos ni con que limitaciones.

## Data Contract

Un Data Contract describe una fuente o indice concreto. Debe incluir:

- identificador y version;
- owner y steward;
- fuentes incluidas y excluidas;
- freshness y `as_of`;
- formato de chunks y metadatos;
- permisos y clasificacion;
- calidad garantizada;
- golden set y ultima evaluacion;
- limitaciones conocidas;
- triggers de rollback;
- contacto operativo.

## Agent Contract

Un Agent Contract describe la combinacion de fuentes, tools e indices que un agente puede usar en produccion. Es necesario cuando un agente depende de varias capacidades con versiones distintas.

Debe declarar:

- fuentes compatibles;
- versiones aprobadas;
- rangos de compatibilidad;
- fallback y degradacion graceful;
- politicas de abstencion;
- restricciones de uso;
- gates cumplidos.

## Rollout sin romper agentes

La publicacion debe ser progresiva: staging, golden set, QA, porcentaje bajo de trafico, comparacion de metricas y subida gradual. Si recall, latencia, errores o permisos degradan, se vuelve a la version anterior.

## Ejemplo de aplicacion

En un copiloto hipotecario, normativa, posicion de cliente y procedimientos internos pueden versionar por separado. El Agent Contract fija que combinacion exacta ha pasado pruebas, que fuentes faltan, que limitaciones declarar y a quien escalar incidencias.

## Regla practica

El agente no lee “el ultimo indice” por magia. Lee lo que el manifest o Agent Contract declara como publicable.
