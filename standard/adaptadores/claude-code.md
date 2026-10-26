---
documento: HS-ADP-CLAUDE
titulo: Adaptador de agente — Claude Code
version_estandar: 0.5.0
estado: aprobado (D-036; §3.4 y §4 ampliados en F3.7, D-041…D-043)
fecha: 2026-10-23
verificado_contra: documentación oficial de code.claude.com, leída el 2026-10-22 y el 2026-10-23 (docs/fase-3/01-verificacion-fuentes.md, fase-3/INFORME.md §6)
version_minima: 2.1.277
adr: [ADR-003, ADR-009, ADR-012, ADR-013]
---

# Adaptador de Claude Code

Traduce el núcleo neutro (`05-componentes`, `03-estructura-canonica`) a los archivos y opciones reales de Claude Code. Todo lo que aparece aquí está verificado en la documentación oficial en la fecha indicada (R-01). Lo que no se pudo verificar se marca.

## 1. Versión mínima

`adapters.agents[].min_version` del manifiesto: **2.1.277**. Es la versión desde la que la documentación describe la lectura de `AGENTS.md` sin `CLAUDE.md` y desde la que se ha verificado este adaptador. La CLI todavía no comprueba la versión instalada (F5).

## 2. Mapeo del núcleo a archivos

| Núcleo | Claude Code | Rol | Notas verificadas |
|---|---|---|---|
| Instrucciones raíz | `CLAUDE.md` con `@AGENTS.md` | `adapter.claude.instructions` | ADR-003. Si existe `CLAUDE.md`, Claude no lee `AGENTS.md` por sí mismo |
| Instrucciones de segmento | `<seg>/CLAUDE.md` con `@AGENTS.md` | `instructions.segment` | HS-INS-013 |
| Permisos y política | `.claude/settings.json` | `adapter.claude.settings` | §3 y ficha |
| Personal (no versionado) | `.claude/settings.local.json`, `CLAUDE.local.md` | `adapter.claude.local` | HS-SEC-003 |
| `skill` | `.claude/skills/<name>/SKILL.md` | — (F3.3) | ADR-012. Claude **no** lee `.agents/skills/` |
| `subagente` | `.claude/agents/<name>.md` | — (F3.3) | `name` y `description` obligatorios. `tools` es una lista de herramientas permitidas: un revisor usa `Read, Grep, Glob` |
| `hook` | Bloque `hooks` de `.claude/settings.json` y script en `.claude/hooks/` | — (F3.3) | Solo `type: command` (o `http`) cuenta como control. **Exit 2** bloquea. Se usa `${CLAUDE_PROJECT_DIR}` en la ruta del script |
| `mcp` | `.mcp.json` | — | Requiere aprobación en sesión interactiva; un repositorio no puede aprobar sus propios servidores |
| `plugin` | `.claude-plugin/plugin.json` y `enabledPlugins` en settings | — | No se usa para distribuir componentes del estándar (ADR-017): `--bare` no carga plugins y un plugin habilitado solo en el proyecto no se descarga salvo que su fuente sea una ruta relativa |

## 3. Política de permisos (deny-first)

### 3.1 Qué garantiza la configuración del proyecto y qué no

| Mecanismo en `.claude/settings.json` | ¿Aplica sin confiar en la carpeta? | Capa | Comentario |
|---|---|---|---|
| `permissions.deny` y `permissions.ask` | **Sí**, de inmediato | L2 | Son la base del adaptador |
| `permissions.allow` | No: solo tras aceptar el diálogo de confianza, y nunca en `-p` | L2 | No imponen nada: solo evitan confirmaciones de comandos sin efectos (§3.4) |
| `disableBypassPermissionsMode: "disable"` | Sí, desde cualquier archivo | L2 | Impide el modo que se salta las confirmaciones |
| `disableAutoMode: "disable"` | Sí, desde cualquier archivo | L2 | Impide el modo en que un clasificador decide las confirmaciones (HS-SEC-010). Un `settings.local.json` puede anularlo; en *managed settings* no |
| `defaultMode: auto` o `bypassPermissions` | **No tienen efecto** desde el proyecto | — | Se prohíben por claridad |
| Hooks del proyecto | Sí, **también en `-p` sin confianza** (R-14) | L3 | Útiles como retroalimentación; en CI son un riesgo (§5) |

