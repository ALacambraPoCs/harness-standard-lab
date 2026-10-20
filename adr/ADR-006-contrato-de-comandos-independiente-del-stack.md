---
id: ADR-006
titulo: "Contrato de comandos independiente del stack"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-006 · Contrato de comandos independiente del stack [APROBADO 2026-10-19]

**Recomendación**
- El estándar define **roles de comando**:
  - Obligatorios: `setup`, `check` (rápido: lint, tipos y tests unitarios) y `test`.
  - Condicionales: `e2e`, `build`, `dev`, `clean`.
- El manifiesto declara cómo se invoca cada uno: Make, just o scripts del gestor de paquetes.
- Cada comando debe:
  - ser idempotente;
  - no ser interactivo;
  - devolver un código de salida significativo;
  - imprimir errores en formato orientado a remedio.

**Justificación**
- Es la pieza portable más repetida en el corpus (`make setup|test|check`, `init.sh`).
- Hace que AGENTS.md, la CI y la CLI usen exactamente los mismos comandos.

**Alternativas**
- Exigir `init.sh` o un Makefile concreto: impone herramientas a stacks que ya tienen las suyas.

**Riesgos**
- En monorepos, los comandos pueden depender del segmento.
- El contrato debe admitir comandos por segmento (Fase 4).

**Evidencia**
- S-LHE L02, L03, L06.
- S-OAI-HE p.3: la aplicación se puede arrancar en cada worktree.

**Validación**
- Regla de ejecución en CI: `setup` y `check` terminan con código 0 en un runner limpio.
