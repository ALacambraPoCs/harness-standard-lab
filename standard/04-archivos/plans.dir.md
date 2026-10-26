---
rol: plans.dir
roles_adicionales: [plans.active, plans.completed, plans.index]
titulo: Tareas y planes de ejecución (docs/plans/)
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas, cli, ci]
dependencias: [manifest, pr.template, instructions.root]
propietario: Propietario de cada tarea (campo owner); la estructura y el workflow, propietario de plataforma/harness (CODEOWNERS)
requisitos: [HS-STA-001, HS-STA-002, HS-STA-003, HS-STA-004, HS-STA-005, HS-STA-006, HS-CI-002, HS-CI-003, HS-SEC-006]
reglas: [tasks.schema, tasks.naming, tasks.unique, tasks.location, tasks.body, tasks.acceptance, tasks.depends, tasks.transition, tasks.done-pr, tasks.deleted, pr.anchors, pr.risk, pr.sensitive, pr.trivial, pr.task, pr.issue]
ejemplo_canonico: template/niveles/n1/docs/plans/_plantilla-tarea.md
fuentes: [ADR-005, ADR-016, D-023, X-01, S-OAI-HE, S-LHE]
evolucion: >-
  MAJOR si cambia un estado, una transición permitida o un campo obligatorio del esquema de tarea;
  MINOR si se añade un campo o un ancla opcional; PATCH si es editorial.
---

# Tareas y planes de ejecución (docs/plans/)

> Rutas, obligatoriedad y nivel: `standard/roles.yaml#plans.dir`, `#plans.active`, `#plans.completed` y `#plans.index`. Esquema: `schemas/task.schema.json`.

## Propósito

Ser la **fuente de verdad versionada del trabajo**: qué se hace, por qué, con qué criterios de aceptación, quién responde y en qué estado está. Una persona o un agente sin contexto previo debe poder **retomar** una tarea solo con su archivo y el repositorio (continuidad entre sesiones, ADR-005).

El estado `done` no lo declara quien hace el trabajo: lo **verifica la CI**, que vuelve a ejecutar los criterios de aceptación en el PR que completa la tarea (ADR-016).

## Contenido requerido

**Estructura**

| Ruta | Contenido |
|---|---|
| `docs/plans/active/` | Un archivo por tarea no terminal: `T-NNNN-<slug>.md` |
| `docs/plans/completed/` | Tareas `done` o `cancelled`, con el mismo nombre |
| `docs/plans/INDEX.md` | Generado por `harness tasks index`; no se edita |

**Frontmatter de cada tarea** (`schemas/task.schema.json`)

| Campo | Obligatorio | Regla |
|---|---|---|
| `id` | Sí | `T-NNNN`, único, igual al prefijo del nombre de archivo (`tasks.naming`, `tasks.unique`) |
| `title`, `owner` (`@persona`), `risk` (bajo/medio/alto), `created` | Sí | `tasks.schema`. Un agente trabaja siempre a nombre de un `owner` humano |
| `status` | Sí | proposed · ready · in_progress · blocked · in_review · done · regressed · cancelled. Solo transiciones permitidas (`tasks.transition`) |
| `acceptance[]` | Sí, ≥ 1 | `{id: ACn, description, check}`. `check` es un comando que termina en 0, o `manual` con `verified_by` |
| `done_pr` | Si `done` | Número del PR que la completa; debe coincidir con el PR en curso (`tasks.done-pr`) |
| `blocked_reason` | Si `blocked` | Texto |
| `segments`, `depends_on`, `issue`, `lease` | No | `depends_on` debe apuntar a tareas existentes (`tasks.depends`) |

**Cuerpo** (anclas, `tasks.body`): `objetivo`, `alcance`, `plan`, `progreso`, `decisiones`; y `resultado` con contenido si la tarea está `done`.

**Transiciones permitidas** (`tasks.transition`)

```
(nueva) → proposed | ready | in_progress
proposed → ready | cancelled          ready → in_progress | cancelled
in_progress → blocked | in_review | done | cancelled
blocked → in_progress | cancelled     in_review → in_progress | done
done → regressed                      regressed → in_progress
cancelled → (terminal)
```

Una tarea no se borra (`tasks.deleted`): se cancela y se conserva su historia.

## Contenido recomendado y opcional

