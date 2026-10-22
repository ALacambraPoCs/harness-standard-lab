---
documento: F3-FUENTES
titulo: Verificación de fuentes para la Fase 3 (componentes y adaptador de Claude Code)
fecha: 2026-10-22
metodo: Lectura de la documentación oficial vigente por dos subagentes, con cita y URL. Lo no verificado se marca así (R-08).
---

# F3 · Verificación de fuentes

## 1. Hallazgos que cambian decisiones previas

| # | Hallazgo | Fuente | Impacto |
|---|---|---|---|
| H1 | Claude Code **no lee** `.agents/skills/`. La página de memoria lo dice expresamente: "anything under a `.agents/` directory" no se lee | code.claude.com/docs/en/skills; /memory | Confirma la premisa de ADR-012 |
| H2 | **GitHub Copilot y Cursor leen `.claude/skills/`** además de `.agents/skills/`. Codex y Gemini CLI leen `.agents/skills/` | docs.github.com/en/copilot/concepts/agents/about-agent-skills; cursor.com/docs/context/skills; learn.chatgpt.com/docs/build-skills; geminicli.com/docs/cli/skills | **Cambia ADR-012:** `.claude/skills/` ya es portable a 3 de las 5 herramientas |
| H3 | Claude Code **ignora sin error** los campos de frontmatter que no reconoce | code.claude.com/docs/en/skills | Corrige la justificación de ADR-012 ("producen error"). El riesgo de portabilidad está en las otras herramientas, no en Claude |
| H4 | `skills-ref` es una demostración: "not meant to be used in production" | github.com/agentskills/agentskills/tree/main/skills-ref | No conviene depender de él en CI. La CLI valida la especificación por su cuenta |
| H5 | Con `claude -p` **sin `--bare`** se ejecutan los hooks y los servidores de `.mcp.json` del proyecto **aunque la carpeta no sea de confianza**, pero las reglas `permissions.allow` del proyecto no se aplican | code.claude.com/docs/en/headless; /settings; /mcp | En CI, el agente se ejecuta con `--bare` y configuración explícita. Refuerza ADR-013 |
| H6 | Las reglas deny de Read y Edit no cubren subprocesos (por ejemplo, un script de Python que lee `.env`). Para eso está el sandbox (macOS y Linux/WSL2; no en Windows nativo) | code.claude.com/docs/en/permissions; /sandboxing | Una regla deny no basta como control de secretos. La seguridad la dan las capas L2 (permisos), L2 (sandbox) y L4/L5 (CI y plataforma) |

## 2. Hechos verificados (resumen)

