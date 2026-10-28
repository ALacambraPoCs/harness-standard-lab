# Plataforma: rulesets y environments de referencia (F5.3, ADR-010 rev. 2)

Configuración de GitHub que exige cada nivel. **No se aplica sola:** la crea una persona administradora (o IaC) y `harness platform check` (HS-CI-006) comprueba que existe.

| Archivo | Dónde | Qué |
|---|---|---|
| `ruleset-n1.json` | Instancia, rama por defecto | PR obligatorio, checks requeridos (conformidad, tareas, puerta de riesgo alto), sin force push ni borrado. **0 aprobaciones** (D-056: un único mantenedor no puede aprobar su propio PR) |
| `ruleset-n2.json` | Instancia, rama por defecto | N1 + 1 aprobación, Code Owners y aprobación del último push por otra persona |
| `ruleset-tags-estandar.json` | Repositorio del estándar | Los tags `cli-v*` no se pueden borrar, mover ni actualizar (las instancias fijan los workflows reutilizables a ellos, `ci.pinned`) |

**Environment `aprobacion-riesgo-alto`** (puerta de ADR-010 rev. 2), en Settings → Environments:
- *Required reviewers*: al menos una persona. En el laboratorio, el mantenedor con *Prevent self-review* desactivado; en equipos, plataforma o seguridad con *Prevent self-review* activado (N2+).
- *Deployment branches and tags*: sin restricción (el job se ejecuta desde ramas de PR).
- Crearlo **antes** de usar el estándar 0.6.0+: si un workflow lo referencia y no existe, GitHub lo crea sin protección.

## Lo verificado y lo pendiente

- Verificado (docs.github.com, 2026-10-28): los nombres de los parámetros de `pull_request` y `required_status_checks` y los tipos de regla `deletion` y `non_fast_forward` (REST, «Create a repository ruleset»; «Available rules for rulesets»).
- **No verificado:** que GitHub acepte estos archivos en «Import a ruleset», el valor especial `~DEFAULT_BRANCH`, el tipo `update` para tags y el `context` exacto de los checks de un workflow reutilizable (`<job que llama> / <job llamado>`). `harness platform check` compara los checks por sufijo (`… / harness check`), así que tolera la diferencia de prefijo. Se comprueba en F5.7.
