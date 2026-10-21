# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Hay dos líneas de versión: **standard** (A) y **cli** (B).

## [Sin publicar] — Fase 2 (en curso)

### Añadido (F2.1, 2026-10-21)
- `standard/03-estructura-canonica.md`: árbol N0–N1, regla de ubicación del conocimiento, convenciones de nombres y rutas, archivos generados, instrucciones de segmento, brownfield.
- `standard/roles.yaml`: nuevos roles `instructions.segment`, `adapter.claude.local`, `quality.doc`, `runbooks.dir`, `references.dir`, `plans.active`, `plans.completed`, `plans.index`, `project.rules`, `pr.template`; campos `obligatoriedad`, `condicion`, `ficha`, `patron`, `relativa_a`.
- `schemas/ficha.schema.json` y `standard/04-archivos/_PLANTILLA.md` (plantilla de ficha de archivo).
- CLI: `harness roles [--write [--check]]` genera la tabla de roles; `role_path` resuelve roles relativos (`relativa_a`).
- Tests: integridad de fichas frente a `roles.yaml` y tabla de roles al día; paso de CI equivalente.
- Decisiones D-020…D-023 y experimento X-01 (`docs/experimentos/`).

### Añadido (F2.2, 2026-10-21)
- Fichas `standard/04-archivos/instructions.root.md`, `instructions.segment.md` y `adapter.claude.instructions.md` (incluye `CLAUDE.local.md`).
- Anclas de contenido `<!-- harness:… -->` en la plantilla y en el ejemplo greenfield (resumen, comandos, restricciones, mapa; `claude` en CLAUDE.md).
- `examples/fragmentos/` con el ejemplo canónico de segmento (`AGENTS.md` + `CLAUDE.md`).
- `docs/fase-2/CANDIDATOS-N1.md`: requisitos candidatos C-01…C-10 para la F2.5.
- Fuentes S-ETH-AGENTSMD y S-LULLA-AGENTSMD en el inventario.

### Añadido (F2.3, 2026-10-21)
- Fichas `manifest` (incluye el contrato de comandos), `architecture.map`, `decisions.dir`, `security.policy`, `references.dir`, `codeowners` y `pr.template`.
- Plantilla: `docs/decisions/_plantilla.md` (ADR con frontmatter), ADR-0001 con frontmatter, anclas en ARCHITECTURE.md y SECURITY.md (tabla riesgo → control), `.github/pull_request_template.md` con anclas `tarea`, `riesgo`, `evidencia`, `sensible`.
- Ejemplo greenfield con anclas en arquitectura, seguridad y decisiones; fragmento `examples/fragmentos/references-README.md`.
- Candidatos C-11…C-20; fuentes S-MATKLAD-ARCH, S-NYGARD-ADR y S-GH-PRTEMPLATE.

### Añadido (F2.5, 2026-10-21) — estándar 0.2.0 (sin publicar)
- 26 requisitos nuevos en `standard/requirements.yaml` (estado `propuesto`, `desde: 0.2.0`): 7 que se añaden a N0 y 19 de N1. `niveles_definidos: [N0, N1]` y `niveles_desde: {N0: 0.1.0, N1: 0.2.0}`.
- Aplicabilidad por versión (D-029, propuesta): la CLI solo aplica los requisitos con `desde` ≤ versión declarada; N1 exige declarar 0.2.0.
- `schemas/adr.schema.json`; `budgets.instructions_max_constraints` en el manifiesto; `niveles_desde` en el esquema de requisitos.
- Reglas nuevas (`rules/n1.py`, `rules/lifecycle.py`): anclas de AGENTS.md, arquitectura y seguridad; flujo; presupuesto de restricciones; cadena de 32 KiB; segmentos (ámbito, duplicación, CLAUDE.md); `@AGENTS.md` primero; `.claude/CLAUDE.md`; rutas portables; idioma; índice y frontmatter de ADR; procedencia de referencias; plantilla de PR; workflow de tareas; estructura de tareas; la parte estática de `harness tasks validate` y el índice dentro de `harness check`.
- `harness pr check`: aviso si se reescribe un ADR aceptado (`pr.adr-immutable`). La regla de riesgo bajo en rutas sensibles pasa a llamarse `pr.risk-sensitive`.
- Los hallazgos de `harness tasks` y `harness pr check` citan ya su requisito (antes `pendiente:F2.5`).
- Fixture conforme `n1-basico` y 25 casos nuevos; la matriz cuenta como cobertura de las reglas de PR las pruebas de `tests/test_tasks.py`. La plantilla se valida en N0 y en N1 (`{{LEVEL}}`, `{{DOCS_LANGUAGE}}`, `{{DATE}}`; ancla `flujo` en AGENTS.md).
- Fichas: los `pendiente:F2.5` se sustituyen por los IDs; `02-niveles-de-conformidad.md` §3b.

