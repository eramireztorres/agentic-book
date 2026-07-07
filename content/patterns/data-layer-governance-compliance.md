---
id: "pattern.data-layer-governance-compliance"
title: "Gobierno, compliance y soberania en Capa 1 Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "governance", "compliance", "enterprise-data"]
audience: ["executive", "architect", "security", "data-scientist", "engineer"]
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
tags: ["governance", "compliance", "gdpr", "eu-ai-act", "sovereignty", "lineage"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-access-security"
  - "risk.data-layer-security-risk-register"
  - "pattern.data-layer-catalog"
---

# Gobierno, compliance y soberania en Capa 1 Data Layer

La Capa 1 debe asegurar que el conocimiento corporativo consumido por agentes respeta soberania, permisos, retencion, trazabilidad y normas aplicables. No basta con que el agente prometa comportarse bien.

## Soberania del dato

Cada fuente debe declarar restricciones de residencia, jurisdiccion, proveedor de embeddings, regiones permitidas, ruta de procesamiento y si puede salir a servicios externos. Esta informacion debe viajar como metadata consultable y formar parte del Data Contract.

## GDPR y EU AI Act

La ingesta debe aplicar minimizacion, limitacion de finalidad, confidencialidad, proteccion desde el diseño y proteccion por defecto. Para datos personales o alto riesgo, se requiere DPIA o revision equivalente, ademas de trazabilidad de fragmentos recuperados y capacidad de borrar chunks derivados de una fuente concreta.

## Linaje institucional

Toda respuesta relevante debe poder vincularse a:

- documento fuente;
- version de documento;
- `chunk_id` recuperado;
- version de indice y embeddings;
- version de prompt/modelo;
- filtros de permisos aplicados;
- usuario, rol y timestamp.

Sin linaje, no hay auditoria ni capacidad real de explicar por que el agente respondio algo.

## Roles

- Data Owner: responsable de valor, definicion y autorizacion de una fuente.
- Data Steward: mantiene calidad, metadata, freshness y golden sets.
- Security Architect: define controles tecnicos, cifrado, masking y aislamiento.
- Compliance/DPO: valida regulacion, DPIA y tratamiento de datos personales.
- AI/Product Owner: decide casos de uso y aceptacion funcional.
- Data Consumer: consume respuestas o tools, no accede libremente al dato.

## Gobierno federado

Un modelo hub-and-spoke suele ser practico: plataforma central para seguridad, catalogo, MCP y FinOps; autonomia de proyecto para chunking, preguntas de negocio y estrategia de recuperacion. El mecanismo de coordinacion es el Data Contract.