- Ancla `hallazgos` con comportamientos inesperados y su evidencia.
- `lease` para reservar la tarea ante trabajo concurrente; su verificación llega con la Fase 4 (concurrencia).
- `issue` para el espejo en GitHub Issues del experimento X-01.
- **Cerrar la tarea en el PR que la completa** (ADR-016). Si el plan necesita una validación posterior (p. ej. una sesión en el laboratorio), esa validación es **otra tarea** con sus propios criterios, no un paso pendiente de la misma. Una tarea que solo queda por cerrar obliga a abrir un PR sin cambios (H-14, D-050).

## Contenido excluido

| No incluir | Va en |
|---|---|
| Decisiones arquitectónicas duraderas | `decisions.dir` (ADR). La tarea enlaza al ADR |
| Conocimiento estable del sistema | `architecture.map`, `instructions.root` o `instructions.segment` |
| Secretos, datos personales, salidas completas de logs | En ningún sitio; enlace a la ejecución de CI |
| Estado copiado de un sistema externo (issue, ticket) como fuente | La tarea es la fuente; la issue es espejo (X-01) |
| Ediciones manuales de `INDEX.md` | Se regenera con `harness tasks index` |

## Formato y convenciones

- Markdown con frontmatter YAML. Nombre `T-NNNN-<slug>.md`, slug en minúsculas con guiones.
- `active/` y `completed/` llevan un `.gitkeep`: Git no versiona directorios vacíos y, sin él, la estructura desaparece cuando la última tarea cambia de carpeta (E-009).
- El PR que completa la tarea **incluye la transición** a `done`: mueve el archivo a `completed/`, pone `status: done` y `done_pr`, y rellena `resultado` (ADR-016).
- Los criterios ejecutables se ejecutan en CI desde la raíz del repositorio, sin secretos y con el límite `tasks.acceptance_timeout` del manifiesto.
- **Tarea trivial** (D-023): un PR puede declarar `trivial — <motivo>` en lugar de una tarea si **todas** sus rutas coinciden con `patrones_triviales` (o `tasks.trivial_paths` del manifiesto) y ninguna con `patrones_sensibles`. Los reverts están exentos.
- El cuerpo del PR (`pr.template`) referencia la tarea; si la tarea tiene `issue` y pasa a `done`, el PR incluye `Closes #<issue>`.

## Ejemplo canónico

Ver `template/niveles/n1/docs/plans/_plantilla-tarea.md`. Las pruebas `tests/test_tasks.py` contienen ejemplos válidos e inválidos de cada regla.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Esquema, nombre, ubicación, anclas y dependencias (`harness check` y `harness tasks validate`) | L4 | HS-STA-001…003, HS-STA-006 |
| Transiciones frente a la base del PR y re-ejecución de la aceptación (`--base --run-acceptance`) | L4 | Implementada (F2.4) |
| Criterios `manual` verificados por un aprobador del PR | L4 + L5 | Implementada (F2.4) |
| Cuerpo del PR coherente con el diff (`harness pr check`) | L4 | Implementada (F2.4) |
| Índice al día (`harness tasks index --check`) | L4 | Implementada (F2.4) |
| Fusión bloqueada si falla el check | L5 | Requiere configurar `harness tasks` como check requerido en el ruleset |
| Espejo en issues (`harness tasks issue-sync`) | — | Experimento X-01; informativo |

## Criterios de aceptación

1. Todas las tareas validan sin errores con `harness tasks validate`.
2. Ninguna tarea llega a `done` en la rama por defecto sin un PR cuyo check `harness tasks` haya re-ejecutado sus criterios con éxito.
3. `INDEX.md` coincide con la salida de `harness tasks index`.
4. Ningún PR no trivial se fusiona sin referenciar una tarea existente.

## Ciclo de vida y evolución

- **Creación:** al adoptar N1; `harness init` (Fase 3) copiará `template/niveles/n1/`.
- **Actualización:** cada sesión de trabajo actualiza `progreso` y, si procede, `decisiones`.
- **Archivo:** las tareas terminadas permanecen en `completed/`. Una política de compactación (resúmenes, archivo por año) se evaluará con datos de uso en la Fase 6.
- **Retirada:** si X-01 concluye que un gestor externo debe ser la fuente de verdad, se requiere un ADR que sustituya a ADR-005.
