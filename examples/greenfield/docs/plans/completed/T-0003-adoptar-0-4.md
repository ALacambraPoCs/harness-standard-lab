---
id: T-0003
title: Adoptar el estándar 0.4.0 y los componentes del catálogo
owner: "@AlbertoLacambra"
status: done
done_pr: 11
risk: medio
created: 2026-10-22
acceptance:
  - id: AC1
    description: La instancia cumple N1 del estándar 0.4.0 sin errores ni avisos (incluye la deriva de componentes)
    check: "harness check --strict"
  - id: AC2
    description: El índice de tareas está al día
    check: "harness tasks index --check"
---

# T-0003 · Adoptar el estándar 0.4.0 y los componentes del catálogo

<!-- harness:objetivo -->
## Objetivo
El repositorio declara el estándar 0.4.0 y usa los componentes del catálogo (hook verificar-al-terminar, subagente verificador, skill cerrar-tarea) con la configuración deny-first de Claude Code.

<!-- harness:alcance -->
## Alcance
- Dentro: manifiesto, AGENTS.md, `.claude/`, `.harness/components.lock` y workflows.
- Fuera de alcance: `src/`.

<!-- harness:plan -->
## Plan
1. PR de adopción (este).
2. Probar en una sesión real de Claude Code (F3.6).
3. Cerrar con la skill `cerrar-tarea`.

<!-- harness:progreso -->
## Progreso
- [x] 2026-10-22 — componentes instalados con `harness components add` (quien: Claude a nombre de @AlbertoLacambra)
- [x] 2026-10-23 — cerrada en el PR de cierre (ver `done_pr`)

<!-- harness:decisiones -->
## Decisiones
- 2026-10-22 — `check` pasa a incluir las pruebas unitarias, para que el hook `verificar-al-terminar` detecte comportamiento roto y no solo errores de sintaxis — Claude

<!-- harness:resultado -->
## Resultado
Logrado: el repositorio declara el estándar 0.4.0 en N1 y usa los componentes del catálogo (hook verificar-al-terminar, subagente verificador, skill cerrar-tarea) con la configuración deny-first de Claude Code. `harness check --strict` pasa sin errores ni avisos (58 reglas ejecutadas, 17 omitidas) y el índice está al día.

Pendiente: probar los componentes en una sesión real de Claude Code (plan F3.6), fuera del alcance de este PR.
