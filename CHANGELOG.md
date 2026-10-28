# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Hay dos líneas de versión: **standard** (A) y **cli** (B).

## [Sin publicar] — Fase 5

### Añadido (F5.3, 2026-10-28) — estándar 0.7.0, CLI 0.7.0rc1
- `harness platform check [--repo] [--branch]` (`platform.py`, D-062): compara el ruleset de la rama por defecto y los environments (puerta de riesgo alto, despliegue) con lo que exige el nivel. Solo lee; sin token en repos públicos. Reglas `platform.*` y requisito **HS-CI-006**.
- Workflow reutilizable `harness-platform.yml` (programado y en push a `main`; abre o comenta una issue si falla) y plantilla N1.
- Reglas de seguridad de workflows en `harness check` (`rules/ci.py`, D-063): **HS-CI-007** (DEBE: `ci.no-pr-target`, `ci.no-untrusted-interpolation`, `ci.permissions`, `ci.model-readonly`) y **HS-CI-008** (DEBERÍA: `ci.pinned`, `ci.merge-group`).
- `standard/plataforma/`: rulesets de referencia N1 y N2, ruleset de tags `cli-v*` del estándar y guía del environment de la puerta.
- Manifiesto: `plataforma.checks_requeridos`, `plataforma.entorno_puerta`, `plataforma.entorno_despliegue`.

### Añadido (F5.1–F5.2, 2026-10-26) — estándar 0.6.0, CLI 0.6.0rc1
- `docs/fase-5/`: plan (D-053), verificación de fuentes de GitHub y Claude Code y modelo de amenazas (D-057), riesgo, escalado y autorización (D-058…D-060).
- ADR-010 rev. 2 aprobado: revisión de agentes informativa, autorización por ruleset y puerta explícita de riesgo alto (environment con revisores).
- `harness pr risk --base <ref> [--format json] [--github-output]` (`risk.py`): clase mínima calculada a partir del diff y de las tareas que el PR cierra.
- Regla `pr.risk-min` y requisito **HS-CI-005** (DEBE, N1, desde 0.6.0). Con 0.6.0 sustituye al aviso `pr.risk-sensitive`.
- `roles.yaml`: `rutas_criticas` y `patrones_pruebas`; manifiesto: `riesgo.rutas_criticas` (solo amplía).
- Workflow `harness-tasks-lifecycle`: paso «Clase de riesgo calculada» y job `puerta-riesgo-alto` en el environment `aprobacion-riesgo-alto` (input `gate-environment`).
- Ficha `ci.workflows` (aplazada desde F2).
- Plantilla: `allow` para `harness pr risk *`; `AGENTS.md` con los disparadores de parada (D-059).

## [Sin publicar] — Fase 3 (cerrada, D-040) y F3.7

### Cambiado (F3.8, 2026-10-26) — CLI 0.5.1rc1, estándar 0.5.0 sin cambios de requisitos
Ajustes por la validación de la F3.7 en el laboratorio (D-047…D-052):
- `cerrar-tarea` 0.3.0: cuerpo del PR desde la plantilla **antes** de abrirlo y `gh pr create --body-file`; nunca `gh pr edit` (D-049); sección «Cómo ejecutar comandos» (un comando por llamada, sin `; echo $?`, `| tail` ni `&&`, D-048); commit vacío si la rama no tiene commits (D-050). 4 pruebas nuevas.
- `verificador` 0.3.0: las mismas reglas de comandos; no repite `test` ni criterios iguales a `check`; sin `command -v` ni `date` (D-048).
- `verificar-al-terminar` 0.3.1: avisa con `systemMessage` (JSON en stdout, exit 0) al suspenderse o agotar los reintentos, porque Claude Code no muestra el stderr de un hook que termina con 0 (D-051). 3 pruebas nuevas.
- Plantilla `settings.json` (D-052): `allow` para `git add`, `git commit`, `gh pr view|create|ready`; `ask` para `git add -f/--force`, `git commit -n/--no-verify` y `gh pr edit`. HS-SEC-012 comprueba esas formas y un caso nuevo lo cubre.
- Guía: la tarea se cierra en el PR que la completa; una validación posterior es otra tarea (ficha `plans.dir` y plantilla de tarea, D-050).
- Workflows reutilizables a `cli-v0.5.1-rc.1`. `tests/test_distribucion.py` sin versiones fijas.

