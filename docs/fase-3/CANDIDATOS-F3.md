---
documento: F3-CANDIDATOS
titulo: Requisitos candidatos de la Fase 3 (componentes y adaptador de Claude Code)
estado: lista viva
actualizado: 2026-10-22 (F3.3: formalizados)
---

# Requisitos candidatos de la F3

**Formalizados en F3.3** (`requirements.yaml`, estado `propuesto`, `desde: 0.3.0`):

| Candidato | Requisito(s) | Cambio respecto al candidato |
|---|---|---|
| K-01, K-02 | HS-CMP-010, HS-CMP-011 | K-02 lo impone el propio esquema `catalog-entry` |
| K-03 | HS-CMP-013 | Se añade la obligación de subir `version` si cambian los archivos |
| K-04 | HS-CMP-001, HS-CMP-002, HS-CMP-012 | El perfil se declara en `metadata.harness-perfil` (campo de la especificación) |
| K-05 | HS-CMP-003 | Sin `harness sync` todavía: avisa si existe `.agents/skills/` |
| K-06 | HS-CMP-007 | Semiautomático |
| K-07 | HS-CMP-004, HS-CMP-005 | «Revisor» no se puede detectar de forma fiable; se exige `tools` explícito en todo subagente |
| — | HS-CMP-006 | Nuevo: scripts de hooks existentes |
| K-08 | HS-CMP-009 (0.4.0, F3.5) | Con lock y SHA-256; ADR-017 |
| K-09, K-10, K-11 | HS-SEC-007, HS-SEC-008, HS-SEC-009 | — |
| K-12 | HS-CI-004 | Solo `run: claude -p`; `claude-code-action` en F5 |
| K-13 | HS-CMP-008 | — |

| # | Candidato | Nivel | Ámbito | Niveles | Verificación | Origen |
|---|---|---|---|---|---|---|
| K-01 | Cada componente del catálogo tiene `componente.yaml` válido contra `catalog-entry.schema.json` y `FICHA.md` con los 17 apartados | DEBE | estándar | — | automática (CI central) | 05-componentes §3 |
| K-02 | Un componente declarado como control (`es_control: true`) es un hook determinista o un workflow, en L3–L5 | DEBE | estándar | — | automática (esquema) | ADR-009, C9 |
| K-03 | Las transiciones de estado de un componente siguen `experimental → estable → deprecado → retirado`; `estable` exige evidencia y, con red o secretos, revisión de seguridad | DEBE | estándar | — | automática (diff de PR) | 05-componentes §5 |
| K-04 | Las skills de la instancia están en `.claude/skills/<name>/SKILL.md`, cumplen la especificación de Agent Skills y usan solo campos de su perfil | DEBE | instancia | N0+ (si hay skills) | automática | ADR-012 |
| K-05 | No existe `.agents/skills/` versionado salvo que lo genere `harness sync` sin deriva | DEBERÍA | instancia | N0+ | automática | ADR-012 |
| K-06 | Ningún hook de tipo `prompt` o `agent` se presenta como control en la política de seguridad (`harness:controles`) | DEBE | instancia | N1+ | semiautomática | ADR-009, C9 |
| K-07 | Los subagentes de revisión o verificación no declaran herramientas de escritura | DEBERÍA | instancia | N1+ | automática (frontmatter) | 05-componentes §4.2, OWASP LLM01 |
| K-08 | Los componentes instalados en una instancia coinciden con su versión del catálogo (sin deriva) | DEBERÍA | instancia | N1+ | automática | F3.5 |
| K-09 | Con `claude-code` y N1+, existe `.claude/settings.json` válido con `deny` de lectura y edición de `.env` y `.env.*` | DEBE | instancia | N1+ | automática | adapter.claude.settings |
| K-10 | `.claude/settings.json` tiene una regla `ask` o `deny` de `Edit` por cada patrón de `patrones_sensibles` | DEBE | instancia | N1+ | automática | adapter.claude.settings, ADR-013 |
| K-11 | `disableBypassPermissionsMode: "disable"`; sin `enableAllProjectMcpServers: true` ni `defaultMode` `auto`/`bypassPermissions` en el proyecto | DEBE | instancia | N1+ | automática | adaptador §3.1 |
| K-12 | Un workflow que ejecuta el agente sobre código de un PR usa `--bare --setting-sources user` y `--settings`/`--mcp-config` de fuera del PR | DEBE | instancia | N1+ | automática (lint de workflows) | adaptador §5, R-14 |
| K-13 | `manifest.adapters.agents[claude-code].min_version` ≥ versión mínima del adaptador (2.1.277) | DEBERÍA | instancia | N0+ | automática | adaptador §1 |
| K-14 | Un PR que pasa una tarea a `done` y a la vez modifica su `acceptance` se marca para revisión (aviso) | DEBERÍA | instancia | N1+ | automática (diff de PR) | skill cerrar-tarea §11 (F3.4) |
