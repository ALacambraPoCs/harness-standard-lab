# harness-example-greenfield

<!-- harness:resumen -->
Servicio de ejemplo que calcula totales de pedidos. Instancia N1 de ejemplo del Estándar de Harness 0.4.0 (repositorio de pruebas de extremo a extremo).

<!-- harness:comandos -->
## Comandos

| Rol | Comando |
|---|---|
| setup | `python3 scripts/setup.py` |
| check | `python3 -m py_compile src/app.py && python3 -m unittest discover -s tests` |
| test | `python3 -m unittest discover -s tests` |

Ejecuta `check` después de cada cambio y `test` antes de pedir revisión.

<!-- harness:restricciones -->
## Restricciones duras

- No añadas dependencias sin un ADR en [decisiones](docs/decisions/README.md).
- No leas ni escribas archivos `.env` ni credenciales.
- No declares una tarea terminada: la CI lo decide.

<!-- harness:flujo -->
## Flujo de trabajo

- Cada cambio no trivial tiene un archivo de tarea en [docs/plans/active](docs/plans/active/) y va en su propia rama y PR. El índice está en [docs/plans/INDEX.md](docs/plans/INDEX.md).
- Actualiza la sección de progreso de la tarea en cada sesión y rellena la plantilla del PR (tarea, riesgo, evidencia, sensible).
- El paso a `done` va en el PR que completa la tarea; el check `harness tasks` vuelve a ejecutar sus criterios de aceptación y bloquea el merge si alguno falla.

<!-- harness:mapa -->
## Dónde está el detalle

- Arquitectura y límites: [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Decisiones: [docs/decisions](docs/decisions/README.md)
- Seguridad y acciones que requieren aprobación: [SECURITY.md](docs/security/SECURITY.md)
