---
id: T-0005
title: Adoptar el estándar 0.5.0 y los componentes ajustados
owner: "@AlbertoLacambra"
status: done
done_pr: 15
risk: medio
created: 2026-10-24
acceptance:
  - id: AC1
    description: La instancia cumple N1 del estándar 0.5.0 sin errores ni avisos (incluye HS-SEC-010…012 y la deriva de componentes)
    check: "harness check --strict"
  - id: AC2
    description: El índice de tareas está al día
    check: "harness tasks index --check"
---

# T-0005 · Adoptar el estándar 0.5.0 y los componentes ajustados

<!-- harness:objetivo -->
## Objetivo
El repositorio declara el estándar 0.5.0: `settings.json` endurecido (sin modo automático, reglas de `gh`, `allow` para los comandos del contrato sin efectos) y los componentes del catálogo en sus versiones nuevas (hook 0.3.0, verificador 0.2.0, skill 0.2.0).

<!-- harness:alcance -->
## Alcance
- Dentro: manifiesto, `.claude/`, `.harness/components.lock` y workflows.
- Fuera de alcance: `src/`.

<!-- harness:plan -->
## Plan
1. PR de adopción (este), con `harness components sync`.
2. Validar en una sesión real de Claude Code con T-0006 (validación de la F3.7).
3. Cerrar con `cerrar-tarea` 0.2.0.

<!-- harness:progreso -->
## Progreso
- 2026-10-24 — componentes actualizados con `harness components sync` y `settings.json` alineado con la plantilla 0.5.0 — Claude a nombre de @AlbertoLacambra
- 2026-10-24 — cerrada en el PR #15 — @AlbertoLacambra

<!-- harness:decisiones -->
## Decisiones
- 2026-10-24 — No se añaden a `allow` los comandos `check` y `test` de la instancia (D-043): ejecutarían sin confirmación código escrito por el agente — Claude

<!-- harness:resultado -->
## Resultado
Estándar 0.5.0 adoptado en N1: check --strict sin errores ni avisos (61 reglas, 17 omitidas), settings.json alineado con la plantilla 0.5.0 y componentes actualizados con harness components sync. Pendiente: la validación en una sesión real de Claude Code con T-0006 (validación de la F3.7), que queda fuera de este cierre.
