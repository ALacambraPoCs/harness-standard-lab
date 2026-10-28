---
documento: HS-03
titulo: Estructura canónica de una instancia (N0–N1)
version_estandar: 0.2.0-borrador
estado: propuesta (F2.1)
fecha: 2026-10-21
adr: [ADR-003, ADR-004, ADR-005, ADR-006, ADR-013, ADR-014]
fuente_de_verdad: standard/roles.yaml
---

# 03 · Estructura canónica de una instancia

## 1. Objeto

Este documento define **qué archivos y directorios forma una instancia del harness**, cuáles son obligatorios en cada nivel y dónde viven.

La fuente de verdad es `standard/roles.yaml`, validado con `schemas/roles.schema.json`. La tabla del §3 se **genera** a partir de ese archivo con `harness roles --write`, y la CI comprueba que esté al día. Si el texto de este documento y `roles.yaml` discrepan, prevalece `roles.yaml`.

**Fuera de alcance:**

- La estructura del código de la aplicación (`src/`, paquetes, módulos). El estándar no impone ninguna arquitectura de aplicación. Solo exige que el proyecto declare sus límites (mapa de arquitectura) y, a partir de N2, sus segmentos (Fase 4).
- El contenido detallado de cada archivo, que se define en su ficha (`standard/04-archivos/`, F2.2–F2.4).

## 2. Árbol de referencia (N0 y N1)

Leyenda: **O** obligatorio · **C** condicional · **R** recomendado · **P** opcional · **G** generado (no se edita a mano) · **X** prohibido versionar.

```
<repo>/
├── AGENTS.md                              O  N0  índice de instrucciones (ADR-003)
├── CLAUDE.md                              C  N0  si adaptador claude-code: "@AGENTS.md" + exclusivo
├── CLAUDE.local.md                        X  N0  preferencias personales → .gitignore
├── .gitignore                                    incluye CLAUDE.local.md y .claude/settings.local.json
├── .harness/
│   ├── manifest.yaml                      O  N0  versión, nivel, adaptadores, comandos, roles, waivers
│   ├── rules/                             C  N1  reglas de arquitectura verificables (Fase 4)
│   └── segments.yaml                      O  N2  mapa de segmentos (Fase 4)
├── docs/
│   ├── architecture/ARCHITECTURE.md       O  N0  mapa de dominios, capas y límites       (reubicable)
│   ├── decisions/                         O  N0  ADR del proyecto + README.md índice     (reubicable)
│   ├── security/SECURITY.md               O  N0  amenazas, secretos, acciones con aprobación (reubicable)
│   ├── plans/                             O  N1  tareas y planes (ADR-005)                (reubicable)
│   │   ├── INDEX.md                       G  N1  índice generado por la CLI
│   │   ├── active/T-NNNN-<slug>.md        O  N1  una tarea por archivo
│   │   └── completed/T-NNNN-<slug>.md     O  N1  tareas en estado terminal
│   ├── quality/QUALITY.md                 R  N1  estado de calidad por segmento (Fase 6)
│   ├── runbooks/                          C  N1  si se despliega u opera (Fase 5)
│   └── references/                        P  N0  documentación externa condensada para el modelo
├── <segmento>/AGENTS.md                   C  N0  instrucciones locales (gana el más cercano)
├── .claude/settings.json                  C  N1  si claude-code: permisos deny-first, hooks (Fase 3)
├── .github/
│   ├── CODEOWNERS                         O  N0  incluye las rutas sensibles (ADR-013)
│   ├── pull_request_template.md           O  N1  enlaza tarea, riesgo y evidencia
│   └── workflows/
│       ├── harness.yml                    O  N0  conformidad (llama al workflow reutilizable)
│       └── harness-tasks.yml              O  N1  ciclo de vida de tareas y espejo en issues (F2.4, X-01)
└── Makefile | justfile | package.json …   O  N0  implementación del contrato de comandos (ADR-006)
```

`harness-tasks.yml` y el contrato de comandos no son roles con ruta fija. Los detecta una regla por su contenido (Fase 2.4) y por el manifiesto (ADR-006), respectivamente.

## 3. Roles (vista generada)

