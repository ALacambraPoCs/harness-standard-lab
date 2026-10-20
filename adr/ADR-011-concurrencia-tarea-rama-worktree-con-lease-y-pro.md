---
id: ADR-011
titulo: "Concurrencia: tarea → rama → worktree, con lease y propiedad por segmento"
estado: propuesto
fecha: 2026-10-19
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-011 · Concurrencia: tarea → rama → worktree, con lease y propiedad por segmento [Fase 4]

**Recomendación**
- Por cada tarea: una rama y un worktree.
- Las tareas se reclaman con un *lease* (el propietario y la caducidad quedan en el archivo de la tarea, y se resuelve por merge en la rama principal o por la API de issues).
- Las tareas que tocan el mismo segmento se serializan, o se paralelizan solo con un contrato de interfaz explícito.
- Antes de integrar, rebase o merge contra la rama principal, y merge queue.

**Justificación**
- P7. S-GIT: una misma rama no puede estar activa en dos worktrees.
- S-VILA p.23: coordinación de tareas con locks de archivo.
- Claude Code tiene `--worktree` (S-CC-SET), aunque su aislamiento no detecta escrituras por la shell.

**Riesgos**
- Conflictos semánticos que git no detecta.
- Mitigación: checks de contrato y tests de integración en el merge queue.
- Riesgo adicional: entornos por worktree (puertos, `.env`, dependencias).

**Validación**
- Escenario de Fase 8: 3 agentes y 1 persona en paralelo, midiendo conflictos y retrabajo.
