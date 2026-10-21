<!-- Ejemplo canónico de AGENTS.md de segmento (ficha standard/04-archivos/instructions.segment.md).
     Ubicación real en una instancia: billing/AGENTS.md, acompañado de billing/CLAUDE.md con "@AGENTS.md"
     si se usa el adaptador claude-code. -->
<!-- harness:ambito -->
# billing/ · Facturación
Cálculo de facturas y notas de crédito. Propietario: @org/billing.

<!-- harness:comandos -->
| Rol | Comando |
|---|---|
| test | `make test PKG=billing` |

<!-- harness:limites -->
- Puede depender de `shared/` y `ledger/api`. No importa nada de `payments/` (usa eventos).

<!-- harness:restricciones -->
- Los importes son `Decimal`; nunca `float` (lo comprueba `make check`).
