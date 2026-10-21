# {{PROJECT_NAME}}

<!-- harness:resumen -->
{{PROJECT_SUMMARY}}

<!-- harness:comandos -->
## Comandos

| Rol | Comando | Cuándo |
|---|---|---|
| setup | `{{SETUP}}` | Al clonar o tras cambiar dependencias |
| check | `{{CHECK}}` | Después de cada cambio |
| test | `{{TEST}}` | Antes de pedir revisión |

<!-- harness:restricciones -->
## Restricciones duras

- No declares una tarea terminada: la CI lo decide con evidencia.
- No leas, muestres ni escribas secretos ni archivos `.env`.
- Toda decisión de arquitectura nueva se registra en [decisiones](docs/decisions/README.md).

<!-- harness:mapa -->
## Dónde está el detalle

- [Arquitectura y límites](docs/architecture/ARCHITECTURE.md): antes de tocar más de un módulo.
- [Decisiones](docs/decisions/README.md): antes de cambiar un patrón establecido.
- [Seguridad](docs/security/SECURITY.md): antes de tocar autenticación, datos, secretos o integraciones.