### 3.2 Límites que hay que asumir (H6)

- Las reglas deny de `Read` y `Edit` cubren las herramientas de archivos de Claude, los comandos de Bash que Claude reconoce (`cat`, `sed`, `tee`…) y las redirecciones. **No cubren** un script de Python o Node que abra el archivo, ni `grep -r` lanzado desde el directorio. Para un bloqueo a nivel de sistema operativo está el **sandbox** (macOS y Linux/WSL2; no disponible en Windows nativo).
- **Conclusión normativa:** los secretos no se protegen con reglas deny. Se protegen no teniéndolos en el árbol de trabajo (HS-SEC-004, escáner en F5). Las reglas deny reducen la exposición accidental y no son un control frente a un agente comprometido.
- La documentación de hooks dice: «use the permission system rather than a hook to enforce a hard allow or deny». Por eso **pedir confirmación en rutas sensibles se hace con reglas `ask`, no con un hook** (cambia F3.4, §6).

- Una regla `Bash(...)` coincide con el texto del comando tras separar los compuestos (`&&`, `;`, `|`…) y quitar envoltorios. `deny` y `ask` aplican si coincide **cualquier** parte; `allow`, solo si coinciden **todas**. Pero no detienen otras formas de invocar el mismo programa (`/usr/bin/gh …`, `sh -c '…'`, opciones antes del subcomando). Las reglas `gh` de §3.4 son reducción de riesgo; la frontera es un token de mínimo privilegio y el sandbox (F5).
- Claude Code ejecuta sin preguntar una lista interna, no configurable, de comandos de solo lectura (`ls`, `cat`, `grep`, formas de solo lectura de `git`…). No hace falta permitirlos.

### 3.3 Anclaje de rutas en las reglas

| Patrón | Significado en `.claude/settings.json` |
|---|---|
| `Read(.env)` (nombre sin barra) | Cualquier `.env` en cualquier profundidad bajo el directorio de trabajo (semántica de gitignore) |
| `Edit(/.github/workflows/**)` | Relativo al directorio de trabajo principal de la sesión. **Claude se inicia en la raíz del repositorio** |
| `Read(//abs/…)` y `Read(~/…)` | Absoluto y relativo a home. No se usan en archivos versionados (HS-INS-005, rutas personales) |

### 3.4 Comandos: qué se rechaza, qué pide confirmación y qué se permite (F3.7)

| Decisión | Reglas | Por qué | Requisito |
|---|---|---|---|
| `deny` | `Bash(gh repo delete *)`, `Bash(gh secret *)`, `Bash(gh ruleset *)`, `Bash(gh auth *)` | Irreversible, credenciales o la frontera L5; `gh auth token` imprime el token en el contexto del modelo | HS-SEC-011 |
| `ask` | `Bash(git push *)`, `Bash(gh pr merge *)`, `Bash(gh api *)` | Efectos fuera del repositorio local; `gh api` puede escribir cualquier cosa en GitHub (H-7) | HS-SEC-008, HS-SEC-011 |
| `ask` | `Bash(harness * --run-commands*)`, `Bash(harness * --run-acceptance*)`, `Bash(harness * --json-out*)` | Ejecutan comandos del manifiesto o de las tareas (que el agente puede editar) o escriben un archivo arbitrario | HS-SEC-012 |
| `allow` | `Bash(harness check *)`, `Bash(harness tasks validate *)`, `Bash(harness tasks index --check)`, `Bash(harness tasks close *)`, `Bash(harness pr check *)`, `Bash(harness components list)` | Comandos del contrato sin efectos, o que solo editan `docs/plans/` (que el agente ya edita sin confirmación). Reducen confirmaciones (H-4) | HS-SEC-012 |
| `ask` | `Bash(git add -f*)`, `Bash(git add * -f*)`, `Bash(git add --force*)`, `Bash(git add * --force*)`, `Bash(git commit -n *)`, `Bash(git commit * -n *)`, `Bash(git commit * -n)`, `Bash(git commit --no-verify*)`, `Bash(git commit * --no-verify*)`, `Bash(gh pr edit *)` | Meter en el índice archivos ignorados (p. ej. `.env`), saltarse los hooks de commit de la persona; `gh pr edit` no lo usa la skill (D-049) | HS-SEC-012 (F3.8, D-052) |
| `allow` | `Bash(git add *)`, `Bash(git commit *)`, `Bash(gh pr view *)`, `Bash(gh pr create *)`, `Bash(gh pr ready *)` | Local y reversible, o solo lectura; nada sale del equipo sin `git push`, que sigue en `ask`. `gh pr create` requiere un push previo y la skill lo abre en borrador | HS-SEC-012 (F3.8, D-052) |

