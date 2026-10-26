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

<!-- harness:flujo -->
## Flujo de trabajo

- Cada cambio no trivial tiene un archivo de tarea en `docs/plans/active/` (N1) y va en su propia rama y PR.
- Actualiza la sección de progreso de la tarea en cada sesión; la plantilla de PR indica tarea, riesgo y evidencia.
- El paso a `done` va en el PR que completa la tarea y lo verifica la CI, que vuelve a ejecutar los criterios de aceptación.
- **Para y pide decisión a la persona** si: un comando del que depende el siguiente paso falla; un permiso bloquea algo necesario (no busques rodeos como `gh api` o `sh -c`); un criterio de aceptación parece incorrecto; el verificador o el mismo check de CI fallan dos veces seguidas; o se detecta un secreto. Si el cambio toca workflows, CODEOWNERS o `.harness/`, avisa de que es riesgo alto y necesita la puerta de aprobación.

<!-- harness:mapa -->
## Dónde está el detalle

- [Arquitectura y límites](docs/architecture/ARCHITECTURE.md): antes de tocar más de un módulo.
- [Decisiones](docs/decisions/README.md): antes de cambiar un patrón establecido.
- [Seguridad](docs/security/SECURITY.md): antes de tocar autenticación, datos, secretos o integraciones.
