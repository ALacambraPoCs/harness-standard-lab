---
rol: adapter.claude.settings
titulo: Configuración compartida de Claude Code (.claude/settings.json)
estado: propuesta
version: 0.1.0
consumidores: [agentes, cli, plataforma]
dependencias: [adapter.claude.instructions, adapter.claude.local, security.policy, codeowners, manifest]
propietario: Propietario de plataforma/harness (CODEOWNERS, ADR-013), con revisión de seguridad para cambios en deny/ask
requisitos: [HS-SEC-007, HS-SEC-008, HS-SEC-009, HS-CMP-006, HS-CMP-007]
reglas: [adapter.claude.settings-secrets, adapter.claude.settings-sensitive, adapter.claude.settings-modes, adapter.claude.hooks-scripts, adapter.claude.hooks-nondeterministic]
ejemplo_canonico: template/adapters/claude-code/.claude/settings.json
fuentes: [S-CC-SET, ADR-009, ADR-013, S-OWASP-LLM01]
evolucion: >-
  MAJOR si se añade una regla obligatoria que una instancia conforme no cumpla; MINOR si se añaden
  recomendaciones o rutas sensibles nuevas (que vienen de roles.yaml); PATCH editorial.
---

# Configuración compartida de Claude Code (`.claude/settings.json`)

> Ruta, obligatoriedad (condicional: `claude-code` y N1 o superior) y nivel: `standard/roles.yaml#adapter.claude.settings`. Detalle técnico y hechos verificados: `standard/adaptadores/claude-code.md`.

## Propósito

Fijar, para todo el equipo, **qué no puede hacer el agente sin preguntar y qué no puede hacer nunca** en este repositorio. Es la capa L2 (permisos) del modelo de control. Complementa a CODEOWNERS y al ruleset (L5), que son la autoridad final, pero no los sustituye.

## Contenido requerido

| Elemento | Requisito | Verificación |
|---|---|---|
| JSON estricto válido (`$schema` `https://json.schemastore.org/claude-code-settings.json` recomendado) | HS-SEC-007 | Automática |
| `permissions.deny` para leer y editar `.env` y `.env.*` | HS-SEC-007 | Automática |
| `permissions.ask` (o `deny`) de `Edit` que cubre **cada** ruta de `rutas_sensibles` de `roles.yaml` | HS-SEC-008 | Automática (rutas de muestra contra las reglas) |
| `permissions.disableBypassPermissionsMode: "disable"` | HS-SEC-009 | Automática |
| Sin `enableAllProjectMcpServers: true` ni `defaultMode` `auto`/`bypassPermissions` | HS-SEC-009 | Automática |
| Hooks `command` que apuntan a scripts versionados existentes | HS-CMP-006 | Automática |

## Contenido recomendado y opcional

- `deny` de lectura de claves (`**/*.pem`, `**/*.key`) y del directorio `secrets/`.
- `ask` para `Bash(git push *)` y `Bash(gh pr merge *)`.
- Hooks `command` del catálogo, por ejemplo `verificar-al-terminar` (F3.4). Solo componentes del catálogo con su ficha.
- `sandbox.enabled: true` en equipos con macOS o Linux/WSL2. En Windows nativo no está disponible, así que no se exige.

## Contenido excluido

| No incluir | Por qué / dónde va |
|---|---|
| `permissions.allow` como mecanismo de seguridad | No aplica sin confianza ni en `-p`. Solo se permite para comodidad (comandos del contrato) |
| `defaultMode: "auto"` o `"bypassPermissions"` | No tiene efecto desde el proyecto y confunde. Va en la configuración de usuario o gestionada |
| Hooks `prompt` o `agent` presentados como control | No son deterministas (ADR-009, C9) |
| Secretos, tokens o `apiKeyHelper` con credenciales | `env` y los helpers se aplican incluso con `--bare` (§5 del adaptador). Ningún secreto en archivos versionados |
| Preferencias personales (modelo, tema) | `.claude/settings.local.json` o `~/.claude/settings.json` |
| Rutas absolutas o de home (`//…`, `~/…`) | No son portables (HS-INS-005) |
| `enabledPlugins` o `extraKnownMarketplaces` sin componente aprobado en el catálogo | Distribución, F3.5 |

## Formato y convenciones

- JSON estricto: sin comentarios ni comas finales (un error invalida el archivo entero).
- Las rutas `/…` se anclan en el directorio de trabajo principal: **Claude Code se inicia en la raíz del repositorio**.
- `Read(.env.*)` también bloquea `.env.example`. La plantilla de variables se llama `env.example` (sin punto inicial) o se documenta en `docs/`.
- Las listas se combinan entre ámbitos (gestionado, proyecto, usuario y local). Un `allow` personal no anula un `ask` o `deny` del proyecto.

## Ejemplo canónico

`template/adapters/claude-code/.claude/settings.json`.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Contenido requerido (tabla anterior) | L4 (`harness check`) | Vigente desde el estándar 0.3.0 |
| `.claude/` bajo CODEOWNERS | L5 | Vigente (HS-SEC-002) |
| `.claude/settings.local.json` ignorado por Git | L4 | Vigente (HS-SEC-003) |
| Cobertura de `patrones_sensibles` por la plantilla | L4 (autotest del repositorio central) | Vigente (`tests/test_template.py`) |

## Criterios de aceptación

1. Una sesión de Claude Code en la raíz pide confirmación al editar cualquier ruta sensible (F3.6, con evidencia).
2. `harness check` falla si falta alguno de los elementos requeridos (F3.3).
3. Ningún cambio en este archivo se fusiona sin aprobación del propietario en CODEOWNERS.

## Ciclo de vida y evolución

- **Creación:** al adoptar N1 con `claude-code`, a partir de la plantilla.
- **Actualización:** cuando cambien `patrones_sensibles` o la documentación de Claude Code (revisión trimestral del adaptador).
- **Retirada:** si la organización gestiona estas reglas en *managed settings* para todos los repositorios. En ese caso, el requisito pasa a verificar que no se contradicen.
