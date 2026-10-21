---
documento: REGISTRO
titulo: Registro vivo — decisiones, cuestiones abiertas, riesgos y próximos pasos
actualizado: 2026-10-21 (F2.3 entregada; pendiente de aprobación)
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
| E-008 | **Hallazgo (defecto de B corregido por el usuario):** con la CLI instalada por `pip`, `harness matrix` buscaba los fixtures en la copia empaquetada y fallaba en la CI central; el usuario lo corrigió (`--fixtures`, commit `1c27d0d`) y se generalizó a `--standard-root .` en F2.1. Lección: probar la CLI **instalada**, no solo desde el árbol de fuentes. | 2026-10-21 | Usuario |
| D-016 | El repositorio central se publicará en una **organización nueva de GitHub.com** creada en la cuenta del usuario (`AlbertoLacambra`). | 2026-10-20 | Usuario |

## Decisiones propuestas pendientes de aprobación

- ADR-008 (parte de actualización de instancias) → F7. ADR-010 → F5. ADR-011 → F4. ADR-012 → F3. ADR-014 → F4. ADR-015 → F6.

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
| R-08 | Afirmaciones sobre la documentación oficial obtenidas por un subagente que no se han revisado a mano. | Media | Medio | Se revisaron a mano las críticas para ADR-003 y ADR-012 (memoria y skills de Claude Code). El resto se reverifica en la fase en que se norme. |

## Próximos pasos

1. **Usuario:** fusionar el PR #3 del ejemplo y subir al repo central, mediante PR, la actualización documental (`fase1-cierre.patch`).
2. **Fase 2** — estructura canónica y fichas de archivo del núcleo + requisitos N1 (alcance propuesto en `fase-1/INFORME.md` §7).
3. Pendientes heredados: Secret Protection/push protection en repos públicos (verificar UI), requisito de rutas portables en instancias (R-11), escáner de secretos en CI (F5), sustituir PAT si vuelve a haber repos privados (R-12).
