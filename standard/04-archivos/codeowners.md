---
rol: codeowners
titulo: CODEOWNERS
estado: propuesta
version: 0.1.0
consumidores: [plataforma, cli, personas]
dependencias: [instructions.root, adapter.claude.instructions, adapter.claude.settings, manifest, ci.workflows]
propietario: Equipo de plataforma y seguridad (el propio CODEOWNERS se protege a sí mismo)
requisitos: [HS-SEC-002, "pendiente:F2.5"]
reglas: [core.codeowners.sensitive-paths]
ejemplo_canonico: template/adapters/github/.github/CODEOWNERS
fuentes: [S-GH, S-VILA#p29, ADR-013]
evolucion: >-
  MAJOR si se añaden rutas sensibles obligatorias (rutas_sensibles en roles.yaml); MINOR si se añaden
  recomendaciones; PATCH editorial.
---

# CODEOWNERS

> Ruta y alternativas reconocidas por GitHub: `standard/roles.yaml#codeowners`.

## Propósito

Asignar un **propietario que tiene que aprobar** los cambios en cada parte del repositorio. Lo más importante es proteger la configuración de agentes, de CI y del propio harness frente a PR que la relajen (ADR-013).

Combinado con la regla de ruleset *Require review from Code Owners*, es un control **L5**. Sin esa regla, solo sugiere revisores.

## Contenido requerido

| Elemento | Requisito | Verificación |
|---|---|---|
| Un único archivo, en la primera ubicación que busca GitHub: `.github/`, raíz o `docs/` | HS-SEC-002 | Automática (aviso si hay varios) |
| Cada ruta de `roles.yaml#rutas_sensibles` con al menos un propietario **tras aplicar la regla "gana el último patrón"** | HS-SEC-002 | Automática |
| Las líneas sensibles van **al final** del archivo, para que ningún patrón posterior las anule | HS-SEC-002 (lo hace efectivo) | Automática (por la semántica) |

## Contenido recomendado y opcional

- Una regla por defecto (`*`) con el equipo propietario del repositorio.
- En N1, propietarios por segmento o directorio para el código. En N2 se generan o validan contra `segments.yaml` (ADR-014).
- Los `AGENTS.md` de segmento PUEDEN delegarse en el propietario del segmento. Nunca se delegan `.claude/`, `.mcp.json`, `.github/workflows/`, `.github/CODEOWNERS` ni `.harness/` (ADR-013).

## Contenido excluido

| No incluir | Por qué |
|---|---|
| Usuarios o equipos sin permiso de escritura | GitHub exige que los propietarios tengan permiso de escritura; si no, no actúan como propietarios (S-GH) y la ruta queda sin propietario efectivo |
| Patrones con `!` o `[ ]` | GitHub no los admite en CODEOWNERS (S-GH) |
| Patrones posteriores que anulen las rutas sensibles (por ejemplo `/.claude/` sin propietario al final) | Gana el último patrón que coincide. Lo detecta la regla |

## Formato y convenciones

- Sintaxis de GitHub: patrón seguido de propietarios (`@usuario`, `@org/equipo` o email). Es parecida a `.gitignore`, sin negación (S-GH).
- `*` no cruza `/`. `docs/*` cubre los archivos de `docs/`, pero no los de sus subdirectorios.
- GitHub lee el archivo de la **rama base** del PR. Un cambio en CODEOWNERS no se aplica hasta que se fusiona (S-GH).
- Debe estar acompañado por la regla de ruleset *Require review from Code Owners* (Fase 5). En el laboratorio con un solo mantenedor esta regla está desactivada (R-10).

## Ejemplo canónico

Ver `template/adapters/github/.github/CODEOWNERS`.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Ubicación única y rutas sensibles cubiertas | L4 (`core.codeowners.sensitive-paths`) | Vigente |
| Propietarios con permiso de escritura (no ignorados por GitHub) | L4 con la API de GitHub | Pendiente F5 |
| Revisión de code owner exigida en el ruleset | L5 | Manual hasta la F5 (R-10 en el laboratorio) |

## Criterios de aceptación

1. `harness check` sin errores de `core.codeowners.sensitive-paths`.
2. En la vista de GitHub (*Code owners* del archivo) no aparecen errores de sintaxis ni propietarios desconocidos.
3. Un PR que toca `.claude/settings.json` pide revisión al propietario de seguridad o plataforma.

## Ciclo de vida y evolución

- **Creación:** en la adopción (N0).
- **Actualización:** al crear un segmento, cambiar de equipo o añadir una ruta sensible en el estándar.
- **Revisión:** trimestral (equipos y personas que ya no están).
- **Retirada:** no aplica.