- `ask` se evalúa antes que `allow`, así que `harness check --run-commands` pide confirmación aunque `harness check *` esté permitido.
- **Límite conocido (inferencia, por analogía con el ejemplo documentado de `git -C . push`):** formas como `git -C . add -f …`, `git -c core.hooksPath=… commit` o flags combinados (`git commit -nm x`) no coinciden con los `ask` específicos y sí con el `allow` general. El riesgo es bajo porque todo es local hasta el `push`, que sigue en `ask`.
- Un test de la CLI (`tests/test_template.py`) congela las opciones de estos subcomandos. Si se añade una opción con efectos y no se cubre con `ask`, la CI central falla.
- **No se permiten en la base** los comandos `check` y `test` de cada instancia. Permitir `python3 -m unittest` es ejecutar sin confirmación código que acaba de escribir el agente. Es una decisión de cada instancia (por ejemplo `Bash(npm test)`), preferiblemente con sandbox. HS-SEC-012 avisa de las reglas que abren intérpretes (`python -c`, `bash -c`, `node -e`…), red, borrado, `git` o `gh` en general.

## 4. Configuración base

`template/adapters/claude-code/.claude/settings.json`. Su contenido requerido está en la ficha `adapter.claude.settings`:

- `deny` para leer y editar `.env*`, claves (`*.pem`, `*.key`) y `secrets/`;
- `ask` para editar **cada** patrón de `patrones_sensibles` (`roles.yaml`), además de `git push` y `gh pr merge`;
- las reglas de comandos de §3.4;
- `disableBypassPermissionsMode: "disable"` y `disableAutoMode: "disable"`;
- `enableAllProjectMcpServers: false`.

## 5. El agente en CI

Hechos verificados (`headless`, `permissions`):
- Con `claude -p`, la carpeta nunca se marca como de confianza. Aun así se ejecutan los hooks y el bloque `env` del proyecto, y los servidores de `.mcp.json` **se conectan sin preguntar**.
- `--bare` omite hooks, skills, comandos, subagentes, plugins, `.mcp.json` y CLAUDE.md, pero **el bloque `env` del proyecto y helpers como `apiKeyHelper` siguen aplicándose**.
- `--setting-sources user` hace que no se lean ni la configuración ni `.mcp.json` del proyecto.

**Regla del adaptador** (candidato K-12): cuando el agente se ejecuta en CI sobre código de un PR, se lanza con `--bare --setting-sources user` y con `--settings` y `--mcp-config` desde una ruta que **no** viene del PR. El job no tiene secretos de escritura (ADR-013, R-14). El workflow completo se diseña en F5.

## 6. Consecuencias para el plan de la F3

- **F3.4:** el hook semilla `rutas-sensibles` se sustituye por las reglas `ask` de §4, que son más simples y además son lo que recomienda la documentación. Se propone otro hook que aporte lo que los permisos no pueden hacer: **`verificar-al-terminar`**, un hook `Stop` que ejecuta `check` y `harness tasks validate` y, si fallan, devuelve exit 2 para que el agente no dé el trabajo por terminado (verificado: en `Stop`, el exit 2 «prevents Claude from stopping»). Es retroalimentación L3, no autoridad: la autoridad sigue en la CI (ADR-016). **No verificado:** el campo `stop_hook_active` para evitar bucles. El hook llevará su propio límite de reintentos.

## 7. Revisión periódica

Cada trimestre, y antes de subir `version_minima`, se reverifican en la documentación oficial §2, §3.1, §3.2 y §5. Si algo cambia, se registra con fecha en `docs/REGISTRO.md`.
