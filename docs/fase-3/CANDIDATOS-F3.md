---
documento: F3-CANDIDATOS
titulo: Requisitos candidatos de la Fase 3 (componentes y adaptador de Claude Code)
estado: lista viva
actualizado: 2026-10-22 (F3.1)
---

# Requisitos candidatos de la F3

No son normativos. Se formalizan (ID, regla y fixtures) en F3.3 y se aprueban con ella.

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