**Skills (Agent Skills, agentskills.io/specification)**
- Campos: `name` (1–64, `a-z0-9-`, sin `--`, igual al directorio) y `description` (1–1024) obligatorios; `license`, `compatibility` (≤ 500), `metadata` (mapa de cadena a cadena) y `allowed-tools` (experimental) opcionales.
- Divulgación progresiva: metadatos (~100 tokens) al inicio, instrucciones (< 5000 tokens recomendado) al activarse y recursos cuando hacen falta. SKILL.md, menos de 500 líneas.
- **Claude Code** añade: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools` (dura un turno), `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks`, `paths` y `shell`. Las descripciones tienen un presupuesto de ≈ 1 % de la ventana y se truncan a 1536 caracteres.

**Subagentes** (`.claude/agents/*.md`)
- Obligatorios: `name` y `description`.
- Opcionales, entre otros: `tools` (lista de permitidas), `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks` e `isolation: worktree`.
- En plugins se ignoran `hooks`, `mcpServers` y `permissionMode`.

**Hooks**
- 33 eventos (PreToolUse, PostToolUse, Stop, SessionStart, SubagentStop, ConfigChange…).
- Tipos: `command`, `http`, `mcp_tool`, `prompt` y `agent` (este último, experimental).
- **Exit 2 bloquea**, y ni siquiera un `allow` en JSON lo anula. Con PreToolUse se devuelve `permissionDecision` con `allow`, `deny`, `ask` o `defer`.
- Una regla deny de permisos prevalece sobre un `allow` del hook.
- Tiempo máximo de `command`: 600 s.
- Controles de gestión: `disableAllHooks` y `allowManagedHooksOnly`.

**Settings y permisos**
- Precedencia: managed > CLI > `settings.local.json` > `settings.json` del proyecto > usuario. Las listas se combinan.
- Orden de evaluación: deny → ask → allow. Un allow no puede abrir una excepción a un deny.
- Sintaxis: `Bash(npm run test *)`, `Read(./.env)`, `Edit(/.github/**)`, `WebFetch(domain:x)`, `mcp__srv__*` y `Agent(name)`.
- `defaultMode`: default, acceptEdits, plan, auto, dontAsk y bypassPermissions. `auto` y `bypassPermissions` **no surten efecto** desde la configuración del proyecto.
- `permissions.disableBypassPermissionsMode: "disable"`.

**Plugins**
- Raíz con `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json` y `.claude-plugin/plugin.json` (solo `name` obligatorio).
- Marketplace en `.claude-plugin/marketplace.json` (`name`, `owner`, `plugins`), con fuentes git fijables por `ref` y `sha`.
- Validación: `claude plugin validate --strict`.
- Desde el proyecto se declaran `extraKnownMarketplaces` (requiere confianza) y `enabledPlugins`. Un plugin habilitado solo en el proyecto no se descarga salvo que su fuente sea una ruta relativa.
- La versión se toma del manifiesto, si no de la entrada del marketplace y si no del SHA.

**MCP**
- `.mcp.json` requiere aprobación en sesión interactiva ("A cloned repository can't approve its own servers"), pero en `-p` se carga sin preguntar.
- Listas `allowedMcpServers` y `deniedMcpServers`; ninguna regla anula una coincidencia en la lista de denegados.
- Especificación MCP 2026-07-28:
  - las descripciones de herramientas no son confiables;
  - se requiere consentimiento antes de invocar;
  - se prohíbe el *token passthrough*;
  - se debe mostrar el comando local completo antes de aprobarlo;
  - se recomienda `stdio` para servidores locales y sandbox.

**Inyección de prompts** (OWASP LLM01:2025): privilegio mínimo, aprobación humana para acciones de alto riesgo, segregación del contenido externo y pruebas adversarias.

## 3. No verificado
- Si `skills-ref` en PyPI (0.1.1) es un canal oficial.
- El comportamiento exacto de `defer` y `ask` en PreToolUse (la página se cortó antes de esa sección).
- S-CODEX-AGENTSMD (32 KiB), que sigue pendiente de leerse a mano (R-08).

## 4. Verificaciones adicionales (F3.2, 2026-10-22)

Lectura directa de code.claude.com/docs/en/settings, /permissions y /hooks:

- **Workspace trust:** «`deny` and `ask` rules apply right away»; `permissions.allow` y `additionalDirectories` esperan a la confianza (y nunca se aplican en `-p`).
- **Anclaje:** `/path` es relativo a la fuente de configuración, que en un proyecto es el «primary working directory». Un nombre sin barra (`Read(.env)`) sigue la semántica de gitignore y coincide a cualquier profundidad.
- **Bash compuesto:** «a rule like `Bash(safe-cmd *)` won't give it permission to run the command `safe-cmd && other-cmd`». Las reglas deny y ask se aplican si coincide cualquier subcomando.
- **`$schema`:** `https://json.schemastore.org/claude-code-settings.json` (documentado y recomendado).
- **`-p` en una carpeta no confiable:** se ejecutan los hooks y el `env` del proyecto y se conectan los MCP de `.mcp.json` sin preguntar. Con `--bare`, el `env` del proyecto y los helpers siguen aplicándose. `--setting-sources user` evita leer la configuración y `.mcp.json` del proyecto.
- **Hooks:** en `Stop`, el exit 2 «Prevents Claude from stopping, continues the conversation»; JSON `{"decision": "block", "reason": …}`; `${CLAUDE_PROJECT_DIR}` disponible. La documentación recomienda: «use the permission system rather than a hook to enforce a hard allow or deny».
- **No verificado:** el campo `stop_hook_active` (la sección no se pudo leer completa).
