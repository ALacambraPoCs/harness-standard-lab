---
id: ADR-012
titulo: "Skills: fuente neutra en `.agents/skills/` y copia generada en `.claude/skills/`"
estado: propuesto
fecha: 2026-10-19
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-012 · Skills: fuente neutra en `.agents/skills/` y copia generada en `.claude/skills/` [Fase 3, recomendación provisional]

**Recomendación**
- Las skills del núcleo se escriben con **solo los seis campos** de Agent Skills y viven en `.agents/skills/`.
- `harness sync` genera `.claude/skills/` (copia, no symlink, por Windows).
- La CI comprueba que no hay deriva entre ambas.
- Las extensiones exclusivas de Claude Code (`context: fork`, `paths`, etc.) solo se permiten en skills marcadas como de adaptador.

**Justificación**
- S-CC-SKILLS (verificado): Claude Code **no lee** `.agents/skills/`.
- Codex, Copilot y Cursor sí la leen (informe de especificaciones oficiales).
- Los campos extra de Claude producen error fuera de Claude Code (S-CC-SKILLS).

**Alternativa**
- En la v1 (solo Claude Code), escribir directamente en `.claude/skills/` limitándose a los campos de la especificación. Es más simple hoy, pero obliga a migrar cuando llegue el segundo adaptador.
- **Decisión pendiente:** simplicidad hoy frente a portabilidad mañana.

**Validación**
- `skills-ref validate` (S-SKILLS) en CI sobre `.agents/skills/`.
