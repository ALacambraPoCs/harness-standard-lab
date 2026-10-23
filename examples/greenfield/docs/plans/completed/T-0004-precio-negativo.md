---
id: T-0004
title: Rechazar precios negativos en total()
owner: "@AlbertoLacambra"
status: done
done_pr: 10
risk: bajo
created: 2026-10-22
issue: 8
acceptance:
  - id: AC1
    description: total() lanza ValueError indicando la línea si un precio es negativo
    check: "python3 -m unittest tests.test_app.TotalTest.test_precio_negativo"
  - id: AC2
    description: Las pruebas existentes siguen pasando
    check: "python3 -m unittest discover -s tests"
---

# T-0004 · Rechazar precios negativos en total()

<!-- harness:objetivo -->
## Objetivo
Un pedido con un precio unitario negativo no produce un total: `total()` lo rechaza con `ValueError` y un mensaje que indica la línea, igual que con las cantidades (T-0002).

<!-- harness:alcance -->
## Alcance
- Dentro: `src/app.py` y `tests/test_app.py`.
- Fuera de alcance: descuentos (se modelarán aparte).

<!-- harness:plan -->
## Plan
1. Añadir la prueba `test_precio_negativo`.
2. Validar los precios en `total()`.
3. Verificar con el subagente `verificador` y cerrar con la skill `cerrar-tarea`.

<!-- harness:progreso -->
## Progreso
- [x] Añadir la prueba `test_precio_negativo` (tests/test_app.py)
- [x] Validar precios negativos en `total()` con `ValueError` que indica la línea (src/app.py)
- [x] `check` pasa: py_compile + `unittest discover -s tests` (3 pruebas OK)
- [x] Verificar con `verificador` y cerrar con `cerrar-tarea` (en el PR)
- 2026-10-23 — cerrada en el PR #10

<!-- harness:decisiones -->
## Decisiones
- 2026-10-22 — AC1 nombra la prueba exacta antes de implementar — @AlbertoLacambra

<!-- harness:resultado -->
## Resultado
Logrado: `total()` rechaza precios negativos con `ValueError("Precio negativo en la línea N: p")`, igual que las cantidades (T-0002). Añadida `test_precio_negativo`. AC1 y AC2 pasan en local (verificador, código 0).

Pendiente: nada dentro del alcance. Los descuentos quedan fuera (se modelarán aparte).
