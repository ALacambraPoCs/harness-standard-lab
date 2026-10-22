---
id: T-0002
title: Rechazar cantidades negativas en total()
owner: "@AlbertoLacambra"
status: done
risk: bajo
created: 2026-10-21
issue: 4
done_pr: 7
acceptance:
  - id: AC1
    description: total() lanza ValueError si una línea tiene cantidad negativa
    check: "python3 -m unittest tests.test_app.TotalTest.test_cantidad_negativa"
  - id: AC2
    description: Las pruebas existentes siguen pasando
    check: "python3 -m unittest discover -s tests"
---

# T-0002 · Rechazar cantidades negativas en total()

<!-- harness:objetivo -->
## Objetivo
Un pedido con una cantidad negativa no produce un total: `total()` lo rechaza con `ValueError` y un mensaje que indica la línea.

<!-- harness:alcance -->
## Alcance
- Dentro: `src/app.py` y `tests/test_app.py`.
- Fuera de alcance: precios negativos (descuentos).

<!-- harness:plan -->
## Plan
1. Añadir la prueba `test_cantidad_negativa`.
2. Validar las cantidades en `total()`.

<!-- harness:progreso -->
## Progreso
- [x] 2026-10-21 — se empieza la tarea (quien: @AlbertoLacambra)
- [x] 2026-10-21 — prueba `test_cantidad_negativa` añadida; se declara done antes de implementar (prueba de ADR-016): el check `harness tasks` falla y bloquea el merge
- [x] 2026-10-21 — validación implementada en `total()`; AC1 y AC2 pasan

<!-- harness:decisiones -->
## Decisiones
- 2026-10-21 — El criterio AC1 se fija antes de implementar: nombra la prueba exacta que debe existir y pasar — @AlbertoLacambra

<!-- harness:resultado -->
## Resultado
`total()` rechaza cantidades negativas con `ValueError` indicando la línea. Pendiente: precios negativos (fuera de alcance).
