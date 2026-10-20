---
id: ADR-013
titulo: "La configuración de agentes es código sensible"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-013 · La configuración de agentes es código sensible [APROBADO 2026-10-19]

**Recomendación**
- `CODEOWNERS` con un propietario de seguridad o plataforma sobre:
  - `AGENTS.md` y todos los `**/AGENTS.md`;
  - `CLAUDE.md`;
  - `.claude/**`, `.agents/**`, `.mcp.json`, `.harness/**`;
  - `.github/workflows/**` y `.github/CODEOWNERS`.
- En CI, los agentes se ejecutan con `claude -p --bare` y configuración explícita.
- El job del agente tiene permisos `contents: read`. Los cambios se aplican en un job separado sin credenciales del modelo, siguiendo el patrón documentado por `openai/codex-action`.
- Los secretos se pasan solo al paso que los necesita.

**Justificación**
- S-VILA p.29: CVE por ejecución previa a la confianza.
- S-CC-SET: `-p` sin `--bare` ejecuta hooks y `.mcp.json` en carpetas no confiables.
- Copilot code review lee las instrucciones de la rama del PR, lo que permite a un PR modificar las reglas que revisan ese mismo PR.
- S-MCP: las descripciones de herramientas no son confiables.

**Riesgos**
- Fricción al cambiar instrucciones.
- Mitigación: propietarios por segmento para los `AGENTS.md` locales.

**Validación**
- Regla de la CLI: CODEOWNERS cubre todas las rutas sensibles.
- Revisión del workflow con un linter de Actions. La herramienta concreta se decide en la Fase 5.