### Añadido (F3.7, 2026-10-23) — estándar 0.5.0 (sin publicar)
- Requisitos aprobados `desde: 0.5.0` (D-041…D-043), con sus reglas:
  - HS-SEC-010 (DEBE) `adapter.claude.settings-automode`: `disableAutoMode: "disable"`;
  - HS-SEC-011 (DEBERÍA) `adapter.claude.settings-gh`: `ask` para `gh api` y `deny` para `gh repo delete|secret|ruleset|auth`;
  - HS-SEC-012 (DEBERÍA) `adapter.claude.settings-allow-broad`: `allow` sin intérpretes, red, borrado ni ejecución del contrato.
- `harness tasks close T-NNNN --pr N [--resultado] [--verified-by] [--autor]` (D-044): transición determinista a `done`, idempotente, sin efectos si falla una precondición (código 2). 7 pruebas.
- `cli.build_parser()` y un test que congela las opciones de los subcomandos permitidos en la base.
- Fixture `n1-endurecido` (0.5.0, generado con `harness components add`) y 6 casos, entre ellos uno que confirma que 0.4.0 no exige lo de 0.5.0 (D-029).

### Cambiado (F3.7)
- Plantilla `settings.json`: `disableAutoMode`, reglas `gh`, `ask` para `--run-commands`, `--run-acceptance` y `--json-out`, y `allow` para comandos del contrato sin efectos (adaptador §3.4).
- `verificar-al-terminar` 0.3.0 (D-045): límite por defecto 2, suspensión con `HARNESS_STOP_MAX=0` (no bloquea, informa) y valor inválido → defecto. 10 pruebas.
- `verificador` 0.2.0 (D-046): informe entre `<!-- verificador:inicio -->` y `<!-- verificador:fin -->`, y solo ese bloque como respuesta.
- `cerrar-tarea` 0.2.0 (D-044, D-046): usa `harness tasks close`, evidencia literal, sin confirmación propia antes del push, `gh` opcional y sin recurrir a `gh api`.
- Estándar 0.5.0 y CLI 0.5.0rc1 (soporta 0.1.x–0.5.x); los workflows reutilizables apuntan a `cli-v0.5.0-rc.1`.
- `tests/test_distribucion.py` ya no depende de las versiones concretas del catálogo.


### Añadido (F3.5, 2026-10-22) — estándar 0.4.0 (sin publicar)
- ADR-017 (propuesto): distribución de componentes por copia versionada con lockfile, frente a plugins de Claude Code.
- `harness components add|sync|remove|list` (`distribucion.py`): dependencias, fusión aditiva de `settings.json`, no sobrescribe archivos no gestionados ni modificados, y hash con los finales de línea normalizados.
- `.harness/components.lock` y requisito HS-CMP-009 (deriva, propuesto) con la regla `core.components.drift`.
- El catálogo viaja en el paquete de la CLI (`force-include`). El esquema `catalog-entry` admite `configuracion.claude_settings`.
- `verificar-al-terminar` 0.2.0 declara su bloque `Stop` como fragmento de configuración.
- Fixture `n1-distribucion`, generado con la propia CLI; 6 casos, entre ellos CRLF no es deriva; `tests/test_distribucion.py` (13 pruebas).

### Cambiado (F3.5)
- Estándar 0.4.0 y CLI 0.4.0rc1 (soporta 0.1.x–0.4.x); los workflows reutilizables apuntan a `cli-v0.4.0-rc.1`.

### Añadido (F3.4, 2026-10-22)
- Primeros componentes del catálogo (`experimental`, versión 0.1.0), con entrada, ficha de 17 puntos y pruebas:
  - `hook/verificar-al-terminar`: hook Stop que ejecuta `check` y `harness tasks validate` y devuelve exit 2 si fallan. Límite de 3 bloqueos por sesión, falla en abierto, solo biblioteca estándar. 7 pruebas.
  - `subagente/verificador`: verificación independiente de solo lectura con informe de formato fijo. 3 pruebas.
  - `skill/cerrar-tarea`: procedimiento de ADR-016, perfil portable. 7 pruebas, entre ellas una que comprueba que cada comando `harness` citado (opciones incluidas) lo acepta la CLI real.
- `harness catalog index [--write|--check]` y paso de CI que comprueba el índice de `catalog/README.md`.
- pytest recoge también `catalog/` (`testpaths`). Candidato K-14.

