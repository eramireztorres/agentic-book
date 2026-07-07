---
id: "pattern.data-layer-deployment-maturity"
title: "Modos de despliegue y madurez para Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "operations", "enterprise-data"]
audience: ["executive", "architect", "engineer", "security"]
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
tags: ["maturity", "deployment", "startup", "enterprise", "legacy-bridge"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-governance-compliance"
  - "pattern.data-layer-production-operations"
  - "playbook.data-layer-handoff"
---

# Modos de despliegue y madurez para Data Layer

La Capa 1 debe ajustarse a la madurez del equipo. No todas las organizaciones necesitan empezar con multi-indice, cross-encoder y gobierno completo, pero todas deben saber que riesgos estan aceptando.

## Startup

Un modo Startup puede usar un indice unico, chunking por seccion, validacion manual, propietario informal y un conjunto pequeno de preguntas de control. Es aceptable para validar valor rapido si el corpus no contiene datos personales o regulados.

Controles minimos:

- owner identificado;
- fuentes allowlisted;
- validacion manual tras reingesta;
- logs basicos de consulta;
- abstencion si retrieval no encuentra evidencia.

## Crecimiento

El modo Crecimiento introduce Data Steward parcial, politicas escritas, particion por dominio, hybrid retrieval, rerank basico y golden set en CI. Empieza a medir recall, calidad de respuesta y regresiones del indice.

Controles esperados:

- RBAC o ABAC en retrieval;
- masking de PII;
- OCR con umbral y cola HITL;
- golden set por corpus;
- versionado basico de indices.

## Enterprise

El modo Enterprise requiere Data Owner formal por dominio, compliance, multi-indice, auditoria completa, evaluacion continua, CI/CD de datos con rollback, politicas de retencion y controles de soberania.

Controles esperados:

- row-level o metadata-level security;
- segregacion por tenant o filtros robustos;
- catalogo tecnico y semantico;
- linaje de respuesta a chunk;
- Data Contract y Agent Contract versionados;
- rollback automatico si degradan metricas.

## Legacy Bridge

Muchas empresas parten de data warehouses, lakes y queries SQL ya aprobadas. El modo Legacy Bridge permite exponer vistas o APIs como tools, y crear RAG solo sobre corpus documental nuevo. No requiere reescribir toda la plataforma antes del primer agente.

Primer agente realista:

```text
2-3 tools sobre vistas existentes + 1 indice RAG pequeño y no personal + owner + allowlist + validacion manual
```

## Criterio de escalado

Escalar de Startup a Crecimiento cuando el corpus supera pocos documentos, hay usuarios recurrentes, aparece PII, hay dependencia de negocio o se necesita medir regresiones. Escalar a Enterprise cuando hay dominios multiples, regulacion, multi-tenant o agentes en produccion.
