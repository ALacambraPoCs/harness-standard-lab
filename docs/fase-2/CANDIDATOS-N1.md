---
documento: F2-CANDIDATOS
titulo: Requisitos candidatos que surgen de las fichas (se formalizan en F2.5)
estado: lista viva
actualizado: 2026-10-21 (F2.5: formalizados)
---

# Requisitos candidatos para la F2.5

Cada candidato tiene su origen en una ficha. **En la F2.5 todos se han formalizado** en `standard/requirements.yaml` (estado `propuesto`, `desde: 0.2.0`); la columna «Requisito» da el ID. Se añade HS-STA-001 (estructura de tareas), que no venía de un candidato. La fuente de verdad es `requirements.yaml`.

| # | Requisito | Candidato | Nivel normativo propuesto | Niveles | Verificación | Origen |
|---|---|---|---|---|---|---|
| C-01 | HS-INS-009 | AGENTS.md raíz contiene las anclas `resumen`, `comandos`, `restricciones` y `mapa` | DEBE | N1+ | automática | instructions.root |
| C-02 | HS-CTX-002 | N.º de restricciones duras como máximo el presupuesto (15 por defecto, ajustable en el manifiesto) | DEBERÍA | N1+ | automática | instructions.root |
| C-03 | HS-INS-010 | AGENTS.md raíz contiene el ancla `flujo` (dónde está la tarea, quién marca `done`) | DEBERÍA | N1+ | automática | instructions.root |
| C-04 | HS-CTX-003 | Bytes acumulados de la cadena raíz → segmento más profundo ≤ 32 KiB (límite de Codex) | DEBERÍA | N0+ | automática | instructions.root / segment |
| C-05 | HS-INS-011 | `<segmento>/AGENTS.md` contiene `ambito` y al menos otra ancla con contenido | DEBE | N0+ | automática | instructions.segment |
| C-06 | HS-INS-012 | `<segmento>/AGENTS.md` no duplica líneas sustantivas de la raíz | DEBERÍA | N0+ | automática | instructions.segment |
| C-07 | HS-INS-013 | Con `claude-code`, cada `<segmento>/AGENTS.md` tiene `<segmento>/CLAUDE.md` con `@AGENTS.md` | DEBE | N0+ | automática | instructions.segment / adapter.claude (S-CC-MEM) |
| C-08 | HS-INS-014 | `@AGENTS.md` es la primera línea no vacía de cada CLAUDE.md | DEBERÍA | N0+ | automática | adapter.claude |
| C-09 | HS-INS-015 | No existe `.claude/CLAUDE.md` (una sola ubicación del adaptador) | DEBERÍA | N0+ | automática | adapter.claude |
| C-10 | HS-GOV-008 | Rutas versionadas portables: sin `:<>"\|?*\` y sin segmentos acabados en espacio o punto | DEBE | N0+ | automática | 03 §5, R-11 |
| C-11 | HS-GOV-007 | `project.docs_language` declarado en el manifiesto | DEBERÍA | N1+ | automática | manifest (D-020) |
| C-12 | HS-ARC-003 | Mapa de arquitectura con anclas `vision`, `mapa-codigo`, `limites`, `invariantes` | DEBE | N1+ | automática | architecture.map |
| C-13 | HS-ARC-004 | `decisions.dir/README.md` con ancla `indice`, coherente con los ADR existentes | DEBE | N1+ | automática | decisions.dir |
| C-14 | HS-ARC-005 | Cada ADR `NNNN-*.md` con frontmatter válido (esquema `adr`) e `id` = número de archivo | DEBE | N1+ | automática | decisions.dir |
| C-15 | HS-ARC-006 | Un ADR `aceptada` no cambia su contenido salvo `estado`/`reemplazada_por` | DEBERÍA | N1+ | automática (diff de PR) | decisions.dir |
| C-16 | HS-SEC-005 | Política de seguridad con anclas `secretos`, `entradas-no-confiables`, `aprobaciones`, `controles` | DEBE | N1+ | automática | security.policy |
| C-17 | HS-CTX-004 | `references.dir` (si existe) con índice y cada archivo con `Fuente:` y fecha | DEBERÍA | N0+ | automática | references.dir |
| C-18 | HS-CI-001 | Existe la plantilla de PR con anclas `tarea`, `riesgo`, `evidencia`, `sensible` | DEBE | N1+ | automática | pr.template |
| C-19 | HS-CI-002 | El cuerpo de cada PR declara `tarea` válida (archivo existente o `trivial` coherente con el diff, D-023) y `riesgo` válido | DEBE | N1+ | automática en CI de tareas | pr.template / F2.4 |
| C-20 | HS-SEC-006 | `sensible: no` en un PR que toca rutas sensibles se marca como error | DEBE | N1+ | automática (diff) | pr.template / ADR-013 |
| C-21 | HS-STA-002 | Cada tarea de `plans.active`/`plans.completed` valida con `schemas/task.schema.json`, nombre `T-NNNN-<slug>.md`, id único y anclas de cuerpo | DEBE | N1+ | automática | plans.dir / F2.4 (`tasks.schema`, `naming`, `unique`, `body`) |
| C-22 | HS-STA-003 | Las tareas terminales están en `completed/` y las no terminales en `active/`; ninguna tarea se borra | DEBE | N1+ | automática (diff) | plans.dir (`tasks.location`, `tasks.deleted`) |
| C-23 | HS-STA-004 | Solo transiciones de estado permitidas respecto a la base del PR | DEBE | N1+ | automática (diff) | plans.dir (`tasks.transition`) |
| C-24 | HS-STA-005 | Una tarea pasa a `done` solo si el check del PR re-ejecuta con éxito sus criterios y `done_pr` es ese PR; los `manual` con `verified_by` aprobador | DEBE | N1+ | automática en CI de tareas | ADR-016 (`tasks.acceptance`, `tasks.done-pr`) |
| C-25 | HS-STA-006 | `plans.index` coincide con la salida de `harness tasks index` | DEBERÍA | N1+ | automática | plans.dir |
| C-26 | HS-CI-003 | `harness tasks` configurado como check requerido en el ruleset de la rama por defecto | DEBE | N1+ | semiautomática (API de rulesets) | ADR-016, E-006 |

Nota sobre compatibilidad: añadir un DEBE a N0 es un cambio MAJOR (`GOVERNANCE.md` §3), admitido mientras el estándar sea 0.x. C-05, C-07 y C-10 no rompen ninguna instancia actual: ninguna tiene segmentos y todas las rutas son portables.
