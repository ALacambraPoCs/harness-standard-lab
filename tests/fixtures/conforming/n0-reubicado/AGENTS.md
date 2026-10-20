# ejemplo-reubicado

Servicio de ejemplo que calcula totales de pedidos. Instancia N0 del Estándar de Harness.

## Comandos

| Rol | Comando |
|---|---|
| setup | `python3 scripts/setup.py` |
| check | `python3 -m py_compile src/app.py` |
| test | `python3 -m unittest discover -s tests` |

Ejecuta `check` después de cada cambio y `test` antes de pedir revisión.

## Restricciones duras

- No añadas dependencias sin un ADR en [decisiones](docs/adr/README.md).
- No leas ni escribas archivos `.env` ni credenciales.
- No declares una tarea terminada: la CI lo decide.

## Dónde está el detalle

- Arquitectura y límites: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Decisiones: [docs/adr](docs/adr/README.md)
- Seguridad: ver la política de seguridad en la raíz del repositorio.
