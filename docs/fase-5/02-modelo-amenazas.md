---
documento: F5-02
titulo: F5.1 · Modelo de amenazas del harness
estado: aprobado (D-057)
fecha: 2026-10-26
depende_de: [ADR-009, ADR-013, ADR-016, F5-01]
---

# Modelo de amenazas del harness

**Alcance:** un repositorio de instancia en GitHub, personas y agentes de programación (Claude Code en local y, opcionalmente, en CI) y la CLI `harness`. No cubre la seguridad de la propia aplicación del equipo, más allá de lo que el harness verifica.

**Capas** (ADR-009):
- **L1**: instrucción.
- **L2**: permisos del agente.
- **L3**: hook o retroalimentación local.
- **L4**: check de CI.
- **L5**: regla de plataforma (ruleset, environment o token).

Solo **L4 y L5** son autoridad. L1–L3 reducen la probabilidad del daño.

## 1. Activos

| ID | Activo | Por qué importa |
|---|---|---|
| A1 | Rama por defecto (`main`) | Lo que se fusiona se despliega |
| A2 | Configuración de agentes (`AGENTS.md`, `CLAUDE.md`, `.claude/**`, `.mcp.json`, `.harness/**`) | Cambia lo que hacen los agentes de todo el equipo (ADR-013) |
| A3 | Workflows y CODEOWNERS (`.github/**`) | Definen la propia autoridad L4 y L5 |
| A4 | Secretos: tokens de GitHub, claves de modelo, secretos de environment | Dan acceso fuera del repositorio |
| A5 | Entorno de despliegue (`github-pages`) | Producción |
| A6 | Equipo de la persona (archivos, `~/.ssh`, credenciales) | Lo que ejecuta el agente en local |
| A7 | Registro de tareas y evidencias (`docs/plans/`, cuerpos de PR) | Auditoría y X-01 |

## 2. Actores

| ID | Actor | Capacidad |
|---|---|---|
| T1 | Colaborador externo (PR desde un fork) | Abre PR, escribe issues y comentarios |
| T2 | Contenido no confiable que lee el agente (issue, web, dependencia, salida de MCP, archivo del repo) | Inyecta instrucciones (OWASP LLM01) |
| T3 | **Agente con buena intención pero equivocado** (el caso frecuente: H-8, H-13, H-15) | Lo que le permitan los permisos de la sesión |
| T4 | Agente comprometido por T2 | Igual que T3, con intención hostil |
| T5 | Miembro del equipo con escritura (error o mala práctica) | Push a ramas, PR, cambios de configuración |
| T6 | Dependencia o action de terceros comprometida | Código que se ejecuta en CI o en local |

## 3. Vectores y controles

