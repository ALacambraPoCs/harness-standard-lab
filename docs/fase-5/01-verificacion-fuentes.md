---
documento: F5-01
titulo: F5.1 · Verificación de fuentes (GitHub y Claude Code)
estado: aprobado (D-057)
fecha: 2026-10-26
---

# F5.1 · Verificación de fuentes

Leídas el 2026-10-26 en docs.github.com, code.claude.com/docs y github.com/anthropics/claude-code-action.

**Estado de cada hecho:**
- **M** = verificado a mano (cita leída en esta sesión).
- **S** = verificado por un subagente con cita y URL, sin revisión a mano (R-08: se revisa a mano antes de normarlo).
- **NV** = no verificado.

## 1. GitHub (organización Free, repositorios públicos)

| # | Hecho | Estado | Fuente |
|---|---|---|---|
| G1 | Rulesets de repositorio disponibles en repos públicos con Free for organizations. Los rulesets de **organización** y los *push rulesets* requieren Team o Enterprise | S | about-rulesets |
| G2 | Reglas disponibles: PR obligatorio, aprobaciones, descartar aprobaciones obsoletas, revisión de Code Owners, aprobación del último push por otra persona, checks requeridos, bloquear force push y borrado, commits firmados | S | available-rules-for-rulesets |
| G3 | **«Pull request authors cannot approve their own pull requests.»** | **M** | approving-a-pull-request-with-required-reviews |
| G4 | Bypass por actor (admins, roles, equipos, Apps), con la opción «For pull requests only» | S | creating-rulesets-for-a-repository#granting-bypass-permissions |
| G5 | Merge queue: «available in any public repository owned by an organization». **Exige el evento `merge_group`** en los workflows de los checks requeridos | **M** | managing-a-merge-queue |
| G6 | API: `GET /repos/{o}/{r}/rules/branches/{branch}` (reglas activas), `/rulesets` y `/rulesets/{id}`. En repos públicos funcionan sin autenticación. `bypass_actors` solo se devuelve con acceso de escritura | S | rest/repos/rules |
| G7 | Environments en Free con repos públicos: revisores obligatorios (con «Prevent self-review» opcional), temporizador, ramas permitidas y secretos de environment. **Por defecto, los admins pueden saltarse las reglas**; se puede desactivar | S | deployments-and-environments |
| G8 | Un workflow reutilizable **solo puede reducir** los permisos de `GITHUB_TOKEN`, nunca ampliarlos | S | reusing-workflow-configurations |
| G9 | PR desde un fork: token de solo lectura y sin secretos. `pull_request_target`: «Avoid… if it's not necessary» y nunca hacer checkout de código no confiable | S | events-that-trigger-workflows; secure-use |
| G10 | Hardening: datos no confiables por variables `env:` intermedias; fijar las actions a un SHA. Novedad: un *lockfile* de dependencias de workflows «supersedes SHA pinning» (formato **NV**) | S | secure-use |
| G11 | Pages con Actions: `upload-pages-artifact` + `deploy-pages`, permisos `pages: write` e `id-token: write`, environment `github-pages`. **No hay un procedimiento de rollback documentado**; un re-run repite el mismo SHA y solo hasta 30 días | S | using-custom-workflows-with-github-pages; re-run-workflows-and-jobs |
| G12 | Secret scanning automático y gratuito en repos públicos. *Push protection* para usuarios activo por defecto; para el repositorio, **NV** si viene activo | S | enable-secret-scanning; push-protection |

## 2. Claude Code y `claude-code-action`

