# Arquitectura

<!-- harness:vision -->
## Visión
Servicio mínimo que calcula el total de un pedido a partir de sus líneas (cantidad × precio).

<!-- harness:mapa-codigo -->
## Mapa del código
- `src/app.py`: lógica de cálculo de totales (sin E/S).
- `tests/`: pruebas unitarias.
- `scripts/setup.py`: preparación del entorno.

<!-- harness:limites -->
## Límites
- `src/` no importa nada de `tests/` ni de `scripts/`.

<!-- harness:invariantes -->
## Invariantes
- `total()` redondea a 2 decimales y nunca hace E/S.
