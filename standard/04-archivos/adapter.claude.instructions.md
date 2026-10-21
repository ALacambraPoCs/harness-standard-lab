---
rol: adapter.claude.instructions
roles_adicionales: [adapter.claude.local]
titulo: CLAUDE.md (adaptador de Claude Code) y CLAUDE.local.md
estado: propuesta
version: 0.1.0
consumidores: [agentes, cli]
dependencias: [instructions.root, adapter.claude.settings]
propietario: Propietario de plataforma/harness (CODEOWNERS, ADR-013); CLAUDE.local.md es de cada persona y no se versiona
requisitos: [HS-INS-005, HS-INS-006, HS-INS-007, HS-SEC-003, HS-CTX-001, "pendiente:F2.5"]
reglas: [adapter.claude.imports-agents, adapter.claude.no-duplication, adapter.claude.local-files-ignored, core.instructions.references-resolve, core.instructions.size-budget]
ejemplo_canonico: template/adapters/claude-code/CLAUDE.md
fuentes: [S-CC-MEM, S-CC-SET, ADR-003, ADR-013]
evolucion: >-
  MAJOR si cambia la forma de importar AGENTS.md o la versión mínima exigida de Claude Code;
  MINOR si se permite un nuevo tipo de contenido exclusivo; PATCH si es editorial.
---

# CLAUDE.md (adaptador de Claude Code) y CLAUDE.local.md

> Rutas, obligatoriedad y nivel: `standard/roles.yaml#adapter.claude.instructions` y `#adapter.claude.local`.

## Propósito

Hacer que Claude Code cargue `AGENTS.md`, que es la fuente única (ADR-003), y añadir **solo** lo que es exclusivo de Claude Code.

**Por qué hace falta.** Según S-CC-MEM (verificado el 2026-10-19), Claude Code lee `AGENTS.md` solo si no existe `CLAUDE.md`, `.claude/CLAUDE.md` ni `CLAUDE.local.md`. Si una persona crea su `CLAUDE.local.md`, deja de leer `AGENTS.md` sin avisar. Un `CLAUDE.md` versionado con `@AGENTS.md` hace que la carga sea determinista con cualquier configuración.

## Contenido requerido

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Línea `@AGENTS.md`, fuera de bloques de código. **Recomendado: primera línea no vacía** | El propio import | HS-INS-006 | Automática |

## Contenido recomendado y opcional

Solo contenido **exclusivo de Claude Code**, en una sección bajo `<!-- harness:claude -->`:

- Cuándo usar los subagentes del proyecto (`.claude/agents/`, Fase 3). Ejemplo: "antes de abrir el PR, invoca el subagente `verifier`".
- Uso de skills o comandos de Claude Code del catálogo (Fase 3).
- Indicaciones sobre los modos de Claude Code (por ejemplo, usar el modo plan para cambios de varios módulos), siempre que no se presenten como un control de seguridad.

## Contenido excluido

| No incluir | Va en |
|---|---|
| Cualquier regla, comando o restricción **agnóstica** | `AGENTS.md` (HS-INS-007) |
| Permisos, comandos prohibidos, rutas denegadas | `.claude/settings.json`: `permissions.deny` (L2). Las instrucciones no imponen (ADR-009) |
| Estado de tareas | `plans.active` (HS-INS-004) |
| Preferencias personales (estilo propio, URLs de sandbox personales) | `CLAUDE.local.md` (no versionado) |
| Imports de rutas fuera del repositorio (`@~/…`, rutas absolutas) | Ninguno: no son reproducibles y Claude Code pide aprobación para cargarlos (S-CC-MEM) |
| Cadenas de imports anidados | Evitar. S-CC-MEM admite **4 saltos como máximo** y los imports rotos fallan en silencio |

## Formato y convenciones

