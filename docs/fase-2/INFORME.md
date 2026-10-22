---
documento: F2-INFORME
titulo: Informe de cierre de la Fase 2 — Estructura canónica, fichas de archivo y nivel N1
estado: propuesto para cierre
fecha: 2026-10-22
---

# Fase 2 · Informe de cierre

## 1. Qué se ha entregado

| Incremento | Entregable | Aprobación |
|---|---|---|
| F2.1 | Estructura canónica (`03-estructura-canonica.md`), roles N1, plantilla y esquema de ficha | D-024 |
| F2.2 | Fichas de AGENTS.md raíz, de segmento y CLAUDE.md; anclas `harness:*` | D-025 |
| F2.3 | Fichas de manifiesto y comandos, arquitectura, ADR, seguridad, referencias, CODEOWNERS y plantilla de PR | D-026 |
| F2.4 | Esquema de tarea y ciclo de vida; `harness tasks` y `harness pr check`; workflow `harness-tasks-lifecycle.yml`; ADR-016 | D-027, D-028 |
| F2.5 | Estándar 0.2.0: 27 requisitos (8 añadidos a N0 y 19 de N1); aplicabilidad por versión | D-029, D-030 |
| F2.6 | Prueba de extremo a extremo de N1 en `harness-example-greenfield` | Este informe |

Estado del producto:
- **Estándar (A):** 0.2.0 (sin publicar), 50 requisitos y niveles N0 y N1.
- **CLI (B):** 0.2.0rc2 (`cli-v0.2.0-rc.2`), 106 autotests, matriz sin huecos y plantilla validada en N0 y en N1.
- **Instancia de ejemplo (C):** en N1.

## 2. Evidencias de la F2.6

Todas están en `ALacambraPoCs/harness-example-greenfield`, con capturas del usuario del 2026-10-22.

| ID | Evidencia | Qué demuestra |
|---|---|---|
| E-010 | PR #5 (adopción de N1): `harness check` y `harness tasks` en verde y **requeridos** en el ruleset antes del merge | N1 se adopta mediante PR y bajo control L5. La lección de E-005 está aplicada |
| E-011 | PR #7, primer commit (`d60fd2d`): T-0002 declarada `done` sin implementar. `tasks / harness tasks` **en rojo** (AC1 y AC2 con código 1) y merge bloqueado, mientras la conformidad sigue en verde | **ADR-016:** el agente no puede declarar terminado. La CI vuelve a ejecutar los criterios y el ruleset impide el merge |
| E-012 | PR #7, segundo commit (`2abc558`): implementación. Ambos checks en verde y merge (`e9946bd`) | La misma verificación da paso al trabajo realmente terminado |
| E-013 | Issue #4: `status:ready` (tras el PR #5) → `status:in_progress` (tras el #6) → cerrada por `Closes #4` → `status:done` y comentario con el enlace a la ejecución 39779093407, siempre por `github-actions` | **X-01:** espejo de un solo sentido sin edición manual y evidencia trazable desde la issue |

Además, T-0001 pasó a `done` en el PR #6 tras volver a ejecutar `harness check --strict` y `harness tasks index --check` como criterios de aceptación.

## 3. Criterios de aceptación de la fase (`PLAN.md`)

| # | Criterio | Estado |
|---|---|---|
| 1 | Cada archivo obligatorio u opcional de N0 y N1 tiene ficha completa | **Parcial.** De los 20 roles de N0 y N1, 15 tienen ficha. Quedan 5 aplazados a la fase dueña de su subsistema: `ci.workflows` (N0, obligatorio) → F5; `adapter.claude.settings` → F3; `project.rules` → F4; `runbooks.dir` → F5; `quality.doc` → F6. Ver la decisión del §6 |
| 2 | `task.schema.json` valida conformes y rechaza no conformes (transiciones ilegales, `done` sin evidencia) | ✅ `tests/test_tasks.py` y fixtures `nc-tarea-*` |
| 3 | `harness matrix --strict` pasa con N0 y N1 | ✅ |
| 4 | La plantilla instanciada a N1 supera su validador | ✅ `tests/test_template.py[N1]` |
| 5 | Evidencia en GitHub de una tarea que pasa a `done` solo por la CI | ✅ E-011 y E-012 |

## 4. Hallazgos

- **E-009** (simulación previa al laboratorio): un `active/` vacío desaparece en Git. Mitigación: `.gitkeep`. En el laboratorio, después del PR #7 `active/` está vacío y la instancia sigue conforme.
- **Matriz versionada** (F2.5): la CI compara `docs/MATRIZ.md`, y yo regeneré la copia temporal de la raíz. Se añade a la lista de comprobación previa a cada entrega: regenerar `docs/MATRIZ.md` y ejecutar el mismo `diff` que la CI.
- **Orden de configuración:** el check requerido se añadió al ruleset **antes** del merge del PR #5. Con el check nuevo, GitHub solo lo ofrece en el ruleset cuando ya ha aparecido al menos una vez en un PR. La guía de adopción de N1 debe incluir este paso (F7, `harness init`).
- **La numeración de issues y PR es compartida** y hay que predecirla para `done_pr` e `issue`. En la práctica, el agente rellena `done_pr` después de abrir el PR. Es una fricción menor, pero se medirá en X-01.

## 5. Limitaciones conocidas

- **R-10 (un solo mantenedor):** no se han ejercitado los criterios `manual` con `verified_by` ni la revisión de code owner. Sus pruebas existen en `test_tasks.py`, pero no hay evidencia real.
- **HS-CI-003** es semiautomático: la CLI no lee el ruleset, porque la API de rulesets se aborda en F5.
- **X-01** acaba de empezar: 1 tarea con issue, 3 sincronizaciones y 0 desincronizaciones. El criterio de decisión exige ≥ 4 semanas o ≥ 20 tareas.
- **HS-CTX-003** (32 KiB de Codex): la fuente oficial no se ha leído a mano (R-08).
- El ejemplo es pequeño (greenfield). El comportamiento en brownfield grande se probará en F4 y F8.

## 6. Decisiones que se piden

**1. Cerrar la Fase 2 con el criterio 1 parcial.**
- **Recomendación:** aprobar el cierre y aplazar las 5 fichas a las fases que diseñan esos subsistemas.
- **Justificación:** el contenido de esas fichas depende de decisiones que aún no se han tomado: `settings.json` deny-first (F3), `segments.yaml` (F4), la estrategia de CI/CD y despliegue (F5) y las métricas (F6). Escribirlas ahora sería inventar normativa que luego habría que rehacer. `ci.workflows` ya tiene sus requisitos mínimos vigentes (HS-GOV-004 y HS-CI-003); lo que falta es su ficha completa.
- **Alternativa:** escribir ahora la ficha de `ci.workflows` con lo que ya se sabe. Coste bajo, pero se reescribiría en F5.
- **Validación:** `roles.yaml` mantiene `ficha: pendiente:F3/F4/F5/F6`, y la CLI y la matriz lo hacen visible.

**2. Siguiente fase.**
- **Recomendación:** **F3 · Componentes, catálogo y adaptador de Claude Code**, como prevé `04-metodo-y-plan.md`:
  - contratos por tipo de componente;
  - esquema `catalog-entry` y su ciclo de vida;
  - `settings.json` deny-first;
  - ADR-012 (skills) pendiente de aprobación;
  - 2–3 componentes semilla (subagente verificador, hook de rutas sensibles, skill de cierre de tarea).
- **Alternativa:** F4 (segmentación y concurrencia). Es más urgente si el piloto brownfield está cerca, pero su prueba necesita un repositorio grande, que todavía no está designado (Q-09).
