---
id: T-0001
title: Adoptar el nivel N1 del estándar 0.2.0
owner: "@AlbertoLacambra"
status: in_progress
risk: medio
created: 2026-10-21
acceptance:
  - id: AC1
    description: La instancia cumple N1 sin errores ni avisos
    check: "harness check --strict"
  - id: AC2
    description: El índice de tareas está al día
    check: "harness tasks index --check"
---

# T-0001 · Adoptar el nivel N1 del estándar 0.2.0

<!-- harness:objetivo -->
## Objetivo
El repositorio pasa de N0 a N1: el trabajo se gestiona con archivos de tarea y `done` lo verifica la CI (ADR-016).

<!-- harness:alcance -->
## Alcance
- Dentro: manifiesto, AGENTS.md, ADR-0001, arquitectura, seguridad, plantilla de PR, `docs/plans/` y workflows.
- Fuera de alcance: cambios en `src/`.
- No tocar: el contrato de comandos.

<!-- harness:plan -->
## Plan
1. PR de adopción con la estructura N1 y las tareas T-0001 y T-0002.
2. Añadir `tasks / harness tasks` como check requerido en el ruleset.
3. PR que pasa T-0001 a done.

<!-- harness:progreso -->
## Progreso
- [x] 2026-10-21 — estructura N1 preparada (quien: Claude a nombre de @AlbertoLacambra)

<!-- harness:decisiones -->
## Decisiones
- 2026-10-21 — Se elimina el secreto `HARNESS_STANDARD_TOKEN` del workflow: los repositorios son públicos (D-018) — Claude

<!-- harness:resultado -->
## Resultado
(Se rellena al pasar a done.)
