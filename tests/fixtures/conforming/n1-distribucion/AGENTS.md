# ejemplo-n1

<!-- harness:resumen -->
Servicio de ejemplo que calcula totales de pedidos. Instancia N1 del Estándar de Harness.

<!-- harness:comandos -->
## Comandos

| Rol | Comando |
|---|---|
| setup | `python3 scripts/setup.py` |
| check | `python3 -m py_compile src/app.py` |
| test | `python3 -m unittest discover -s tests` |

Ejecuta `check` después de cada cambio y `test` antes de pedir revisión.

<!-- harness:restricciones -->
## Restricciones duras

- No añadas dependencias sin un ADR en [decisiones](docs/decisions/README.md).
- No leas ni escribas archivos `.env` ni credenciales.
- No declares una tarea terminada: la CI lo decide.

<!-- harness:flujo -->
## Flujo de trabajo

- Cada cambio no trivial tiene una tarea en [docs/plans/active](docs/plans/active/) y va en su propia rama y PR.
- Actualiza `Progreso` de la tarea en cada sesión. El paso a `done` lo verifica la CI en el PR.

<!-- harness:mapa -->
## Dónde está el detalle

- Arquitectura y límites: [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Decisiones: [docs/decisions](docs/decisions/README.md)
- Seguridad y acciones que requieren aprobación: [SECURITY.md](docs/security/SECURITY.md)