<!-- generado:roles:inicio (harness roles --write) -->
| Rol | Ruta por defecto | Tipo | Oblig. | Nivel | Capa | Reubicable | Condición | Ficha |
|---|---|---|---|---|---|---|---|---|
| `manifest` | `.harness/manifest.yaml` | archivo | O | N0 | nucleo | no | — | [ficha](04-archivos/manifest.md) |
| `instructions.root` | `AGENTS.md` | archivo | O | N0 | nucleo | no | — | [ficha](04-archivos/instructions.root.md) |
| `instructions.segment` | `<segmento>/AGENTS.md` | archivo | C | N0 | nucleo | no | El segmento tiene reglas, comandos o límites propios que no aplican al resto del repositorio. | [ficha](04-archivos/instructions.segment.md) |
| `adapter.claude.instructions` | `CLAUDE.md` | archivo | C | N0 | adaptador:claude-code | no | El manifiesto declara el adaptador claude-code. | [ficha](04-archivos/adapter.claude.instructions.md) |
| `adapter.claude.local` | `CLAUDE.local.md` | archivo | X | N0 | adaptador:claude-code | no | Preferencias personales de cada persona; DEBE estar en .gitignore (HS-SEC-003). | [ficha](04-archivos/adapter.claude.instructions.md) |
| `architecture.map` | `docs/architecture/ARCHITECTURE.md` | archivo | O | N0 | nucleo | sí | — | [ficha](04-archivos/architecture.map.md) |
| `decisions.dir` | `docs/decisions` | directorio | O | N0 | nucleo | sí | — | [ficha](04-archivos/decisions.dir.md) |
| `security.policy` | `docs/security/SECURITY.md` | archivo | O | N0 | nucleo | sí | — | [ficha](04-archivos/security.policy.md) |
| `quality.doc` | `docs/quality/QUALITY.md` | archivo | R | N1 | nucleo | sí | — | pendiente:F6 |
| `runbooks.dir` | `docs/runbooks` | directorio | C | N1 | nucleo | sí | El repositorio se despliega o se opera en un entorno compartido. | pendiente:F5 |
| `references.dir` | `docs/references` | directorio | P | N0 | nucleo | sí | — | [ficha](04-archivos/references.dir.md) |
| `plans.dir` | `docs/plans` | directorio | O | N1 | nucleo | sí | — | [ficha](04-archivos/plans.dir.md) |
| `plans.active` | `{plans.dir}/active` | directorio | O | N1 | nucleo | no | — | [ficha](04-archivos/plans.dir.md) |
| `plans.completed` | `{plans.dir}/completed` | directorio | O | N1 | nucleo | no | — | [ficha](04-archivos/plans.dir.md) |
| `plans.index` | `{plans.dir}/INDEX.md` | archivo | G | N1 | nucleo | no | Lo genera la CLI a partir de los archivos de tarea; no se edita a mano. | [ficha](04-archivos/plans.dir.md) |
| `project.rules` | `.harness/rules` | directorio | C | N1 | nucleo | no | El proyecto declara límites de arquitectura que se verifican de forma mecánica. | pendiente:F4 |
| `segments.map` | `.harness/segments.yaml` | archivo | O | N2 | nucleo | no | — | pendiente:F4 |
| `adapter.claude.settings` | `.claude/settings.json` | archivo | C | N1 | adaptador:claude-code | no | El manifiesto declara claude-code y el nivel es N1 o superior. | [ficha](04-archivos/adapter.claude.settings.md) |
| `codeowners` | `.github/CODEOWNERS` (alt.: CODEOWNERS, docs/CODEOWNERS) | archivo | O | N0 | adaptador:github | no | — | [ficha](04-archivos/codeowners.md) |
| `pr.template` | `.github/pull_request_template.md` (alt.: pull_request_template.md, docs/pull_request_template.md) | archivo | O | N1 | adaptador:github | no | — | [ficha](04-archivos/pr.template.md) |
| `ci.workflows` | `.github/workflows` | directorio | O | N0 | adaptador:github | no | — | [ficha](04-archivos/ci.workflows.md) |
<!-- generado:roles:fin -->

## 4. Dónde vive cada tipo de conocimiento

Esta tabla es la regla de ubicación. Se convertirá en requisitos en la F2.5. Se adapta del SOP *encode knowledge into repo* (S-LHE, OpenAI advanced pack) y de S-OAI-HE p.5-7.

