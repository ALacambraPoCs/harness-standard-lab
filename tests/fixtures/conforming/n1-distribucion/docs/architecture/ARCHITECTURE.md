# Arquitectura

<!-- harness:vision -->
Calcula totales de pedidos para el servicio de facturación.

<!-- harness:mapa-codigo -->
- `src/app.py`: lógica de cálculo de totales (sin E/S).
- `tests/`: pruebas unitarias.

<!-- harness:limites -->
`src/` no importa nada de `tests/` ni de `scripts/`.

<!-- harness:invariantes -->
Los importes se calculan en céntimos enteros; nunca con coma flotante.
