---
id: "playbook.data-layer"
title: "Playbook de Capa 1 Data Layer para agentes IA"
type: "playbook"
domain: ["agents", "data-layer", "enterprise-data", "governance"]
audience: ["executive", "architect", "engineer", "data-scientist", "security", "agent"]
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
tags: ["data-layer", "playbook", "governance", "rag", "mcp"]
related:
  - "pattern.data-layer-decision-tree"
  - "pattern.data-layer-governance-compliance"
  - "pattern.data-layer-rag-pipeline"
  - "playbook.data-layer-handoff"
  - "checklist.data-layer-readiness"
---

# Playbook de Capa 1 Data Layer para agentes IA

La Capa 1 Data Layer define como se ingesta, gobierna, clasifica, indexa y publica conocimiento corporativo para que agentes IA puedan consumirlo con seguridad. Su foco no es la orquestacion del agente, sino entregar fuentes, indices, tools y contratos confiables a la Capa 2.

## Promesa operativa

El playbook permite decidir en poco tiempo que mecanismo de acceso corresponde a cada tipo de dato, que controles de gobierno son obligatorios, como operar el pipeline documental y que contratos debe recibir el equipo que desarrolla agentes.

La regla base es:

```text
No todo dato debe ir a RAG.
No toda fuente debe exponerse como SQL o API directa.
Cada tipo de dato necesita un mecanismo, controles y contrato propios.
```

## Alcance

La Capa 1 cubre:

- clasificacion de fuentes y tipologias de dato;
- soberania, cumplimiento, roles y politicas de acceso;
- ingestion documental, OCR, chunking, embeddings, retrieval y validacion;
- catalogo tecnico y semantico;
- operacion en produccion, CDC, CI/CD de datos, golden sets y degradacion graceful;
- Data Contracts y Agent Contracts para publicar fuentes a agentes.

Quedan fuera el fine-tuning de modelos base, la evaluacion intrinseca del modelo y el diseno profundo de planning, memory o tool chaining de agentes. Esas responsabilidades pertenecen a la Capa 2, aunque dependen de los contratos entregados por la Capa 1.

## Audiencias

Responsables de requisitos y cumplimiento deben priorizar gobierno, compliance, catalogo y handoff. Desarrolladores de datos deben recorrer decision tree, clasificacion, pipeline y operacion. Equipos consumidores de agentes deben enfocarse en disponibilidad, freshness, limitaciones, Data Contract, Agent Contract y comportamiento ante degradacion.

## Niveles de madurez

- Startup: indice unico, owner informal, validacion manual y foco en validar valor rapido.
- Crecimiento: Data Steward parcial, politicas escritas, retrieval hibrido, rerank basico y golden set en CI.
- Enterprise: Data Owner formal por dominio, compliance, multi-indice, evaluacion continua, CI/CD con rollback y auditoria completa.

## Principio de exito

Un agente no debe recibir una carpeta de documentos sin gobierno. Debe recibir capacidades de datos con metadatos, permisos, freshness, trazabilidad, criterios de calidad y un contrato versionado que indique como debe consumirlas y cuando debe abstenerse.
