---
id: T-0006
title: Descuento porcentual en total()
owner: "@AlbertoLacambra"
status: done
done_pr: 14
risk: bajo
created: 2026-10-24
issue: 12
acceptance:
  - id: AC1
    description: total() aplica un descuento porcentual opcional y rechaza valores fuera de 0–100 con ValueError
    check: "python3 -m unittest tests.test_app.TotalTest.test_descuento"
  - id: AC2
    description: Las pruebas existentes siguen pasando
    check: "python3 -m unittest discover -s tests"
---

# T-0006 · Descuento porcentual en total()

<!-- harness:objetivo -->
## Objetivo
`total(lines, descuento=0)` aplica un descuento porcentual sobre la suma (0 por defecto) y redondea a 2 decimales. Un descuento menor que 0 o mayor que 100 lanza `ValueError`.

<!-- harness:alcance -->
## Alcance
- Dentro: `src/app.py` y `tests/test_app.py`.
- Fuera de alcance: descuentos por línea e impuestos.

<!-- harness:plan -->
## Plan
1. Añadir la prueba `test_descuento` (casos válidos y fuera de rango).
2. Implementar el parámetro `descuento`.
3. Verificar con el subagente `verificador` y cerrar con la skill `cerrar-tarea`.

<!-- harness:progreso -->
## Progreso
- 2026-10-24 — Añadida `test_descuento` en `tests/test_app.py` (casos válidos 0/10/100, redondeo y −1/101 → `ValueError`). Sin implementar: falla con `TypeError` porque `total()` aún no acepta `descuento`. AC1 y AC2 pendientes.
- 2026-10-24 — Implementado `descuento` en `total()` (`src/app.py`): valida 0–100 con `ValueError`, aplica el porcentaje sobre el subtotal y redondea a 2 decimales. Local: `check` y `test` en verde (4 pruebas). AC1 y AC2 pasan localmente; la tarea sigue `in_progress` hasta el PR de cierre.
- 2026-10-24 — cerrada en el PR #14 — @AlbertoLacambra

<!-- harness:decisiones -->
## Decisiones
- 2026-10-24 — AC1 nombra la prueba exacta antes de implementar — @AlbertoLacambra

<!-- harness:resultado -->
## Resultado
total(lines, descuento=0) aplica el descuento porcentual 0–100 sobre el subtotal, redondea a 2 decimales y lanza ValueError fuera de rango. Pendiente: nada dentro de alcance; descuentos por línea e impuestos quedan fuera de alcance.
