---
rol: ci.workflows
titulo: Workflows de CI de la instancia
estado: propuesta
version: 0.1.0
consumidores: [plataforma, cli, personas]
dependencias: [manifest, codeowners, pr.template, plans.active]
propietario: Equipo de plataforma/harness (y seguridad para los cambios de permisos)
requisitos: [HS-GOV-004, HS-CI-003, HS-CI-004, HS-CI-005, HS-CI-006, HS-CI-007, HS-CI-008]
reglas: [core.ci.agent-bare, ci.no-pr-target, ci.no-untrusted-interpolation, ci.permissions, ci.model-readonly, ci.pinned, ci.merge-group]
ejemplo_canonico: template/niveles/n1/.github/workflows/harness-tasks.yml
fuentes: [S-GH, ADR-009, ADR-010, ADR-013, ADR-016, D-058, D-060, F5-01]
evolucion: >-
  MAJOR si cambia un check requerido o sus permisos; MINOR si se añade un job opcional; PATCH editorial.
---

# Workflows de CI de la instancia

> Ruta: `.github/workflows/` (`standard/roles.yaml#ci.workflows`). Ficha aplazada en F2 (D-031) y redactada en F5.2.

## Propósito

Concentrar la **autoridad L4** del harness: los checks que deciden si un PR se puede fusionar. Las instancias no reimplementan esos checks; **llaman a los workflows reutilizables** del repositorio del estándar, fijados a un tag `cli-v…`, para que la lógica sea la misma en todas.

## Contenido requerido

| Workflow | Nivel | Qué hace | Check requerido | Requisito |
|---|---|---|---|---|
| `harness.yml` → `harness-conformance.yml` | N0 | `harness check` de la instancia | `harness / conformance / harness check` | HS-GOV-004 |
| `harness-tasks.yml` → `harness-tasks-lifecycle.yml` | N1 | Tareas y transiciones, aceptación de las que pasan a `done` (ADR-016), cuerpo del PR contra el diff, clase de riesgo calculada (D-058) e índice | `tasks / harness tasks` | HS-CI-003, HS-CI-005 |
| Ídem, job `puerta-riesgo-alto` | N1 | Solo si la clase es `alto`: espera la aprobación en el environment `aprobacion-riesgo-alto`. Si no, se salta y cuenta como éxito | `tasks / puerta riesgo alto` | ADR-010 rev. 2 |
| `harness-platform.yml` → `harness-platform.yml` | N1 (0.7.0+) | `harness platform check` semanal y en cada push a la rama por defecto; si falla, abre o comenta una issue. **No es check de PR** | — (programado) | HS-CI-006 |

Opcional: el componente de catálogo `despliegue-pages` (F5.6) despliega en GitHub Pages desde la rama por defecto, verifica el SHA servido, revierte solo si falla y publica `harness audit` en el resumen. Solo sus jobs de despliegue tienen `pages: write` e `id-token: write`.

Opcional: el componente de catálogo `revisor-informativo` (F5.4) añade una revisión de PR con agente, **informativa** (nunca check requerido), con el modelo en solo lectura y la publicación en un job sin credenciales del modelo.

Reglas de forma para cualquier workflow de la instancia:
- `permissions:` a nivel de workflow con `contents: read`, y ampliación **por job** solo de lo que usa (G8: un workflow reutilizable no puede ampliar lo que le da quien lo llama).
- Disparadores `pull_request` y `merge_group` en todo check requerido (G5).
- **Sin `pull_request_target`** salvo con un ADR propio (G9).
- Datos del evento (`github.event.*`) solo a través de `env:`, nunca interpolados en `run:` (G10).
- Actions de terceros fijadas a un SHA completo (G10).
- Un paso que ejecute `claude -p` usa `--bare --setting-sources user` (HS-CI-004).

## Contenido excluido

| No incluir | Por qué |
|---|---|
| Secretos del modelo en jobs con permisos de escritura | ADR-013: el job del modelo es de solo lectura; la publicación va en otro job |
| Lógica de conformidad copiada en la instancia | Deriva respecto al estándar; se llama al workflow reutilizable |
| `continue-on-error` en checks requeridos | Convierte el control en informativo sin que se vea |

## Formato y convenciones

- Nombres de job estables: son los nombres de los checks requeridos en el ruleset.
- `cli-ref` y el ref de `uses:` son el mismo tag.

## Ejemplo canónico

`template/adapters/github/.github/workflows/harness.yml` (N0), `template/niveles/n1/.github/workflows/harness-tasks.yml` y `harness-platform.yml` (N1).

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existen los workflows del nivel | L4 (`harness check`) | Vigente |
| `claude -p` con `--bare --setting-sources user` | L4 (`core.ci.agent-bare`) | Vigente desde 0.3.0 |
| Sin `pull_request_target`, sin interpolación no confiable, `permissions:` en lectura, modelo sin escritura | L4 (`ci.*`, HS-CI-007) | Vigente desde 0.7.0 |
| Actions fijadas a SHA y `merge_group` | L4 (`ci.pinned`, `ci.merge-group`, HS-CI-008) | Vigente desde 0.7.0 |
| Los checks requeridos y el environment de la puerta existen y están protegidos | L5 vía API (`harness platform check`, HS-CI-006) | Vigente desde 0.7.0; plantillas en `standard/plataforma/` |

## Criterios de aceptación

1. Un PR de la instancia muestra los checks requeridos del nivel y no se puede fusionar si alguno falla.
2. Un PR que toca `.github/workflows/` queda en espera de aprobación en el environment de la puerta (F5.7).
3. Ningún job con credenciales del modelo tiene permiso de escritura.

## Ciclo de vida y evolución

- Los cambios en `.github/workflows/` son ruta crítica (riesgo `alto`, D-058) y pasan por CODEOWNERS.
- Subir `cli-ref` se hace en un PR propio, con el CHANGELOG del estándar.
