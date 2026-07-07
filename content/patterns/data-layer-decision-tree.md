---
id: "pattern.data-layer-decision-tree"
title: "Arbol de decision para acceso a datos en Capa 1"
type: "pattern"
domain: ["agents", "data-layer", "enterprise-data"]
audience: ["architect", "engineer", "data-scientist", "agent"]
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
tags: ["decision-tree", "tool", "rag", "knowledge-graph", "feature-store"]
related:
  - "playbook.data-layer"
  - "pattern.data-layer-classification-mcp"
  - "pattern.data-layer-rag-pipeline"
  - "standard.data-layer-if-then-rules"
---

# Arbol de decision para acceso a datos en Capa 1

La decision mas importante de la Capa 1 es elegir el mecanismo correcto para cada fuente. El error mas comun es vectorizar todo por comodidad.

## Preguntas de decision

1. Si el dato es un numero exacto, fresco o transaccional, usar Tool/API con `as_of`. No vectorizar saldos, movimientos, estados de pedido ni posiciones de cliente.
2. Si el dato representa relaciones entre entidades, evaluar Knowledge Graph. Si no existe grafo, usar Tool o RAG con filtros y metadatos relacionales.
3. Si el dato es texto documental, usar RAG. Si contiene articulos, epigrafes, normativa o terminos exactos, preferir hybrid retrieval BM25 + vector.
4. Si el dato contiene PII sin anonimizar, no usar corpus global. Usar indice por `case_id`, expediente o particion con AuthZ fuerte.
5. Si es una senal batch, riesgo, scoring o propension, usar feature store + Tool. No recalcular modelos en cada turno del agente.
6. Si es JSON, log o semiestructurado estable, usar Tool con JSON Schema o transformacion controlada. No embeder logs crudos.
7. Si es imagen, audio o video, decidir si se preprocesa a texto o si requiere procesamiento dinamico multimodal. No embeder DNI, firma o biometria en RAG compartido.

## Seis reglas de oro

- G1: No vectorices el core; usa Tool/API con `as_of`.
- G2: Sin validacion OCR hay informacion perdida y riesgo de alucinacion.
- G3: PII requiere indice por caso o anonimización previa; nunca corpus global compartido.
- G4: Normativa con articulos requiere retrieval hibrido.
- G5: Sin `chunk_id` no hay auditoria suficiente para produccion regulada.
- G6: Si retrieval no devuelve contexto relevante, el agente se abstiene.

## Regla de precedencia en respuestas mixtas

Cuando una respuesta combina datos exactos e interpretacion documental, la cifra exacta viene de Tool/API, la interpretacion viene de RAG con cita y cualquier discrepancia debe explicitarse y escalarse. El agente no debe elegir una fuente sin evidencia.

## Antipatron

No construir un unico RAG corporativo para todo. La Capa 1 debe componer tools, RAG, catalogos, feature store, Knowledge Graph e indices particionados segun riesgo y naturaleza del dato.