| # | Hecho | Estado | Fuente |
|---|---|---|---|
| C1 | *Managed settings*: `/etc/claude-code/managed-settings.json` (Linux y WSL), `/Library/Application Support/ClaudeCode/…` (macOS), `C:\Program Files\ClaudeCode\…` (Windows) o servidor (consola de claude.ai). **En WSL, `/etc/claude-code` puede ser escribible por el usuario** | S | managed-settings |
| C2 | Un `deny` de cualquier nivel no se puede permitir desde otro; claves solo gestionadas: `allowManagedPermissionRulesOnly`, `allowManagedHooksOnly`, `allowManagedMcpServersOnly`, `sandbox.network.allowManagedDomainsOnly`… | S | managed-settings; permissions#settings-precedence |
| C3 | **Sandbox** en macOS, Linux y WSL2 (no en Windows nativo); desactivado por defecto; red con lista de dominios **vacía al inicio**; escritura limitada al directorio de trabajo y temporales | **M** | sandboxing |
| C4 | **Dentro del sandbox, los comandos se aprueban sin preguntar**; las reglas `ask` con contenido (`Bash(git push *)`) **siguen preguntando**. `allowUnsandboxedCommands: false` anula la vía `dangerouslyDisableSandbox` | **M** | sandboxing#auto-allow-mode |
| C5 | El sandbox «is not a complete isolation boundary» (*domain fronting*) | S | sandboxing#security-limitations |
| C6 | Subagentes: `tools` es una lista de herramientas sin patrones documentados. **`disallowedTools: Bash(x)` elimina Bash entero.** Para restringir comandos, `permissions.deny` (afecta a toda la sesión) o un hook `PreToolUse` en el frontmatter del subagente | **M** (tools, disallowedTools) / S (hook) | sub-agents |
| C7 | El `permissionMode` del subagente se ignora si la sesión principal está en `acceptEdits`, auto o bypass | S | sub-agents#permission-modes |
| C8 | `-p` sin `--bare` ejecuta los hooks y los MCP del proyecto incluso en carpetas no confiables. `--bare` es lo recomendado para scripts y «will become the default for `-p`»; **no lee credenciales OAuth** | S (confirma R-14) | headless |
| C9 | Opciones de CI: `--setting-sources`, `--settings`, `--strict-mcp-config`, `--tools`, `--disallowedTools`, `--permission-mode dontAsk` («locked-down CI runs»), `--max-turns`, `--max-budget-usd` (puede pasarse algo del límite), `--restricted` | S | cli-reference; headless |
| C10 | `claude-code-action@v1`: autenticación con API key, token OAuth, **federación de identidad (OIDC → cuenta de servicio de Console)** o Bedrock, Vertex o Foundry. Solo la dispara quien tiene escritura; rechaza bots salvo `allowed_bots`. **Restaura `.claude/`, `.mcp.json`, `CLAUDE.md`… desde la rama base del PR** antes de ejecutar. Si usa `--bare`: **NV** | S | github-actions; docs/security.md |
| C11 | `claude setup-token` (token OAuth de suscripción, un año): ligado a la persona, **no lo lee `--bare`** y la documentación recomienda una API key para secretos compartidos. Términos: «ordinary, individual usage» | S | authentication; legal-and-compliance |
| C12 | Modo automático: «does not guarantee safety»; `ask` y `deny` siguen aplicando; activo por defecto en Team y Enterprise | S | permission-modes |
| C13 | Que `Stop` muestre `systemMessage`: **NV**. Hay issues abiertas que dicen que no se muestra (#50542, #16289; no son documentación) | NV | hooks |

## 3. Consecuencias para el estándar (inferencia)

1. **Un solo mantenedor no puede aprobar su propio PR (G3).** Una regla de aprobaciones ≥ 1, de Code Owners o de último push bloquea todos sus PR. Con D-056, en el laboratorio la puerta humana es **el propio merge** más los checks requeridos. Las aprobaciones se especifican para N2+ y se prueban en el piloto (F8).
2. **Q-12 resuelta:** el «solo lectura» del verificador **no se puede imponer** con `tools` si necesita Bash. Las opciones reales son un hook `PreToolUse` con lista blanca o el sandbox (C4, C6).
3. **El sandbox es la salida para D-043.** Con él, `check` y `test` se ejecutan sin confirmación y con escritura y red acotadas, y los `ask` con contenido siguen funcionando. Es posible en WSL2, que es lo que usas.
4. **Agente en CI sin clave personal (D-055):** el camino corporativo es la federación OIDC con Console, o Bedrock/Vertex. El token de suscripción no es apto: es personal y no lo lee `--bare`.
5. `claude-code-action` **ya mitiga R-14 a su manera**, restaurando la configuración desde la rama base. Hay que decidir en F5.4 si eso basta o si se exige `--bare`.
6. **Rollback de Pages:** hay que construirlo nosotros, con un workflow manual que vuelva a desplegar un tag o SHA.
7. **Merge queue:** exige `merge_group` en todos los checks requeridos. Nuestros workflows reutilizables ya lo declaran.
8. P-11 (`systemMessage` en `Stop`) está en duda (C13). Se comprueba en F5.7 y, si no se muestra, se documenta `claude --debug`.