| ID | Vector | Actor | Activo | Control (capa) | Estado | Residual |
|---|---|---|---|---|---|---|
| V1 | Un PR modifica la configuración de agentes para relajar reglas o meter un hook | T1, T4, T5 | A2 | CODEOWNERS (L5, HS-SEC-002) y regla `ask` para editar (L2, HS-SEC-008). En CI, `--bare --setting-sources user` y configuración desde fuera del PR (L4, HS-CI-004) | ✅ L2, L4 · ⚠️ L5 sin una segunda persona (R-10) | Con un único mantenedor, CODEOWNERS no aporta independencia |
| V2 | Un PR modifica un workflow para exfiltrar secretos o fusionar | T1, T5 | A3, A4 | Forks sin secretos (plataforma). CODEOWNERS en `.github/**`. Los checks requeridos de un PR no pueden aprobarse a sí mismos. Prohibir `pull_request_target` | ✅ L4 (HS-CI-007, F5.3) | Reglas estáticas: una interpolación indirecta (composite action) puede escapar |
| V3 | Inyección en issue o PR que lee un agente en CI | T2 → T4 | A1, A4 | Job del modelo con `contents: read` y sin secretos de escritura. Publicación en un job separado sin credenciales del modelo (ADR-013). Revisión **informativa**, no autoridad (ADR-010) | ✅ diseño y contención (componente `revisor-informativo`, F5.4; prueba en F5.7) | El texto del informe puede engañar a quien lo lea; credenciales con formato desconocido no se enmascaran |
| V4 | Inyección en contenido que lee el agente en local | T2 → T4 | A6, A1 | `deny` de secretos (L2), `ask` para push y rutas sensibles (L2), sandbox (L2+SO), CI como autoridad (L4) | ✅ L2 · ✅ sandbox en la plantilla (F5.5, HS-SEC-013) | Windows nativo sin sandbox; el sandbox no es aislamiento completo |
| V5 | El agente se salta las reglas Bash con otra forma de invocar (`sh -c`, rutas absolutas) | T3, T4 | A1, A3 | Las reglas Bash **no son frontera** (C-docs). Frontera: sandbox (L2+SO) y token de mínimo privilegio | ✅ sandbox (F5.5) para lo que corre dentro; lo excluido (`git`, `gh`) depende del token (F5.5-C) | R-16 reducido |
| V6 | Modo automático o «no volver a preguntar» que amplía permisos sin revisión | T3, T5 | A6 | `disableAutoMode` y `disableBypassPermissionsMode` en el proyecto (L2), y en *managed settings*, donde no se pueden anular | ✅ proyecto · ✅ plantilla gestionada (F5.5, D-068) | `settings.local.json` puede reactivarlos; en WSL, el managed es escribible por el usuario (C1) |
| V7 | El agente declara terminado algo roto, o falsea la evidencia | T3, T4 | A1, A7 | ADR-016: la CI vuelve a ejecutar los criterios (L4, check requerido L5). El informe del verificador es informativo | ✅ (E-011, E-023) | Criterios débiles: candidato K-14 (aviso si cambian en el PR de cierre) |
| V8 | El agente debilita los criterios de aceptación para que pasen | T3, T4 | A7, A1 | La skill lo prohíbe (L1); revisión humana | ⚠️ solo L1 | K-14 lo convierte en L4 |
| V9 | Fusión sin revisión humana suficiente para el riesgo | T5 | A1 | Ruleset: PR obligatorio, checks requeridos, aprobaciones por clase de riesgo (L5) | ✅ L4 riesgo (F5.2) · ✅ comprobación L5 (`harness platform check`, F5.3) · ⚠️ un mantenedor (G3) | En el laboratorio, la persona es la única puerta |
| V10 | Despliegue no autorizado o imposible de revertir | T4, T5 | A5 | Environment `github-pages` limitado a `main`, con bypass de admins desactivado si procede (L5). Rollback ensayado | 🔲 F5.6 | Rollback propio (G11) |
| V11 | Credencial del agente con más alcance del necesario (`gh` con el token completo de la persona) | T3, T4 | A1, A3, A4 | `deny` de `gh auth`, `gh secret`, `gh ruleset` y `gh repo delete`; `ask` de `gh api` (L2). Token fine-grained de mínimo privilegio para el agente (L5) | ✅ L2 (E-022) · ✅ token de mínimo privilegio (F5.5-C, por probar en F5.7) | Commits con la identidad de la persona |
| V12 | Action o dependencia comprometida en CI | T6 | A3, A4 | Fijar actions a SHA o *lockfile* (G10); permisos mínimos por job (G8) | ✅ L4 (`ci.pinned`, HS-CI-008) | Tags `cli-v*` mutables salvo ruleset de tags en el estándar |
| V13 | Secretos versionados | T3, T5 | A4 | Secret scanning (plataforma, G12), `deny` de lectura (L2), HS-SEC-004 | ✅ plataforma · ⚠️ *push protection* del repo por confirmar | — |
| V14 | Servidor MCP del repositorio que se ejecuta sin aprobación | T1, T4 | A6 | `enableAllProjectMcpServers: false`; en CI, `--bare` o `--strict-mcp-config` | ✅ L2 · ✅ L4 (HS-CI-004) | — |

## 4. Riesgos aceptados (por ahora)

| Riesgo | Por qué | Hasta |
|---|---|---|
| Un único mantenedor: sin independencia en revisión ni aprobación (V1, V9) | D-056 | F8 (piloto) |
| Las reglas Bash como reducción de riesgo y no frontera (V5) | Hasta tener sandbox y token propio | F5.5 |
| Agente en CI sin modelo real (V3) | D-055: la prueba usa un simulador hostil | Piloto con federación OIDC corporativa |

## 5. Cómo se valida (F5.7)

Una **prueba adversarial** por vector abierto, con evidencia en el laboratorio:
- un PR que modifica `.claude/settings.json` y un workflow (V1, V2);
- un simulador de agente comprometido en CI que intenta escribir y exfiltrar (V3);
- un intento de `sh -c 'git push …'` con y sin sandbox (V5);
- un despliegue desde una rama no permitida y un rollback (V10).
