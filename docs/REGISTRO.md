---
documento: REGISTRO
titulo: Registro vivo — decisiones, cuestiones abiertas, riesgos y próximos pasos
actualizado: 2026-10-20 (repo central publicado; CI en verde; pendiente prueba de extremo a extremo)
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
| E-001 | **Evidencia:** `ALacambraPoCs/harness-standard-lab` publicado; workflow `ci` en verde en Python 3.11/3.12/3.13 (reportado por el usuario, 2026-10-20). Avisos: deprecación de Node 20 en `actions/checkout@v4`/`setup-python@v5` y migración de `ubuntu-latest` a Ubuntu 26 → corregidos en cli 0.1.1. | 2026-10-20 | Usuario (reporte) |
| D-016 | El repositorio central se publicará en una **organización nueva de GitHub.com** creada en la cuenta del usuario (`AlbertoLacambra`). | 2026-10-20 | Usuario |

## Decisiones propuestas pendientes de aprobación

- ADR-008 (parte de actualización de instancias) → F7. ADR-010 → F5. ADR-011 → F4. ADR-012 → F3. ADR-014 → F4. ADR-015 → F6.

## Cuestiones abiertas

| ID | Cuestión | Necesaria para | Propuesta provisional |
|---|---|---|---|
| Q-01 | ¿Quién forma el grupo de gobierno con autoridad para aprobar cambios del estándar? **Aplazada por el usuario (2026-10-20)**; mientras tanto aprueba el usuario. | F9 | Un responsable de DevEx/plataforma, uno de seguridad y dos tech leads de equipos piloto |
| Q-02 | Idioma de los archivos de instancia (AGENTS.md, docs/): ¿inglés, español o libre? | F2 | Libre, porque la validación es por esquema y anclas. El idioma se declara en el manifiesto. |
| Q-03 | ~~Lenguaje de la CLI~~ | — | **Resuelta (D-014): Python** |
| Q-04 | ¿Dónde vive el estado de las tareas: solo en el repositorio, o enlazado con GitHub Issues/Projects? | F2/F4 | En el repositorio como fuente, con enlace opcional a la issue |
| Q-05 | Plataforma de despliegue (Actions + environments, ArgoCD, otra). | F5 | Por confirmar |
| Q-06 | Fuente de la telemetría de coste y tokens del agente (consola de la organización, OpenTelemetry, logs de CI). | F6 | Por verificar qué expone Claude Code |
| Q-07 | En la v1, ¿skills en `.agents/skills` con sincronización o directamente en `.claude/skills`? | F3 | ADR-012 |
| Q-08 | ¿Hay requisitos regulatorios o de cliente (datos, auditoría, EU AI Act) que afecten al uso de agentes? | F5 | Por confirmar con seguridad y legal |
| Q-10 | Organización de GitHub: **`ALacambraPoCs`**, repo central `harness-standard-lab` (respondida 2026-10-20). Pendiente: **visibilidad** (público recomendado, ver `fase-1/PUBLICACION.md` §1) y equipos (se usa `@AlbertoLacambra` mientras tanto). | F1 | Público en Free |
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
| R-09 | ~~CI del repo central sin ejecutar~~ (ejecutada, E-001). Sigue abierto: el workflow reutilizable no se ha ejecutado aún desde una instancia. | Media | Medio | Ejecutarlos al publicar el repo (Q-10) antes de cerrar F2 |
| R-10 | Laboratorio con un único mantenedor: no se pueden exigir aprobaciones ni revisión de code owner (GitHub no permite autoaprobar). Los controles L5 de revisión quedan sin ejercitar. | Alta | Medio | Desviación documentada en `fase-1/PUBLICACION.md` §6; se corrige con un segundo mantenedor o en el piloto (F8) |
| R-11 | Copiar archivos de Windows a WSL añade metadatos ADS (`*:Zone.Identifier`, `*:sec.endpointdlp`) que se versionan y rompen el clonado en Windows. Ocurrió en la primera subida (171 archivos). | Media | Medio | Eliminados por el usuario; `.gitignore` los ignora y la CI central rechaza rutas no portables (cli 0.1.1). Propuesta para F2: requisito de rutas portables en instancias. |
| R-08 | Afirmaciones sobre la documentación oficial obtenidas por un subagente que no se han revisado a mano. | Media | Medio | Se revisaron a mano las críticas para ADR-003 y ADR-012 (memoria y skills de Claude Code). El resto se reverifica en la fase en que se norme. |

## Próximos pasos

1. **Usuario:** ejecutar `docs/fase-1/PUBLICACION.md` (push de los dos repositorios, rulesets, prueba de extremo a extremo) y devolver los resultados para registrarlos como evidencia (cierra R-09).
2. **Fase 2** (estructura canónica y fichas de archivo del núcleo): fichas de AGENTS.md, mapa de arquitectura, ADR, tareas/planes (esquema de tarea, ADR-005), seguridad, contrato de comandos, CODEOWNERS y plantilla de PR; requisitos N1; reglas y fixtures asociados.
3. Leer para F2: cookbook de planes de ejecución de OpenAI; estudio ETH Zurich sobre AGENTS.md; matklad ARCHITECTURE.md.
