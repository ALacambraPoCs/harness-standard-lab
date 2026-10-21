---
rol: manifest
titulo: Manifiesto de instancia (.harness/manifest.yaml) y contrato de comandos
estado: propuesta
version: 0.1.0
consumidores: [cli, ci, agentes, personas]
dependencias: []
propietario: Propietario de la instancia (tech lead); revisión de plataforma/harness por CODEOWNERS (ADR-013)
requisitos: [HS-GOV-001, HS-GOV-002, HS-GOV-003, HS-GOV-006, HS-VER-001, HS-VER-002, HS-VER-003, HS-CTX-001]
reglas: [core.manifest.valid, core.manifest.standard-version, core.waivers.valid, core.roles.relocation, core.commands.declared, core.commands.execute, core.commands.idempotent]
ejemplo_canonico: template/core/.harness/manifest.yaml
fuentes: [decision-propia, ADR-004, ADR-006, ADR-007]
evolucion: >-
  Sigue el versionado de schemas/manifest.schema.json: MAJOR si un manifiesto válido deja de serlo;
  MINOR si se añade un campo opcional; PATCH si cambian descripciones.
---

# Manifiesto de instancia y contrato de comandos

> Ruta, obligatoriedad, nivel y capa: `standard/roles.yaml#manifest`. Esquema: `schemas/manifest.schema.json`.

## Propósito

Es la **declaración verificable** de una instancia. Responde a estas preguntas:

- Qué versión del estándar cumple el repositorio y a qué nivel.
- Qué adaptadores usa.
- Cómo se invocan sus comandos canónicos.
- Qué roles viven en rutas no estándar.
- Qué excepciones (waivers) tiene vigentes.

Es la única entrada de configuración de la CLI y de la CI (ADR-004).

## Contenido requerido

El esquema hace de ancla: cada clave obligatoria se valida en el JSON Schema.

| Elemento | Clave | Requisito | Verificación |
|---|---|---|---|
| Versión del estándar y nivel declarado | `standard.version`, `standard.level` | HS-GOV-001, HS-GOV-002 | Automática |
| Nombre, propietario y tipo de proyecto | `project.name`, `project.owner`, `project.kind` | HS-GOV-001 | Automática |
| Adaptadores de agente (con versión mínima) y de plataforma | `adapters.agents[]`, `adapters.platform` | HS-GOV-001 | Automática |
| Contrato de comandos: `setup`, `check` y `test` | `commands.*` | HS-VER-001 | Automática |

## Contenido recomendado y opcional

| Elemento | Clave | Cuándo |
|---|---|---|
| Idioma de los documentos de la instancia | `project.docs_language` | **Recomendado** (D-020). Ayuda a personas y agentes |
| Comandos condicionales | `commands.e2e`, `build`, `dev`, `clean` | Si aplican (ADR-006) |
| Roles reubicados | `roles.<rol>` | Solo en brownfield y solo con roles reubicables (HS-GOV-006) |
| Presupuestos | `budgets.instructions_max_lines` | Si el valor por defecto (200) no encaja |
| Mapa de segmentos | `segments` | Desde N2 (Fase 4) |
| Waivers | `waivers[]` | Excepciones temporales (HS-GOV-003) |
| Extensiones del proyecto | `x-*` | Solo datos que no afecten a la conformidad |

## Contrato de comandos (ADR-006)

| Rol | Obligatoriedad | Debe hacer | No debe hacer |
|---|---|---|---|
| `setup` | Obligatorio | Dejar el entorno listo desde cero. Idempotente (HS-VER-003) | Pedir datos interactivos; descargar secretos de producción |
| `check` | Obligatorio | Comprobación rápida: lint, tipos y tests unitarios. Es el comando que el agente ejecuta tras cada cambio | Tardar tanto que el agente deje de usarlo. Objetivo orientativo: pocos minutos (Fase 6) |
| `test` | Obligatorio | Suite completa salvo E2E | Depender de servicios externos no declarados |
| `e2e` | Condicional | Pruebas extremo a extremo | Ejecutarse en `check` |
| `build` | Condicional | Generar el artefacto desplegable | Desplegar |
| `dev` | Condicional | Arrancar la aplicación en local o en un worktree | Usar puertos fijos que impidan varios worktrees (Fase 4) |
| `clean` | Recomendado | Devolver el árbol a un estado limpio | Borrar configuración personal (`.env.local`, `CLAUDE.local.md`) |

**Propiedades comunes:**

- No interactivo: se ejecuta con la entrada estándar cerrada.
- Idempotente.
- Código de salida significativo.
- Errores con el patrón QUÉ / POR QUÉ / CÓMO arreglarlo.
- Ejecutable desde la raíz y desde cualquier worktree.
- Sin rutas absolutas de la máquina de nadie.

El valor del manifiesto es la **invocación exacta**: la misma cadena que citan `AGENTS.md` (HS-INS-002) y la CI.

## Contenido excluido

| No incluir | Va en |
|---|---|
| Secretos, tokens, URLs con credenciales | Gestor de secretos o variables de CI (HS-SEC-004) |
| Lógica de build (scripts largos en la cadena del comando) | `Makefile`, `justfile`, `package.json` o un script; el manifiesto solo lo invoca |
| Configuración de herramientas de agente (permisos, hooks) | Su adaptador (`.claude/settings.json`) |
| Estado de tareas o del proyecto | `plans.active` |
| Waivers sin aprobador ni caducidad | En ningún sitio: el esquema los rechaza |

## Formato y convenciones

- YAML 1.2. Las fechas se escriben `AAAA-MM-DD`; la CLI las trata como texto y las valida con `format: date`.
- Ruta fija `.harness/manifest.yaml`, no reubicable.
- No se admiten claves desconocidas, salvo las que empiezan por `x-`.
- Comentarios en YAML permitidos y recomendados para explicar waivers y reubicaciones.

## Ejemplo canónico

Ver `template/core/.harness/manifest.yaml` y `tests/fixtures/conforming/n0-reubicado/.harness/manifest.yaml`. Este último muestra roles reubicados y un waiver.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Esquema, versión soportada y nivel definido | L4 (`core.manifest.*`) | Vigente |
| Waivers válidos, que no superan 90 días y no han caducado | L4 (`core.waivers.valid`) | Vigente |
| Roles reubicados válidos | L4 (`core.roles.relocation`) | Vigente |
| Comandos declarados, ejecutables e idempotentes | L4 (`core.commands.*`, con `--run-commands`) | Vigente |
| Cambios revisados por plataforma o harness | L5 (CODEOWNERS de `/.harness/`) | Vigente |

## Criterios de aceptación

1. `harness check` sin errores `core.manifest.*`, `core.waivers.*`, `core.roles.*` ni `core.commands.*`.
2. Cada waiver tiene un motivo comprensible para una persona ajena al equipo.
3. Los comandos del manifiesto son los mismos que usan la CI y las personas.

## Ciclo de vida y evolución

- **Creación:** con la plantilla o con `harness init` (Fase 7).
- **Actualización:** al cambiar de nivel, de versión del estándar o un comando, o al aprobar o renovar un waiver.
- **Revisión:** en cada actualización de versión del estándar (Fase 9: `harness upgrade`).
- **Retirada:** no aplica mientras la instancia siga el estándar.