### Añadido (F3.3, 2026-10-22) — estándar 0.3.0 (sin publicar)
- 16 requisitos propuestos (`desde: 0.3.0`): 12 de instancia (HS-CMP-001…008, HS-SEC-007…009, HS-CI-004) y 4 del catálogo central (HS-CMP-010…013).
- `harness_cli/skills.py`: validador propio de Agent Skills con perfiles (`metadata.harness-perfil`, ADR-012).
- Reglas `rules/components.py`: skills, subagentes, hooks (scripts y no deterministas), versión mínima, `settings.json` (secretos, rutas sensibles por muestras, modos) y `claude -p` en CI.
- `harness catalog validate [--base]` (`catalog.py`): entrada, ficha de 17 puntos, skill y, con base, transiciones de estado y subida de versión. Paso nuevo en la CI central (`fetch-depth: 0`).
- Fixture conforme `n1-componentes` (0.3.0), 15 casos nuevos y `tests/test_catalog.py` (15 pruebas). La matriz cuenta como cobertura las pruebas de `test_catalog.py` para el contexto `catalog`.

### Cambiado (F3.3)
- Estándar 0.3.0 y CLI 0.3.0rc1 (soporta 0.1.x–0.3.x); los workflows reutilizables apuntan a `cli-v0.3.0-rc.1`. La plantilla declara 0.3.0.

### Añadido (F3.2, 2026-10-22)
- `standard/adaptadores/claude-code.md`: versión mínima, mapeo del núcleo a archivos, política deny-first (qué aplica sin confianza y qué no), límites de las reglas deny, anclaje de rutas y ejecución del agente en CI (`--bare --setting-sources user`, R-14).
- Ficha `standard/04-archivos/adapter.claude.settings.md` (aplazada de F2).
- Plantilla `template/adapters/claude-code/.claude/settings.json` con deny de secretos, `ask` para cada patrón sensible, `disableBypassPermissionsMode` y sin aprobación automática de MCP. El autotest comprueba la cobertura de `patrones_sensibles`.
- Candidatos K-09…K-13. F3.4 sustituye el hook `rutas-sensibles` por `verificar-al-terminar`.

### Añadido (F3.1, 2026-10-22)
- `standard/05-componentes/00-modelo.md`: qué es un componente, sus 6 tipos (skill, subagente, hook, mcp, workflow, plugin), contrato común, seguridad, ciclo de vida y estructura del catálogo.
- `schemas/catalog-entry.schema.json` con reglas cruzadas: solo los hooks deterministas y los workflows pueden ser control; los hooks `prompt` y `agent` nunca; `estable` exige evidencia; los componentes con red o secretos exigen revisión de seguridad; perfil obligatorio en skills (ADR-012). `tests/test_catalog_schema.py` (28 casos).
- Plantilla de ficha de 17 puntos (`standard/05-componentes/_PLANTILLA-FICHA.md`) y `catalog/README.md`.
- ADR-012 rev. 2 (aprobado, D-034); verificación de fuentes de la F3; plan de la F3 (D-033); candidatos K-01…K-08; R-14.

## Fase 2 (cerrada, D-031)

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

### Añadido (cierre F2, 2026-10-22)
- `docs/fase-2/INFORME.md` (cierre de la Fase 2), `docs/fase-2/GUIA-F2.6.md` y evidencias E-010…E-013.
- `examples/greenfield` sincronizado con `harness-example-greenfield` tras el PR #7 (T-0001 y T-0002 en `done`).
- Registro de medición de X-01.

### Cambiado (F2.6, 2026-10-21)
- Los 27 requisitos de 0.2.0 pasan a `aprobado` (D-030) y se aprueba la aplicabilidad por versión (D-029).
- `examples/greenfield` sube a N1 del estándar 0.2.0 (copia de referencia de `harness-example-greenfield` tras el PR de adopción). Sin el secreto `HARNESS_STANDARD_TOKEN` (repos públicos, D-018).
- Ficha `plans.dir`: `.gitkeep` explícito en `active/` y `completed/` (E-009).

### Añadido (F2.5, 2026-10-21) — estándar 0.2.0 (sin publicar)
- 27 requisitos nuevos en `standard/requirements.yaml` (estado `propuesto`, `desde: 0.2.0`): 8 que se añaden a N0 y 19 de N1. `niveles_definidos: [N0, N1]` y `niveles_desde: {N0: 0.1.0, N1: 0.2.0}`.
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
