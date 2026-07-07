---
id: "pattern.data-layer-access-security"
title: "Seguridad de acceso y Early-Binding Guard en Data Layer"
type: "pattern"
domain: ["agents", "data-layer", "security", "enterprise-data"]
audience: ["security", "architect", "engineer", "agent"]
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
tags: ["security", "early-binding", "rbac", "abac", "pii", "prompt-injection"]
related:
  - "pattern.data-layer-governance-compliance"
  - "risk.data-layer-security-risk-register"
  - "pattern.data-layer-classification-mcp"
  - "checklist.data-layer-readiness"
---

# Seguridad de acceso y Early-Binding Guard en Data Layer

La seguridad de la Capa 1 debe aplicarse antes de que el contexto llegue al modelo. El prompt del sistema no es un control de acceso suficiente.

## Early-Binding Guard

Early-Binding Guard significa que los filtros de autorizacion se aplican directamente en el retrieval sobre metadata consultable. Si el usuario no tiene permisos, los fragmentos restringidos son invisibles para el motor de busqueda y no llegan al LLM.

El flujo esperado es:

```text
usuario -> identidad/rol/atributos -> retrieval con filtros -> chunks autorizados -> LLM
```

No es aceptable:

```text
retrieval global -> chunks sensibles -> prompt pide al LLM que ignore lo no permitido
```

## Politicas de acceso

La metadata debe incluir, segun el dominio, `tenant_id`, clasificacion, dominio, fuente, vigencia, owner, sensibilidad, jurisdiccion y scopes. RBAC puede ser suficiente en fases tempranas; ABAC es preferible cuando hay atributos dinamicos como region, unidad, expediente, cliente o caso.

## Tratamiento de informacion sensible

La informacion sensible debe pasar por cuatro fases: definicion, deteccion, tratamiento y recuperacion. El tratamiento puede ser masking, seudonimizacion, anonimizacion irreversible, particion por caso o prohibicion de indexacion.

La anonimización simple no garantiza no reidentificacion. Si el dato permite reconstruir identidad por contexto, debe tratarse como sensible.

## Prompt injection indirecta

Un documento autorizado puede contener instrucciones maliciosas. Early-Binding protege quien accede, pero no que instrucciones viajan dentro del contenido. Las mitigaciones incluyen:

- tratar contenido recuperado como datos, nunca como instrucciones;
- delimitar contexto recuperado;
- no permitir que el contenido recuperado autorice acciones;
- validacion de tool calls;
- HITL para acciones irreversibles;
- cuarentena de documentos sospechosos.

## Regla de produccion

El agente solo puede ver contexto ya autorizado, filtrado, trazable y marcado como dato. Cualquier autorizacion derivada del propio documento recuperado debe rechazarse.