- Nombre exacto `CLAUDE.md` en la raíz. **No se usa** `.claude/CLAUDE.md` para no tener dos ubicaciones; Claude Code admite ambas (S-CC-MEM).
- Recordatorio: **importar no ahorra contexto**. Todo lo importado se carga al arrancar (S-CC-MEM), así que el presupuesto se mide sobre `AGENTS.md` + `CLAUDE.md`.
- **Presupuesto propio**: 200 líneas por defecto (HS-CTX-001). Recomendación interna: **20 líneas o menos**. Si crece, probablemente contiene contenido agnóstico.
- Versión mínima de Claude Code: la declarada en `adapters.agents[claude-code].min_version` del manifiesto (2.1.277 en las plantillas, por la lectura nativa de AGENTS.md).
- **Segmentos — obligatorio:** cada `<segmento>/AGENTS.md` DEBE tener al lado un `<segmento>/CLAUDE.md` con `@AGENTS.md` (pendiente:F2.5). Motivo (S-CC-MEM, verificado 2026-10-21): con un `CLAUDE.md` raíz, Claude no lee AGENTS.md de subdirectorios; en cambio carga bajo demanda los `CLAUDE.md` de subdirectorios, y el import resuelve relativo al archivo.

### CLAUDE.local.md

- Es personal y **NO DEBE versionarse**: `.gitignore` incluye `CLAUDE.local.md` y `.claude/settings.local.json` (HS-SEC-003).
- Como el `CLAUDE.md` versionado ya importa `AGENTS.md`, el `CLAUDE.local.md` de una persona **no** interrumpe la carga de las instrucciones del equipo.
- No es un mecanismo para desactivar restricciones. Si una restricción molesta, se propone un cambio por PR.

## Ejemplo canónico

```markdown
@AGENTS.md

<!-- harness:claude -->
## Solo para Claude Code
- Antes de abrir el PR, invoca el subagente `verifier` (.claude/agents/verifier.md) y adjunta su informe.
- Para cambios que afecten a más de un módulo, empieza en modo plan.
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe e importa `@AGENTS.md` | L4 (`adapter.claude.imports-agents`) | Vigente (N0) |
| No duplica encabezados ni líneas de AGENTS.md | L4 (`adapter.claude.no-duplication`) | Vigente (N0) |
| `CLAUDE.local.md` y `settings.local.json` en `.gitignore` | L4 (`adapter.claude.local-files-ignored`) | Vigente (N0) |
| Imports resolubles y sin rutas personales | L4 (`core.instructions.references-resolve`) | Vigente (N0) |
| `@AGENTS.md` como primera línea no vacía | L4 | Pendiente F2.5 (DEBERÍA) |
| Cada `<segmento>/AGENTS.md` tiene `<segmento>/CLAUDE.md` con `@AGENTS.md` | L4 | Pendiente F2.5 (DEBE) |
| `.claude/CLAUDE.md` ausente (una sola ubicación) | L4 | Pendiente F2.5 (DEBERÍA) |
| Revisión por propietario de plataforma | L5 (CODEOWNERS + ruleset) | Vigente (ADR-013) |

## Criterios de aceptación

1. Con o sin `CLAUDE.local.md` personal, una sesión de Claude Code en el repositorio carga las instrucciones de `AGENTS.md`. Prueba manual descrita en ADR-003.
2. `harness check` sin errores en las reglas `adapter.claude.*`.
3. Todo lo que contiene es exclusivo de Claude Code. Si se borrara, solo perderían información los usuarios de Claude Code.

## Ciclo de vida y evolución

- **Creación:** al declarar `claude-code` en el manifiesto, desde `template/adapters/claude-code/`.
- **Actualización:** cuando cambien los subagentes o skills del proyecto (Fase 3) o la versión mínima de Claude Code.
- **Revisión:** trimestral, junto con la reverificación de la documentación oficial de Claude Code (R-01). Si Claude Code pasa a cargar `AGENTS.md` de forma incondicional en todas sus superficies, se revisa HS-INS-006.
- **Retirada:** al quitar el adaptador `claude-code` del manifiesto.
