# {{PROJECT_NAME}}

{{PROJECT_SUMMARY}}

## Comandos

| Rol | Comando |
|---|---|
| setup | `{{SETUP}}` |
| check | `{{CHECK}}` |
| test | `{{TEST}}` |

Ejecuta `check` después de cada cambio y `test` antes de pedir revisión.

## Restricciones duras

- No declares una tarea terminada: la CI lo decide con evidencia.
- No leas, muestres ni escribas secretos ni archivos `.env`.
- Toda decisión de arquitectura nueva se registra en [decisiones](docs/decisions/README.md).

## Dónde está el detalle

- Arquitectura y límites: [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Decisiones: [docs/decisions](docs/decisions/README.md)
- Seguridad y acciones que requieren aprobación: [SECURITY.md](docs/security/SECURITY.md)
