# Plantilla (producto B) — estado: provisional (Fase 2)

Scaffold para una instancia **N0** o **N1** del estándar 0.2.0. Los marcadores `{{…}}` se sustituyen al instanciar.
`harness init` llegará en la Fase 7; hasta entonces se copia a mano:

1. Copia `core/` en la raíz del repositorio.
2. Copia el contenido de cada adaptador declarado (`adapters/claude-code/`, que incluye `.claude/settings.json` deny-first, y `adapters/github/`). Inicia Claude Code siempre en la raíz del repositorio: las reglas `/…` se anclan ahí.
3. Si ya existe un `.gitignore`, añade el contenido de `adapters/claude-code/gitignore.fragment`; si no, renómbralo a `.gitignore`.
4. **Solo N1:** copia también `niveles/n1/` (estructura de tareas y workflow `harness-tasks.yml`), marca `harness tasks` como check requerido en el ruleset (HS-CI-003) y ejecuta `harness tasks index --write`.
5. Sustituye los marcadores y ejecuta `harness check --run-commands`.

Las fichas de cada archivo (contenido requerido y excluido) están en `standard/04-archivos/`. Autotest: `tests/test_template.py` instancia esta plantilla y exige
que supere `harness check` (criterio de aceptación del producto B), en N0 y en N1.

| Marcador | Significado |
|---|---|
| `{{LEVEL}}` | `N0` o `N1` |
| `{{DOCS_LANGUAGE}}` | Idioma de la documentación (`es`, `en`…; D-020) |
| `{{DATE}}` | Fecha de adopción `AAAA-MM-DD` |
| `{{PROJECT_NAME}}` | Nombre del proyecto (minúsculas, guiones) |
| `{{PROJECT_SUMMARY}}` | Una frase: qué es y para qué sirve |
| `{{OWNER}}` | Equipo propietario de GitHub (`@org/equipo`) |
| `{{KIND}}` | service, library, application, infrastructure, monorepo u other |
| `{{SETUP}}`, `{{CHECK}}`, `{{TEST}}` | Invocaciones del contrato de comandos (ADR-006) |
| `{{HARNESS_OWNERS}}`, `{{SECURITY_OWNERS}}`, `{{PLATFORM_OWNERS}}` | Equipos de GitHub para rutas sensibles (ADR-013) |
| `{{CLI_REF}}` | Tag de la CLI, p. ej. `cli-v0.8.0-rc.1` |
| `{{STANDARD_REPO}}` | `owner/harness-standard` |
