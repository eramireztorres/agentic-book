---
id: "pattern.data-layer-rag-pipeline"
title: "Pipeline RAG de Capa 1 para agentes IA"
type: "pattern"
domain: ["agents", "data-layer", "rag", "retrieval", "enterprise-data"]
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
tags: ["rag", "chunking", "embedding", "retrieval", "rerank", "abstention"]
related:
  - "pattern.hybrid-retrieval"
  - "pattern.data-layer-ingestion-strategy"
  - "pattern.data-layer-data-quality"
  - "pattern.data-layer-production-operations"
  - "standard.data-layer-if-then-rules"
---

# Pipeline RAG de Capa 1 para agentes IA

Un pipeline RAG empresarial no empieza en embeddings. Empieza en aprobacion de fuente, clasificacion, owner, seguridad, OCR y metadatos.

## Flujo offline

1. Aprobar fuente y finalidad.
2. Extraer texto o transcripcion con trazabilidad.
3. Validar OCR si aplica.
4. Detectar PII, secretos y sensibilidad.
5. Normalizar estructura y metadata.
6. Crear chunks con `chunk_id`, `document_id`, pagina, vigencia, clasificacion y tenant si aplica.
7. Generar embeddings e indice.
8. Ejecutar golden set y publicar solo si pasa gates.

## Chunking

El chunk debe ser la unidad minima de informacion recuperable con sentido. El chunking por tokens fijo es rapido pero corta ideas. El overlap puede preservar contexto pero aumenta ruido. El chunking semantico o estructural respeta secciones, pero puede generar tamaños irregulares. Una estrategia madura combina estructura semantica con ventanas controladas.

Para normativa con articulos, usar chunking jerarquico y hybrid retrieval. Para documentos largos, considerar parent-child o map-reduce por capitulo.

## Embeddings e indexacion

El modelo de embeddings debe elegirse segun idioma, dominio, coste, soberania y rendimiento. En corpus español o multilingüe se debe validar empiricamente con golden questions, no asumir rendimiento por benchmarks generales.

## Retrieval online

1. Recibir consulta e identidad.
2. Aplicar filtros AuthZ antes de buscar.
3. Recuperar top-k con filtros.
4. Rerank opcional segun modo de madurez.
5. Construir contexto con `chunk_id`, pagina y source.
6. Abstenerse si no hay evidencia suficiente.
7. Loguear query hash, chunks, indice, usuario y timestamp.

## Respuesta

La respuesta debe citar chunks o documentos, declarar limitaciones y respetar freshness. Si hay discrepancia entre Tool/API y RAG, debe explicitarse y escalarse.
