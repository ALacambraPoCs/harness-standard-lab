---
documento: REGISTRO
titulo: Registro vivo — decisiones, cuestiones abiertas, riesgos y próximos pasos
actualizado: 2026-10-24 (F3.7 fusionada y validada en el laboratorio; E-020…E-024)
---

# Registro del proyecto «Estándar de Harness»

## Decisiones aprobadas

| ID | Decisión | Fecha | Aprobada por |
|---|---|---|---|
| D-001 | El entregable principal es un **estándar de estructura de proyecto** con una **plantilla ejecutable** que se pueda validar. No es solo un modelo conceptual. Se distinguen tres productos: A (estándar), B (plantilla) y C (instancia). | 2026-10-19 | Usuario (petición explícita) |
| D-002 | Alcance de la v1: adaptador de agente **Claude Code** y plataforma **GitHub + Actions**. | 2026-10-19 | Usuario |
| D-003 | El estándar y la plantilla viven en un **repositorio central dedicado**. | 2026-10-19 | Usuario |
| D-004 | Perfiles prioritarios: **greenfield** y **brownfield grande**. Monorepo y multi-repo se tratarán más adelante. | 2026-10-19 | Usuario |
| D-005 | **ADR-001 aprobado** sin cambios: productos A/B/C; A y B en un repositorio central con versiones independientes; si A y B discrepan, prevalece A. | 2026-10-19 | Usuario |
| D-006 | **ADR-002 aprobado** sin cambios: palabras clave DEBE/NO DEBE/DEBERÍA/NO DEBERÍA/PUEDE; IDs `HS-<DOMINIO>-NNN`; registro `requirements.yaml` con naturaleza (guidance/enforcement), verificación, conformidad, fuentes, estado y retirada; todo DEBERÍA justifica cuándo es aceptable no cumplirlo. | 2026-10-19 | Usuario |
| D-007 | **ADR-003 aprobado** sin cambios: `AGENTS.md` (raíz y por segmento) es la fuente única; `CLAUDE.md` = `@AGENTS.md` + solo contenido exclusivo de Claude Code; duplicación prohibida y validada por la CLI; imports deben resolverse; `CLAUDE.local.md` permitido sin versionar. | 2026-10-19 | Usuario |
| D-008 | **ADR-004 aprobado** sin cambios: `.harness/manifest.yaml` obligatorio con JSON Schema (standard, project, adapters, commands, roles, segments, waivers); validación por roles con rutas por defecto, desviación solo en roles que lo permiten; validación por esquema/anclas, no por palabras clave; waivers con aprobador y caducidad. | 2026-10-19 | Usuario |
| D-009 | **ADR-005 aprobado** sin cambios: un archivo Markdown+frontmatter (JSON Schema) por tarea/plan en `docs/plans/{active,completed}/` (detalle F2); se eliminan feature_list y progreso globales; índice generado; estados `proposed/ready/in_progress/blocked/in_review/done/regressed/cancelled`; solo CI/CLI marca `done` con evidencia enlazada (run + commit); campo `lease` reservado (ADR-011); `issue:` opcional (Q-04). | 2026-10-19 | Usuario |
| D-010 | **ADR-006 aprobado** sin cambios: roles de comando `setup`, `check`, `test` (obligatorios), `e2e`, `build`, `dev` (condicionales), `clean` (recomendado), declarados en el manifiesto; propiedades: no interactivo, idempotente, exit code significativo, errores orientados a remedio, ejecutable desde cualquier worktree, sin secretos de producción; AGENTS.md/CI/CLI usan exactamente esos comandos. | 2026-10-19 | Usuario |
| D-011 | **ADR-007 aprobado** sin cambios: niveles acumulativos N0 (legible por agentes), N1 (trabajo verificado), N2 (concurrente), N3 (autonomía supervisada); brownfield entra por N0; N2 exige N1; el nivel acota la autonomía (impuesto técnicamente donde se pueda, auditado en el resto); waivers por requisito, con aprobador y caducidad (máx. propuesto 90 días); requisitos marcados como no exentables; bajada de nivel si la conformidad falla de forma sostenida (umbral en F9). | 2026-10-19 | Usuario |
| D-012 | **ADR-009 aprobado** sin cambios: instrucciones solo guían; capas L1 instrucciones, L2 permisos del agente, L3 hooks deterministas, L4 CI (autoridad si check requerido), L5 plataforma (rulesets, CODEOWNERS, merge queue, environments); todo requisito `enforcement` respaldado por L4/L5; hooks `prompt`/`agent` no cuentan como control; presupuesto de contexto medible (inicial <200 líneas/archivo, ajustable); paridad hook local ↔ CI. | 2026-10-19 | Usuario |
| D-013 | **ADR-013 aprobado** sin cambios: CODEOWNERS obligatorio y no exentable sobre AGENTS.md/CLAUDE.md, `.claude/`, `.agents/`, `.mcp.json`, `.harness/`, `.github/workflows/`, `CODEOWNERS`; ruleset con revisión de code owner y aprobación del último push por otra persona; agentes en CI con `claude -p --bare` y config explícita, job del agente `contents: read` separado del job que aplica cambios, secretos por paso / OIDC, `permissions:` explícitos; MCP catalogado y no confiable; revisión de agente solo informativa. | 2026-10-19 | Usuario |
| D-014 | **ADR-008 aprobado parcialmente**: la CLI se implementa en **Python ≥ 3.11** (pyyaml, jsonschema). Distribución por `pip install` desde el repo central y workflow reutilizable. Mecanismo de actualización de instancias (Copier o propio) sigue pendiente (F7). Resuelve Q-03. | 2026-10-19 | Usuario |
| D-015 | **Los 23 requisitos de `standard/requirements.yaml` (v0.1.0, nivel N0) quedan aprobados** sin cambios (estado `aprobado`). | 2026-10-20 | Usuario |
| D-017 | ~~Reemplazada por D-018.~~ Los repositorios del laboratorio son **privados** y la organización `ALacambraPoCs` pasa a **GitHub Team** para disponer de rulesets, checks requeridos y code owners en privado (reproduce el entorno corporativo). | 2026-10-20 | Usuario |
| D-018 | El usuario descarta el plan Team (no quiere pagar). Los repositorios del laboratorio pasan a **públicos** en la org Free `ALacambraPoCs` (central hecho el 2026-10-20; ejemplo pendiente). Con repos públicos: rulesets, checks requeridos, secret scanning y push protection disponibles sin coste; el token de lectura deja de ser necesario. | 2026-10-20 | Usuario |
| E-001 | **Evidencia:** `ALacambraPoCs/harness-standard-lab` publicado; workflow `ci` en verde en Python 3.11/3.12/3.13 (reportado por el usuario, 2026-10-20). Avisos: deprecación de Node 20 en `actions/checkout@v4`/`setup-python@v5` y migración de `ubuntu-latest` a Ubuntu 26 → corregidos en cli 0.1.1. | 2026-10-20 | Usuario (reporte) |
| E-002 | **Evidencia:** cli 0.1.1 publicada; `ci` en verde en los 3 jobs (3.11/3.12/3.13) sin avisos de Node 20 (reportado por el usuario, 2026-10-20). | 2026-10-20 | Usuario (reporte) |
| E-003 | **Evidencia L5:** con `harness-standard-lab` público, el ruleset `main-protegida` rechaza un push directo a `main`: `GH013 … Changes must be made through a pull request` y `3 of 3 required status checks are expected` (salida aportada por el usuario, 2026-10-20). Verifica HS-GOV-004 (parte ruleset) en el repo central. | 2026-10-20 | Usuario (reporte) |
| E-004 | **Evidencia de extremo a extremo (fallo):** en `harness-example-greenfield` (público), el PR `prueba/hs-ins-002` ejecuta el workflow reutilizable `harness-conformance.yml@cli-v0.1.1` del repo central; `harness check` (CLI 0.1.1, estándar 0.1.0) detecta `core.instructions.commands-match` (HS-INS-002) con QUÉ/POR QUÉ/CÓMO y nivel efectivo «ninguno»; 20 reglas ejecutadas (informe aportado por el usuario, 2026-10-20). Cierra la parte «workflow reutilizable sin ejecutar desde una instancia» de R-09. | 2026-10-20 | Usuario (reporte) |
| E-005 | **Evidencia negativa (valida ADR-009):** el PR #1 de `harness-example-greenfield` se fusionó en `main` con el check `conformance / harness check` en rojo, porque aún no existía el ruleset. Un check de CI (L4) que no es *requerido* por la plataforma (L5) solo informa: no impide integrar código no conforme. `main` del ejemplo queda temporalmente no conforme (HS-INS-002) hasta el revert. | 2026-10-20 | Usuario (captura) |
| E-006 | **Evidencia L5 en instancia:** con el ruleset `main-protegida` activo en `harness-example-greenfield`, el PR #2 muestra `harness / conformance / harness check (pull_request)` fallido y marcado **Required**; el botón *Merge pull request* queda deshabilitado (captura del usuario, 2026-10-20). Verifica HS-GOV-004 completo (check ejecutado + requerido) en una instancia. | 2026-10-20 | Usuario (captura) |
| E-007 | **Evidencia de corrección:** el PR #3 (revert de #1) pasa `harness / conformance / harness check` (**Required**, 12 s) y el merge queda habilitado (captura del usuario, 2026-10-20). Ciclo completo demostrado: incumplimiento detectado → merge bloqueado → corrección → merge permitido. | 2026-10-20 | Usuario (captura) |
| D-019 | **Fase 1 cerrada** con los criterios de aceptación cumplidos (ver `fase-1/INFORME.md` §6). | 2026-10-20 | Usuario (validación de evidencias) |
| D-020 | **Q-02 resuelta:** el idioma de los archivos de cada instancia es **libre**; se declara en `project.docs_language` del manifiesto. La validación no depende del idioma (esquemas y anclas, ADR-004). | 2026-10-21 | Usuario |
| D-021 | **Q-04 resuelta como experimento:** el estado de las tareas se enlaza con **GitHub Issues** de forma provisional para evaluar si aporta y es eficiente. El diseño del experimento y su criterio de retirada se fijan en la Fase 2. | 2026-10-21 | Usuario |
| D-022 | **Experimento X-01 aprobado** sin cambios: issue como espejo del archivo de tarea (dirección única archivo→issue), `Closes #n` para cerrar, job de CI con `issues: write` separado, métricas y criterio de adopción/retirada (`docs/experimentos/X-01-tareas-y-github-issues.md`). | 2026-10-21 | Usuario |
| D-023 | **Q-11 resuelta:** requiere archivo de tarea si cambia comportamiento del código, toca > 1 segmento, riesgo medio/alto, > 1 sesión o la ejecuta un agente sin supervisión paso a paso. Exentas: documentación, formato/lint, parches de dependencias y reverts, con etiqueta `trivial` en el PR verificada por CI contra las rutas del diff. | 2026-10-21 | Usuario |
| D-024 | **F2.1 aprobada** (estructura canónica, roles N1, plantilla y esquema de ficha). Fusionada en `harness-standard-lab` (PR #2, commit `7ee8b5f`, 3 checks en verde). | 2026-10-21 | Usuario |
| D-025 | **F2.2 aprobada** (fichas de AGENTS.md raíz, de segmento y CLAUDE.md; anclas; candidatos C-01…C-10). Fusionada en `harness-standard-lab`. | 2026-10-21 | Usuario |
| D-026 | **F2.3 aprobada** (fichas de manifiesto/comandos, arquitectura, ADR, seguridad, referencias, CODEOWNERS y plantilla de PR; candidatos C-11…C-20). | 2026-10-21 | Usuario |
| D-027 | **ADR-016 aprobado:** la transición a `done` va en el propio PR y la verifica el check requerido `harness tasks`, que re-ejecuta los criterios de aceptación; los `manual` exigen `verified_by` aprobador del PR. | 2026-10-21 | Usuario |
| D-028 | **F2.4 aprobada** (esquema y ciclo de vida de tareas, `harness tasks`/`pr check`, workflow de tareas y plantilla N1). Fusionada en `harness-standard-lab` con la CI en verde; tag `cli-v0.2.0-rc.1`. | 2026-10-21 | Usuario |
| D-029 | **Aplicabilidad por versión aprobada:** un requisito aplica solo si `desde` ≤ `standard.version` declarada; cada nivel existe desde una versión (`niveles_desde`; N1 desde 0.2.0). Concreta parte de ADR-008. | 2026-10-21 | Usuario |
| D-030 | **F2.5 aprobada:** los 27 requisitos de 0.2.0 (HS-GOV-007/008, HS-INS-009…015, HS-CTX-002…004, HS-ARC-003…006, HS-SEC-005/006, HS-CI-001…003, HS-STA-001…006) pasan a `aprobado`. Fusionada en `harness-standard-lab` (PR #6). | 2026-10-21 | Usuario |
| E-009 | **Hallazgo F2.6 (simulación antes del laboratorio):** al pasar a `completed/` la última tarea activa, `active/` queda vacío y Git no lo versiona; fallan HS-STA-001 y el enlace de AGENTS.md. Lo detectó `harness check` en la simulación del PR #7 del ejemplo. Mitigación: `.gitkeep` en `active/` y `completed/` (ya en la plantilla; ahora explícito en la ficha). | 2026-10-21 | Claude |
| E-010 | **Adopción de N1 bajo control L5:** PR #5 de `harness-example-greenfield`, con `harness check` y `tasks / harness tasks` en verde y requeridos en el ruleset antes del merge. | 2026-10-22 | Usuario |
| E-011 | **ADR-016 validado (rechazo):** PR #7, commit `d60fd2d`. T-0002 declarada `done` sin implementar; `harness tasks` en rojo (AC1/AC2 con código 1) y merge bloqueado, con la conformidad en verde. | 2026-10-22 | Usuario |
| E-012 | **ADR-016 validado (aceptación):** PR #7, commit `2abc558`, con la implementación; ambos checks en verde y merge `e9946bd`. T-0001 pasó a `done` en el PR #6 tras volver a ejecutar `harness check --strict` como criterio. | 2026-10-22 | Usuario |
| E-013 | **X-01 de extremo a extremo:** issue #4 `status:ready` → `status:in_progress` → cerrada por `Closes #4` → `status:done` y comentario con enlace a la ejecución 39779093407, siempre por `github-actions`. | 2026-10-22 | Usuario |
| E-014 | **Regla `ask` (F3.6):** en modo *accept edits*, crear un archivo de control no pide confirmación y editar `AGENTS.md` sí (diálogo solo Yes/No). | 2026-10-23 | Usuario |
| E-015 | **Hook `verificar-al-terminar`:** con la prueba en rojo bloqueó la parada 3 veces con el mensaje exacto y después la permitió; con `check` en verde no intervino. | 2026-10-23 | Usuario |
| E-016 | **Subagente `verificador`:** ejecución en segundo plano (48 s); `check`, AC1, AC2 y `harness tasks validate` con código 0, sin editar. Informe resumido, no literal (H-3). | 2026-10-23 | Usuario |
| E-017 | **Skill `cerrar-tarea`:** cargada desde `.claude/skills/`; PR #10 con `done_pr` escrito tras abrir el PR y `tasks / harness tasks` en verde en el primer push del cierre. Con T-0003 (PR #11) no siguió el orden y la CI lo rechazó una vez (H-8). | 2026-10-23 | Usuario |
| E-018 | **Adopción 0.4.0 con componentes:** PR #9 de `harness-example-greenfield` con ambos checks requeridos en verde (incluida HS-CMP-009). Estado final `6bbe505`: 60 reglas, 0 errores, 0 avisos. | 2026-10-23 | Usuario |
| E-019 | **X-01:** issue #8 `in_progress` → cerrada por `Closes #8` → `status:done` con comentario, automáticamente. | 2026-10-23 | Usuario |
| E-020 | **`disableAutoMode` (F3.7):** con Shift+Tab solo aparecen *manual → accept edits → plan*; no `auto`. | 2026-10-24 | Usuario |
| E-021 | **Hook suspendido:** con `HARNESS_STOP_MAX=0` y rojo intencionado, Claude terminó en un turno sin bloqueo (F3.6: 3 turnos). Sin rastro visible del aviso (H-11). | 2026-10-24 | Usuario |
| E-022 | **Reglas de gh:** `gh api` pide confirmación citando la regla; `gh auth status` se deniega sin diálogo; `gh auth token`, rechazado por el propio modelo. | 2026-10-24 | Usuario |
| E-023 | **Cierre con `tasks close`:** PR #14 y #15 con la tarea cerrada por la CLI, sin edición manual, sin confirmación propia antes del push y con el bloque literal del verificador en el cuerpo. `gh pr edit` falló y el cuerpo lo subió la persona (H-13). | 2026-10-24 | Usuario |
| E-024 | **Confirmaciones:** 4 de edición y 25 de comandos en tres sesiones; 5 evitables sin tocar la seguridad (`fase-3/VALIDACION-F3.7.md` §2). | 2026-10-24 | Usuario |
| D-031 | **Fase 2 cerrada** con el criterio 1 parcial: 5 fichas aplazadas a la fase dueña de su subsistema (`adapter.claude.settings` → F3, `project.rules` → F4, `ci.workflows` y `runbooks.dir` → F5, `quality.doc` → F6). `fase-2/INFORME.md`. | 2026-10-22 | Usuario |
| D-032 | **Siguiente fase: F3** (componentes, catálogo y adaptador de Claude Code): contratos por tipo de componente, `catalog-entry` y ciclo de vida, `settings.json` deny-first, ADR-012 y 2–3 componentes semilla. | 2026-10-22 | Usuario |
| D-033 | **Plan de la F3 aprobado** (`fase-3/PLAN.md`): 6 incrementos, de F3.1 (modelo de componentes) a F3.6 (prueba en el laboratorio). | 2026-10-22 | Usuario |
| D-034 | **ADR-012 rev. 2 aprobado:** fuente canónica de skills en `.claude/skills/`, perfiles `portable` (por defecto) y `claude-code`, `.agents/skills/` generado por `harness sync` solo cuando un adaptador lo necesite, y validación propia en la CLI. | 2026-10-22 | Usuario |
| D-035 | **F3.1 aprobada** (modelo de componentes, `catalog-entry`, ciclo de vida, plantilla de ficha). Fusionada en `harness-standard-lab` (PR #9). | 2026-10-22 | Usuario |
| D-036 | **F3.2 aprobada** (adaptador de Claude Code, ficha `adapter.claude.settings`, `settings.json` deny-first), con el cambio de hook semilla: `verificar-al-terminar` (Stop) en lugar de `rutas-sensibles`, cuya función cubren las reglas `ask`. Fusionada (PR #10). | 2026-10-22 | Usuario |
| D-037 | **F3.3 aprobada:** los 16 requisitos de 0.3.0 (HS-CMP-001…008 y 010…013, HS-SEC-007…009, HS-CI-004) pasan a `aprobado`; `harness catalog validate` en la CI central. Fusionada (`03a1473`). | 2026-10-22 | Usuario |
| D-038 | **F3.4 aprobada:** componentes semilla `verificar-al-terminar` (hook, `es_control: false`), `verificador` (subagente) y `cerrar-tarea` (skill), en estado `experimental`; `harness catalog index`. | 2026-10-22 | Usuario |
| D-039 | **ADR-017 y F3.5 aprobados:** distribución de componentes por copia versionada (`harness components`, `.harness/components.lock`), HS-CMP-009 (deriva) aprobado, estándar 0.4.0. | 2026-10-22 | Usuario |
| D-040 | **Fase 3 cerrada** con los criterios 1–5 cumplidos (`fase-3/INFORME.md`). Fusionado en `harness-standard-lab` (PR #15). Las propuestas P-1…P-6 se deciden una a una para un incremento F3.7. | 2026-10-23 | Usuario |
| D-041 | **P-1 aprobada:** `disableAutoMode: "disable"` en la plantilla y requisito nuevo HS-SEC-010 (DEBE, N1, desde 0.5.0) en lugar de modificar HS-SEC-009 (D-029). Se reevalúa en F5. | 2026-10-23 | Usuario |
| D-042 | **P-2 aprobada:** `ask` para `Bash(gh api *)`; `deny` para `gh repo delete`, `gh secret`, `gh ruleset` y `gh auth`; HS-SEC-011 (DEBERÍA). Reducción de riesgo, no frontera. | 2026-10-23 | Usuario |
| D-043 | **P-3 aprobada:** `allow` solo para comandos del contrato sin efectos, `ask` para las opciones que ejecutan o escriben, test que congela las opciones y HS-SEC-012 (DEBERÍA) contra `allow` amplios. `check`/`test` de la instancia: decisión de cada instancia. | 2026-10-23 | Usuario |
| D-044 | **P-4 aprobada:** `harness tasks close T-NNNN --pr N` (transición determinista) y skill `cerrar-tarea` 0.2.0 que lo usa; `gh` opcional. | 2026-10-23 | Usuario |
| D-045 | **P-5 aprobada:** hook `verificar-al-terminar` 0.3.0 con límite 2 y suspensión con `HARNESS_STOP_MAX=0`. | 2026-10-23 | Usuario |
| D-046 | **P-6 aprobada:** verificador 0.2.0 con informe literal entre marcas; la skill lo copia en `harness:evidencia` y no pide confirmación propia antes del push. | 2026-10-23 | Usuario |
| E-008 | **Hallazgo (defecto de B corregido por el usuario):** con la CLI instalada por `pip`, `harness matrix` buscaba los fixtures en la copia empaquetada y fallaba en la CI central; el usuario lo corrigió (`--fixtures`, commit `1c27d0d`) y se generalizó a `--standard-root .` en F2.1. Lección: probar la CLI **instalada**, no solo desde el árbol de fuentes. | 2026-10-21 | Usuario |
| D-016 | El repositorio central se publicará en una **organización nueva de GitHub.com** creada en la cuenta del usuario (`AlbertoLacambra`). | 2026-10-20 | Usuario |

## Decisiones propuestas pendientes de aprobación

- **Validación de la F3.7** (`fase-3/VALIDACION-F3.7.md`): aceptar el resultado.
- **Propuestas por hallazgos de la validación** (se deciden una a una): P-8 forma de los comandos en skill y verificador (H-12, H-15); P-9 cuerpo del PR al crearlo, sin `gh pr edit` (H-13, H-16); P-10 tareas que solo se cierran (H-14); P-11 corregir la ficha del hook (H-11); P-12 `allow` para `git commit` y `gh pr create|view|ready`.
- **Siguiente fase:** F4 (segmentación y concurrencia; requiere un repositorio brownfield, Q-09) o F5 (CI/CD y seguridad; incluye el modo automático y `claude-code-action`).
- ADR-008 (resto de la actualización de instancias) → F7. ADR-010 → F5. ADR-011 → F4. ADR-014 → F4. ADR-015 → F6.

## Cuestiones abiertas

| ID | Cuestión | Necesaria para | Propuesta provisional |
|---|---|---|---|
| Q-01 | ¿Quién forma el grupo de gobierno con autoridad para aprobar cambios del estándar? **Aplazada por el usuario (2026-10-20)**; mientras tanto aprueba el usuario. | F9 | Un responsable de DevEx/plataforma, uno de seguridad y dos tech leads de equipos piloto |
| Q-02 | ~~Idioma de los archivos de instancia~~ **Resuelta (D-020): libre, declarado en el manifiesto.** | — | — |
| Q-03 | ~~Lenguaje de la CLI~~ | — | **Resuelta (D-014): Python** |
| Q-04 | ~~Estado de tareas y GitHub Issues~~ **Resuelta como experimento (D-021, X-01 aprobado D-022).** | — | — |
| Q-05 | Plataforma de despliegue (Actions + environments, ArgoCD, otra). | F5 | Por confirmar |
| Q-06 | Fuente de la telemetría de coste y tokens del agente (consola de la organización, OpenTelemetry, logs de CI). | F6 | Por verificar qué expone Claude Code |
| Q-07 | En la v1, ¿skills en `.agents/skills` con sincronización o directamente en `.claude/skills`? | F3 | ADR-012 |
| Q-08 | ¿Hay requisitos regulatorios o de cliente (datos, auditoría, EU AI Act) que afecten al uso de agentes? | F5 | Por confirmar con seguridad y legal |
| Q-10 | ~~Organización y visibilidad~~ **Resuelta:** `ALacambraPoCs`, repos públicos, plan Free (D-018). Pendiente solo: equipos (se usa `@AlbertoLacambra`). | F2 | — |
| Q-11 | ~~Umbral de tarea trivial~~ **Resuelta (D-023).** | — | — |
| Q-12 | ¿Se pueden restringir los comandos Bash de un subagente (p. ej. el `verificador`) por configuración, o solo con sandbox? Hoy su «solo lectura» es L1. | F5 | Verificar en la documentación de subagentes y sandbox |
| Q-09 | Repositorios candidatos para el piloto (1 greenfield + 1 brownfield grande). | F8 (identificar en F2) | Por designar |

## Riesgos

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R-01 | Las capacidades de las herramientas cambian rápido (versiones de Claude Code, migración de la documentación de Codex) y el estándar queda obsoleto. | Alta | Medio | Núcleo agnóstico, adaptadores con versión mínima, reverificación trimestral con fecha |
| R-02 | Sobreingeniería: una plantilla demasiado pesada para repositorios pequeños. | Media | Alto | Niveles N0–N3, presupuesto de complejidad, ablación (ADR-015) |
| R-03 | Confianza indebida en instrucciones de lenguaje natural como control. | Media | Alto | ADR-009: lo crítico se impone en permisos, CI y rulesets |
| R-04 | Validador manipulable (cumplir la letra y no el fondo). | Media | Medio | Esquemas, reglas de ejecución y revisión humana de muestras en el piloto |
| R-05 | Fricción de adopción en brownfield grande. | Alta | Alto | Entrada por N0, manifiesto con rutas existentes, waivers que caducan |
| R-06 | Importar como normas cifras o umbrales del curso (T4) sin evidencia. | Media | Medio | Solo como valores por defecto ajustables y marcados así |
| R-07 | La configuración de agentes del repositorio como vector de ataque (hooks, MCP, instrucciones modificadas en un PR). | Media | Alto | ADR-013 |
| R-09 | **Cerrado** (E-001, E-003, E-004, E-006, E-007). | Media | Medio | Ejecutarlos al publicar el repo (Q-10) antes de cerrar F2 |
| R-10 | Laboratorio con un único mantenedor: no se pueden exigir aprobaciones ni revisión de code owner (GitHub no permite autoaprobar). Los controles L5 de revisión quedan sin ejercitar. | Alta | Medio | Desviación documentada en `fase-1/PUBLICACION.md` §6; se corrige con un segundo mantenedor o en el piloto (F8) |
| R-11 | Copiar archivos de Windows a WSL añade metadatos ADS (`*:Zone.Identifier`, `*:sec.endpointdlp`) que se versionan y rompen el clonado en Windows. Ocurrió en la primera subida (171 archivos). | Media | Medio | Eliminados por el usuario; `.gitignore` los ignora y la CI central rechaza rutas no portables (cli 0.1.1). Propuesta para F2: requisito de rutas portables en instancias. |
| R-12 | ~~Mitigado por D-018 (repos públicos: no hace falta token)~~. En privado, la instancia lee el repo del estándar con un **PAT fine-grained personal** (Contents: read, 1 repo, caducidad ≤ 90 días): credencial de larga duración ligada a una persona. | Media | Medio | Aceptado para el laboratorio. F5: sustituir por GitHub App de solo lectura o publicar la CLI como paquete interno. |
| R-13 | **Hallazgo F2.2:** con el `CLAUDE.md` raíz que exige ADR-003, Claude Code (ajuste por defecto) **no carga** los `AGENTS.md` de subdirectorios (S-CC-MEM). Sin mitigación, las instrucciones de segmento serían invisibles para Claude. | Alta (si hay segmentos) | Alto | `<segmento>/CLAUDE.md` con `@AGENTS.md` obligatorio (fichas F2.2; requisito candidato C-07 en F2.5) |
| R-14 | **Hallazgo F3 (H5):** con `claude -p` sin `--bare`, Claude Code ejecuta los hooks y los MCP de `.claude/settings.json` y `.mcp.json` del repositorio aunque la carpeta no sea de confianza. Un PR malicioso podría ejecutar código en el runner de CI si el agente se lanza sobre ese PR. | Media | Alto | En CI, el agente siempre con `--bare` y `--settings`/`--mcp-config` explícitos desde una ruta de confianza (no del PR). Se norma en F3.2 y F5 |
| R-15 | **Hallazgo F3.6 (H-4, H-9):** el coste en confirmaciones (26 en dos sesiones) empuja a aprobar «y no volver a preguntar» o a activar el modo automático, que Claude Code sugiere en el propio diálogo. La base no desactiva el modo automático. | Alta | Alto | P-1 (`disableAutoMode`) y P-3 (`allow` para comandos del contrato sin efectos); medir confirmaciones en F6 |
| R-16 | **Hallazgo F3.6 (H-7):** cuando un comando `gh` falla, el agente recurre a `gh api`, que puede escribir en GitHub sin regla específica. Las reglas Bash no son frontera (otras formas de invocación). | Media | Alto | P-2 (`ask` para `gh api`, `deny` para operaciones destructivas); sandbox y token de mínimo privilegio en F5 |
| R-17 | **Hallazgo de la validación F3.7 (H-12, H-13, H-15):** el agente compone comandos (`; echo $?`, `\| tail`, `&&`) que anulan las reglas `allow` y ocultan errores; un paso fallido puede darse por bueno. | Alta | Medio | P-8 y P-9; la CI sigue siendo la autoridad y detectó todos los casos |
| R-08 | Afirmaciones sobre la documentación oficial obtenidas por un subagente que no se han revisado a mano. | Media | Medio | Se revisaron a mano las críticas para ADR-003 y ADR-012 (memoria y skills de Claude Code). El resto se reverifica en la fase en que se norme. |

## Próximos pasos

1. **Usuario:** aceptar la validación de la F3.7 y decidir P-8…P-12 una a una. Después, plan de la F5 (recomendada por encima de la F4).
2. **X-01:** seguir midiendo (umbral: ≥ 4 semanas o ≥ 20 tareas; hoy 4 tareas, 0 desincronizaciones).
3. **Pendientes heredados:**
   - Secret Protection y push protection en repos públicos;
   - borrar el secreto `HARNESS_STANDARD_TOKEN` del ejemplo y revocar el PAT;
   - escáner de secretos (F5);
   - verificar a mano S-CODEX-AGENTSMD (R-08);
   - segundo mantenedor (R-10);
   - candidato K-14 (avisar si cambian los criterios de aceptación en un PR que cierra la tarea).
