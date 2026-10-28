# Plataforma: rulesets y environments de referencia (F5.3, ADR-010 rev. 2)

Configuración de GitHub y de Claude Code a nivel de organización que exige cada nivel. **No se aplica sola:** la crea una persona administradora (o IaC) y `harness platform check` (HS-CI-006) comprueba que existe.

| Archivo | Dónde | Qué |
|---|---|---|
| `ruleset-n1.json` | Instancia, rama por defecto | PR obligatorio, checks requeridos (conformidad, tareas, puerta de riesgo alto), sin force push ni borrado. **0 aprobaciones** (D-056: un único mantenedor no puede aprobar su propio PR) |
| `ruleset-n2.json` | Instancia, rama por defecto | N1 + 1 aprobación, Code Owners y aprobación del último push por otra persona |
| `managed-settings.json` | Equipos (consola de claude.ai o `/etc/claude-code/`) | Configuración gestionada de Claude Code (F5.5-B, D-068): modos desactivados, `deny` universales y sandbox con dominios bloqueados a la lista gestionada. **En WSL, `/etc/claude-code` puede ser escribible por el usuario: preferir la configuración desde servidor** |
| `token-agente.md` | Cada persona | Token fine-grained de mínimo privilegio para el agente (F5.5-C, D-069) |
| `ruleset-tags-estandar.json` | Repositorio del estándar | Los tags `cli-v*` no se pueden borrar, mover ni actualizar (las instancias fijan los workflows reutilizables a ellos, `ci.pinned`) |

**Environment `aprobacion-riesgo-alto`** (puerta de ADR-010 rev. 2), en Settings → Environments:
- *Required reviewers*: al menos una persona. En el laboratorio, el mantenedor con *Prevent self-review* desactivado; en equipos, plataforma o seguridad con *Prevent self-review* activado (N2+).
- *Deployment branches and tags*: sin restricción (el job se ejecuta desde ramas de PR).
- Crearlo **antes** de usar el estándar 0.6.0+: si un workflow lo referencia y no existe, GitHub lo crea sin protección.

## Lo verificado y lo pendiente

- Verificado (docs.github.com, 2026-10-28): los nombres de los parámetros de `pull_request` y `required_status_checks` y los tipos de regla `deletion` y `non_fast_forward` (REST, «Create a repository ruleset»; «Available rules for rulesets»).
- **No verificado:** que GitHub acepte estos archivos en «Import a ruleset», el valor especial `~DEFAULT_BRANCH` y el tipo `update` para tags. Se comprueba en F5.7.
- **Verificado en el laboratorio (E-025, 2026-10-28):** el `context` de un check de workflow reutilizable es `<job que llama> / <job llamado>` (`conformance / harness check`, `tasks / harness tasks`), como en `ruleset-n1.json`; `harness platform check` en N1 da 0 errores contra `harness-example-greenfield`.