| Tipo de conocimiento | Dónde vive | Dónde **no** debe vivir |
|---|---|---|
| Qué es el proyecto, comandos canónicos, restricciones duras, mapa de documentos | `AGENTS.md` raíz | Wikis o chats externos sin reflejo en el repo |
| Reglas que solo aplican a una parte del código | `<segmento>/AGENTS.md` | `AGENTS.md` raíz (hincha el contexto de todos) |
| Peculiaridades de una herramienta de agente | Su adaptador (`CLAUDE.md`, `.claude/`) | `AGENTS.md` (núcleo agnóstico) |
| Estructura, límites y dependencias permitidas | `architecture.map` | Instrucciones (se duplicaría) |
| Por qué se decidió algo | `decisions.dir` (ADR) | Comentarios sueltos, descripciones de PR |
| Qué se está haciendo, progreso, bloqueos, evidencia | Archivo de tarea en `plans.active` | `AGENTS.md`, `CLAUDE.md`, issues como fuente (X-01: la issue es espejo) |
| Comandos y su invocación real | `commands` del manifiesto + herramienta de build | Copias divergentes en la documentación |
| Reglas que deben cumplirse siempre | Linters, tests, `.harness/rules/`, CI | Solo en lenguaje natural (ADR-009) |
| Amenazas, secretos, acciones que requieren aprobación | `security.policy` | Instrucciones únicamente |
| Preferencias personales | `CLAUDE.local.md` (no versionado) | Archivos versionados |
| Documentación de terceros que el modelo necesita | `references.dir`, con fuente y fecha | Pegada dentro de las instrucciones |
| Credenciales y secretos | Gestor de secretos o variables de CI | **Ningún archivo del repositorio** (HS-SEC-004) |

## 5. Convenciones de nombres y rutas

1. **Rutas portables.** Ningún archivo versionado contiene en su ruta `:`, `<`, `>`, `"`, `|`, `?`, `*` o `\`, ni un segmento que termine en espacio o en punto. Origen: incidente R-11. Pasará a requisito en la F2.5.
2. **Archivos de tarea:** `T-NNNN-<slug>.md`, con `NNNN` correlativo de 4 dígitos en el repositorio y `<slug>` en minúsculas con guiones (`a-z0-9-`). El ID `T-NNNN` coincide con el campo `id` del frontmatter (F2.4).
3. **ADR del proyecto:** `NNNN-<slug>.md` en `decisions.dir`, más un `README.md` índice.
4. **Directorios del estándar:** `.harness/` está reservado para el estándar. Los proyectos no deben guardar ahí archivos propios ajenos a los roles definidos.
5. **Idioma libre** (D-020): el contenido puede escribirse en cualquier idioma, declarado en `project.docs_language`. Los nombres de rol, rutas canónicas, claves de esquema y anclas son fijos y no se traducen.

## 6. Archivos generados

- Llevan en la primera línea un comentario `<!-- generado por harness <comando>; no editar -->` o el equivalente de su formato.
- La CI regenera cada archivo y falla si difiere de lo versionado. Es el mismo patrón que `docs/MATRIZ.md` en el repo central.
- En N1 el único generado es `plans.index`. Los artefactos de adaptador generados (por ejemplo `.claude/skills/`, ADR-012) llegan en la Fase 3.

## 7. Instrucciones locales de segmento

- Un `AGENTS.md` en un subdirectorio aplica a ese subárbol y prevalece sobre el raíz cuando entran en conflicto. Es la semántica de S-AGENTSMD ("gana el más cercano"). **Claude Code no lo carga por sí solo** cuando existe un `CLAUDE.md` raíz (S-CC-MEM, verificado 2026-10-21), así que con el adaptador `claude-code` cada `<segmento>/AGENTS.md` necesita al lado un `<segmento>/CLAUDE.md` con `@AGENTS.md` (ficha `instructions.segment`).
- Solo se crea si el segmento tiene reglas, comandos o límites propios. No se crean `AGENTS.md` vacíos o redundantes.
- Ese `<segmento>/CLAUDE.md` contiene solo `@AGENTS.md` y lo exclusivo de Claude (ADR-003). Lo valida una regla de la F2.5.
- En N2 los segmentos se declaran en `segments.yaml` y las instrucciones locales se validan contra él (Fase 4).

## 8. Repositorios existentes (brownfield)

- Los roles con **reubicable = sí** pueden declarar su ruta actual en `roles` del manifiesto. Así no hay que mover documentación existente (ADR-004).
- Los roles con ruta fija (`AGENTS.md`, `CLAUDE.md`, `.harness/*`, CODEOWNERS, workflows) lo son porque la herramienta destino o el propio estándar los buscan ahí.
- Si un rol se reubica, sus roles hijos (`relativa_a`) siguen al padre. Por ejemplo, con `plans.dir: work/tasks`, `plans.active` pasa a ser `work/tasks/active`.

## 9. Pendiente en fases posteriores

| Tema | Fase |
|---|---|
| Fichas de cada rol (contenido requerido y excluido, anclas) | F2.2–F2.4 |
| Requisitos N1 derivados de §4 y §5 | F2.5 |
| `.claude/settings.json`, skills, agentes y hooks | F3 |
| Segmentos, monorepo y `.harness/rules/` | F4 |
| Runbooks, workflows de despliegue y escáner de secretos | F5 |
| `quality.doc` y métricas | F6 |
