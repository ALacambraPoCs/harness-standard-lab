---
id: ADR-005
titulo: "Estado de tareas: un archivo por tarea en lugar de una lista compartida"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-005 · Estado de tareas: un archivo por tarea en lugar de una lista compartida [APROBADO 2026-10-19]

**Recomendación**
- Sustituir el `feature_list.json` y el archivo de progreso globales por **un archivo por tarea o plan**: Markdown con frontmatter validado por esquema.
- Campos del frontmatter: id, título, propietario, segmento(s), estado, dependencias, clase de riesgo, criterios de aceptación ejecutables y evidencia (enlace a run de CI o commit).
- Los archivos viven en `docs/plans/active|completed/`, o en `.harness/tasks/` si se separa estado y plan (detalle en Fase 2).
- El índice se **genera**; no se edita a mano.
- Las transiciones a `done` solo las hace la CI o la CLI cuando la verificación pasa.

**Justificación**
- Un archivo compartido es un punto de conflicto garantizado cuando varias personas y agentes trabajan en paralelo (laguna 1 de F0-01).
- S-OAI-HE p.6 ya ubica el progreso y las decisiones dentro de cada plan de ejecución.
- Resuelve las contradicciones C1 y C2.
- Mantiene el principio P4: el agente no se certifica a sí mismo.

**Alternativas**
- (a) Lista JSON única con un esquema unificado: sirve para el nivel N1 en un repositorio pequeño, pero no escala a N2.
- (b) Estado fuera del repositorio (issues de GitHub): contradice P1, aunque **puede complementar** el archivo mediante enlaces. Decisión de detalle en la Fase 4.

**Riesgos**
- Más archivos.
- Hace falta un esquema de estados claro, que incluya `regressed`, porque el curso no lo contempla (contradicción C9 del informe de lecciones).

**Evidencia**
- S-OAI-HE p.6.
- S-LHE L07 y L08 (pass-gate).
- S-VILA p.23: una lista compartida coordinada mediante locks.

**Validación**
- Simulación con 3 o más tareas concurrentes en worktrees: no se producen conflictos de merge en los archivos de estado.
