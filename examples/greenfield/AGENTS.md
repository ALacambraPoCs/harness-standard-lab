# harness-example-greenfield

Servicio de ejemplo que calcula totales de pedidos. Instancia N0 de ejemplo del Estándar de Harness (repositorio de pruebas de extremo a extremo).

## Comandos

| Rol | Comando |
|---|---|
| setup | `python3 scripts/setup.py` |
| check | `python3 -m py_compile src/app.py` |
| test | `python3 -m unittest discover -s tests` |

Ejecuta `check` después de cada cambio y `test` antes de pedir revisión.

## Restricciones duras

- No añadas dependencias sin un ADR en [decisiones](docs/decisions/README.md).
- No leas ni escribas archivos `.env` ni credenciales.
- No declares una tarea terminada: la CI lo decide.

## Dónde está el detalle

- Arquitectura y límites: [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Decisiones: [docs/decisions](docs/decisions/README.md)
- Seguridad y acciones que requieren aprobación: [SECURITY.md](docs/security/SECURITY.md)
