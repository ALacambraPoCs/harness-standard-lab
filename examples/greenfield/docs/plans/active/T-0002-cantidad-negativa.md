---
id: T-0002
title: Rechazar cantidades negativas en total()
owner: "@AlbertoLacambra"
status: ready
risk: bajo
created: 2026-10-21
issue: 4
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
- [ ] (pendiente)

<!-- harness:decisiones -->
## Decisiones
- 2026-10-21 — El criterio AC1 se fija antes de implementar: nombra la prueba exacta que debe existir y pasar — @AlbertoLacambra

<!-- harness:resultado -->
## Resultado
(Se rellena al pasar a done.)
