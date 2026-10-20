# Plantilla (producto B) — estado: provisional (Fase 1)

Scaffold mínimo para una instancia **N0**. Los marcadores `{{…}}` se sustituyen al instanciar.
`harness init` llegará en la Fase 7; hasta entonces se copia a mano:

1. Copia `core/` en la raíz del repositorio.
2. Copia el contenido de cada adaptador declarado (`adapters/claude-code/`, `adapters/github/`).
3. Si ya existe un `.gitignore`, añade el contenido de `adapters/claude-code/gitignore.fragment`; si no, renómbralo a `.gitignore`.
4. Sustituye los marcadores y ejecuta `harness check --run-commands`.

Las fichas definitivas de cada archivo (contenido requerido y excluido) se publican en la Fase 2
(`standard/04-archivos/`). Autotest: `tests/test_template.py` instancia esta plantilla y exige
que supere `harness check` (criterio de aceptación del producto B).

| Marcador | Significado |
|---|---|
| `{{PROJECT_NAME}}` | Nombre del proyecto (minúsculas, guiones) |
| `{{PROJECT_SUMMARY}}` | Una frase: qué es y para qué sirve |
| `{{OWNER}}` | Equipo propietario de GitHub (`@org/equipo`) |
| `{{KIND}}` | service, library, application, infrastructure, monorepo u other |
| `{{SETUP}}`, `{{CHECK}}`, `{{TEST}}` | Invocaciones del contrato de comandos (ADR-006) |
| `{{HARNESS_OWNERS}}`, `{{SECURITY_OWNERS}}`, `{{PLATFORM_OWNERS}}` | Equipos de GitHub para rutas sensibles (ADR-013) |
| `{{CLI_REF}}` | Tag de la CLI, p. ej. `cli-v0.1.1` |
| `{{STANDARD_REPO}}` | `owner/harness-standard` |