### Cambiado (F2.5)
- CLI 0.2.0rc2 (soporta estándar 0.1.x y 0.2.x). Los workflows reutilizables usan por defecto `cli-v0.2.0-rc.2`.

### Añadido (F2.4, 2026-10-21)
- `schemas/task.schema.json` (esquema de tarea, ADR-005) y ficha `standard/04-archivos/plans.dir.md` (cubre `plans.active`, `plans.completed` y `plans.index`).
- ADR-016 (aprobado, D-027): la transición a `done` va en el propio PR y la verifica un check requerido que re-ejecuta los criterios de aceptación.
- `roles.yaml`: `patrones_sensibles` y `patrones_triviales` (D-023, ADR-013); manifiesto: `tasks.trivial_paths` y `tasks.acceptance_timeout`.
- CLI: `harness tasks validate [--base --run-acceptance --pr-number --approvers]`, `harness tasks index [--write|--check]`, `harness tasks issue-sync [--dry-run]` (X-01) y `harness pr check`.
- Workflow reutilizable `.github/workflows/harness-tasks-lifecycle.yml` (jobs `verify` y `sync-issues`) y plantilla `template/niveles/n1/` (plantilla de tarea, índice y workflow que lo llama).
- `tests/test_tasks.py` (29 casos sobre repos git temporales). Candidatos C-21…C-26.

### Cambiado (F2.4)
- CLI 0.2.0rc1. El workflow de tareas usa por defecto `cli-ref: cli-v0.2.0-rc.1`, tag que hay que crear tras fusionar F2.4. `harness-conformance.yml` sigue en `cli-v0.1.1`.

### Corregido (F2.2)
- `03-estructura-canonica.md` §7 afirmaba que Claude Code carga `<segmento>/AGENTS.md` bajo demanda: con un `CLAUDE.md` raíz no lo hace (S-CC-MEM, verificado 2026-10-21). Ahora se exige `<segmento>/CLAUDE.md` con `@AGENTS.md`.

### Corregido
- Con la CLI instalada por `pip`, `harness matrix` buscaba los fixtures en la copia empaquetada del estándar (sin `tests/`) y fallaba en la CI. Lo detectó y corrigió el usuario con `--fixtures tests/fixtures`. Se generaliza a `harness --standard-root . …` en la CI central (también para `roles`). `matrix` y `roles` muestran un error explicativo si no encuentran sus archivos. No se busca el estándar en el directorio actual a propósito: una instancia podría aportar un `standard/` propio para relajar las reglas.

## [cli 0.1.1] — 2026-10-20

### Cambiado
- Acciones de GitHub fijadas por SHA a versiones con runtime Node 24: `actions/checkout` v7.0.1, `actions/setup-python` v7.0.0 y `actions/upload-artifact` v7.0.2. Elimina el aviso de deprecación de Node 20 que apareció en la primera ejecución de la CI.
- Runner fijado a `ubuntu-24.04`, porque `ubuntu-latest` migra a Ubuntu 26 desde el 2026-10-19.
- El workflow reutilizable usa por defecto `cli-ref: cli-v0.1.1`.

### Añadido
- La CI del repositorio central rechaza rutas no portables a Windows (`:`, `<>"|?*\`, espacio o punto final). Así se detecta el incidente de los metadatos ADS del 2026-10-20.

## [standard 0.1.0] [cli 0.1.0] — 2026-10-20 — Fase 1

### Cambiado (2026-10-20)
- Los 23 requisitos N0 pasan a estado `aprobado` (D-015).
- El workflow reutilizable recibe `standard-repository` explícito; plantilla y fixtures lo pasan.
- Ejemplo `examples/greenfield` (instancia real del laboratorio) y comprobación en la CI central.
- `.github/CODEOWNERS` del repositorio central.
- Runbook de publicación `docs/fase-1/PUBLICACION.md`.

### Primera entrega (2026-10-19)

### Añadido
- Estructura del repositorio central (ADR-001).
- `standard/00-alcance-terminologia.md`, `01-modelo-conceptual.md` y `02-niveles-de-conformidad.md`.
- `standard/requirements.yaml` con los requisitos del nivel N0.
- `standard/roles.yaml` con los roles de archivo (ADR-004).
- Esquemas `manifest`, `requirement` y `roles` (JSON Schema 2020-12).
- CLI `harness` en Python con los comandos `check`, `matrix` y `explain`, las reglas del nivel N0, la salida en texto y en JSON, y la gestión de waivers.
- Fixtures conformes y no conformes, y autotests con pytest.
- Workflows `ci.yml` (CI de este repositorio) y `harness-conformance.yml` (reutilizable, `workflow_call`).
- ADR-001 a ADR-015 como archivos individuales en `adr/`.

### Corregido respecto a F0-02
- Los workflows reutilizables se ubican en `.github/workflows/` y no en `ci/`, porque GitHub solo permite llamar a workflows reutilizables desde esa ruta.
