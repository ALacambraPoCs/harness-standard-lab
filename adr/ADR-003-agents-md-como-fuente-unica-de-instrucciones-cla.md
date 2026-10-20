---
id: ADR-003
titulo: "AGENTS.md como fuente única de instrucciones; CLAUDE.md como adaptador fino"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-003 · AGENTS.md como fuente única de instrucciones; CLAUDE.md como adaptador fino [APROBADO 2026-10-19]

**Recomendación**
- El núcleo usa `AGENTS.md`, en la raíz y anidado por segmento.
- El adaptador de Claude Code es un `CLAUDE.md` que contiene `@AGENTS.md` más únicamente lo que es exclusivo de Claude Code, por ejemplo cómo usar sus subagentes.
- Se prohíbe duplicar contenido entre ambos archivos.

**Justificación**
- Según S-CC-MEM (verificado el 19-10-2026), Claude Code solo lee `AGENTS.md` de forma nativa si no existe ningún `CLAUDE.md`, `.claude/CLAUDE.md` o `CLAUDE.local.md`.
- Por tanto, un desarrollador que cree su `CLAUDE.local.md` personal desactiva sin darse cuenta la lectura de `AGENTS.md`.
- El import `@AGENTS.md` funciona con cualquier configuración y es la alternativa portable que documenta Claude Code.
- AGENTS.md lo leen también Codex, Copilot y Cursor (S-AGENTSMD), lo que deja abierta la puerta a futuros adaptadores.

**Alternativas**
- (a) Solo `CLAUDE.md`: ata el núcleo a un proveedor.
- (b) Lectura nativa sin `CLAUDE.md`: frágil, por el problema de `CLAUDE.local.md`.
- (c) Symlink: la documentación de Claude Code lo desaconseja con Windows, y el usuario trabaja en Windows.
- (d) Contenido duplicado, como en las plantillas del curso: provoca contradicciones (C3).

**Riesgos**
- El límite de 4 saltos de `@import` (S-CC-MEM).
- Los imports no ahorran contexto, porque se cargan al arrancar.
- Hay que vigilar el tamaño total: regla de presupuesto en ADR-009.

**Evidencia**
- S-CC-MEM, secciones "AGENTS.md" e "Import additional files".
- S-AGENTSMD.
- S-OAI-HE p.5.

**Validación**
- Regla de la CLI: `CLAUDE.md` contiene `@AGENTS.md` y no repite secciones del núcleo.
- Prueba manual en Claude Code: en una sesión interactiva se ve la línea de carga de instrucciones.
