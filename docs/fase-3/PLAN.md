---
documento: F3-PLAN
titulo: Plan de la Fase 3 — Componentes, catálogo y adaptador de Claude Code
estado: aprobado (D-033)
fecha: 2026-10-22
depende_de: [D-031, D-032, ADR-003, ADR-009, ADR-012, ADR-013, ADR-015, ADR-016]
---

# Fase 3 · Plan

## Objetivo

Definir **qué es un componente del harness** y cómo se describe, valida, distribuye y retira. Un componente es una skill, un subagente, un hook, un plugin, un servidor o herramienta MCP, o un workflow.

También hay que fijar **cómo se configura Claude Code de forma segura** en una instancia.

La fase termina con 3 componentes semilla publicados en el catálogo, validados por la CLI y usados de verdad en el laboratorio.

Principio rector (encargo, ADR-015): **ningún componente entra por defecto**. Cada uno tiene propósito, responsable, coste, validación y condición de retirada. Solo cuenta como control lo que es determinista (ADR-009, C9).

## Incrementos

| # | Entregable | Contenido | Depende de |
|---|---|---|---|
| **F3.1** | Modelo de componentes | Contrato neutro por tipo (definición, entrada y salida, permisos, compatibilidad, pruebas, propietario, versión, estado, riesgos, retirada). Esquema `schemas/catalog-entry.schema.json`. Ciclo de vida: `experimental → estable → deprecado → retirado`. Ficha de componente de 17 puntos (plantilla). **Decisión ADR-012** | — |
| **F3.2** | Adaptador de Claude Code | `standard/adaptadores/claude-code.md`: mapeo de núcleo a archivos reales y versión mínima. Ficha `adapter.claude.settings` (aplazada de F2). `settings.json` base deny-first en la plantilla. Uso del agente en CI (`--bare`, H5). Requisitos candidatos | F3.1 |
| **F3.3** | Validación en la CLI | `harness components validate`: entradas del catálogo, especificación de skills implementada en la CLI (H4), frontmatter de subagentes y lint de hooks (solo `command` cuenta como control; scripts presentes y bajo CODEOWNERS). Si ADR-012 lo requiere, `harness sync` con comprobación de deriva | F3.1, F3.2 |
| **F3.4** ✅ (D-038) | 3 componentes semilla | (a) **hook** `verificar-al-terminar`: `Stop` que ejecuta `check` y `harness tasks validate` y, si fallan, devuelve exit 2 para que el agente no dé el trabajo por terminado. *(Cambio en F3.2: la confirmación en rutas sensibles la dan las reglas `ask` de `settings.json`, ver `adaptadores/claude-code.md` §6.)* (b) **subagente** `verificador`: solo lectura; ejecuta `check`, `test` y los criterios de la tarea, e informa con evidencia, sin autoridad. (c) **skill** `cerrar-tarea`: procedimiento ADR-016 (rellenar `done_pr` tras abrir el PR, resultado, índice, `Closes #n`), que ataca la fricción vista en F2.6. Cada uno con ficha de 17 puntos, entrada en el catálogo, pruebas y condición de retirada | F3.1–F3.3 |
| **F3.5** ✅ (D-039) | Distribución | Cómo llega un componente del catálogo central a una instancia: copia versionada (`harness sync`) frente a plugin y marketplace interno (`enabledPlugins`). Prototipo de la opción elegida | F3.4 |
| **F3.6** ✅ (D-040) | Prueba en el laboratorio | `harness-example-greenfield` instala los 3 componentes y se ejecuta una tarea real (T-0003) con Claude Code. Evidencias: el hook pide confirmación, el verificador informa, la skill cierra la tarea y la CI lo verifica | F3.5 |
| **F3.7** ✅ (PR #16; validada, `VALIDACION-F3.7.md`) | Ajustes por hallazgos | P-1…P-6 del `INFORME.md` (D-041…D-046): `disableAutoMode`, reglas `gh`, `allow` acotados, `harness tasks close`, hook 0.3.0, verificador y skill 0.2.0. Estándar 0.5.0 | F3.6 |

## Decisiones que se tomarán (una a una, cuando toque)

| Momento | Decisión | Propuesta provisional |
|---|---|---|
| F3.1 | ADR-012: ubicación canónica de las skills | **Revisada por H2:** fuente en `.claude/skills/`, limitada a los campos de la especificación salvo excepción marcada; `.agents/skills/` se genera solo cuando haya un adaptador que lo necesite (Codex o Gemini) |
| F3.1 | Validador de skills | Implementación propia en la CLI, porque `skills-ref` es solo una demostración (H4) |
| F3.2 | Base de `settings.json` | Deny de lectura de secretos y de edición de rutas sensibles sin confirmación; `disableBypassPermissionsMode`; sin aprobación automática de MCP del proyecto. Asumiendo que la regla deny no basta (H6) |
| F3.5 | Mecanismo de distribución | Se decide con el prototipo. Hoy los plugins solo de proyecto no se descargan salvo que la fuente sea una ruta relativa (verificado), lo que favorece la copia versionada para la v1 |

## Criterios de aceptación de la fase

1. Cada tipo de componente tiene contrato y el esquema `catalog-entry` valida y rechaza con fixtures.
2. Los 3 componentes semilla tienen ficha de 17 puntos, entrada válida en el catálogo, pruebas automáticas y condición de retirada.
3. La plantilla N1 con el adaptador de Claude Code supera su validador, `settings.json` incluido.
4. No hay deriva entre el catálogo y la instancia tras la sincronización (si se aprueba `harness sync`).
5. Evidencia en el laboratorio de los 3 componentes funcionando en una tarea real, y de que las reglas `ask` de `settings.json` piden confirmación en una ruta sensible.

## Supuestos y riesgos

- **Supuesto:** tienes Claude Code instalado en local (≥ 2.1.277) para la F3.6. Si no, la evidencia de F3.6 se limitará a pruebas automáticas de los hooks y a ejecuciones con `claude -p --bare` en CI.
- **Riesgo R-01** (capacidades cambiantes): los 33 eventos de hooks y los campos de los subagentes cambian a menudo. El adaptador fija la versión mínima y la fecha de verificación (2026-10-22).
- **Riesgo nuevo:** que el catálogo crezca por moda. Mitigación: cada componente nace en `experimental` y solo pasa a `estable` con evidencia de uso (métrica en la ficha) y revisión. La retirada se evalúa por ablación en F6.

## Fuentes

Ver `01-verificacion-fuentes.md`. Principales: S-SKILLS, S-CC-SKILLS, S-CC-SET (hooks, sub-agents, settings, permissions, plugins, mcp, headless), S-MCP 2026-07-28 y OWASP LLM01:2025.
