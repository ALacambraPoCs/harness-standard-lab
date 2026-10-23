---
id: T-0001
title: Redondear totales a céntimos
owner: "@ana"
status: in_progress
risk: bajo
created: 2026-10-15
acceptance:
  - id: AC1
    description: Las pruebas unitarias pasan
    check: "python3 -m unittest discover -s tests"
---

# T-0001 · Redondear totales a céntimos

<!-- harness:objetivo -->
## Objetivo
Los totales nunca muestran fracciones de céntimo.

<!-- harness:alcance -->
## Alcance
- Dentro: `src/app.py`.

<!-- harness:plan -->
## Plan
1. Añadir prueba. 2. Corregir el cálculo.

<!-- harness:progreso -->
## Progreso
- [x] 2026-10-15 10:00 — prueba añadida (quien: @ana)

<!-- harness:decisiones -->
## Decisiones
- Ninguna.
