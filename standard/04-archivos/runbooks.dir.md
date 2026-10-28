---
rol: runbooks.dir
titulo: Runbooks de despliegue, rollback e incidentes
estado: propuesta
version: 0.1.0
consumidores: [personas, agentes]
dependencias: [ci.workflows, security.policy]
propietario: Responsable de operación del repositorio (quien despliega)
requisitos: [HS-CI-009]
reglas: [core.runbooks.rollback]
ejemplo_canonico: catalog/workflow/despliegue-pages/src/RUNBOOK-rollback.md
fuentes: [S-GH, ADR-009, ADR-010, D-054, D-072]
evolucion: >-
  MAJOR si cambia una sección obligatoria; MINOR si se añade una recomendada; PATCH editorial.
---

# Runbooks de despliegue, rollback e incidentes

> Ruta, obligatoriedad, nivel y capa: ver `standard/roles.yaml#runbooks.dir`. Ficha aplazada en F2 y redactada en F5.6.

## Propósito
Que **una persona** pueda devolver el servicio a una versión buena sin depender de un agente ni de quien lo desplegó, con los pasos, la verificación y el escalado escritos de antemano. El rollback automático (componente `despliegue-pages`) cubre el caso que se detecta solo; el runbook cubre el resto.

## Contenido requerido
Aplica si la instancia despliega (declara `plataforma.entorno_despliegue` en el manifiesto).

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Un runbook de rollback | archivo `rollback*.md` en el directorio | HS-CI-009 | `core.runbooks.rollback` (L4) |
| Cuándo usarlo | `<!-- harness:cuando -->` | HS-CI-009 | Ídem |
| Pasos numerados | `<!-- harness:pasos -->` | HS-CI-009 | Ídem |
| Cómo se verifica | `<!-- harness:verificacion -->` | HS-CI-009 | Ídem |
| A quién se escala | `<!-- harness:escalado -->` | HS-CI-009 | Ídem |

## Contenido recomendado y opcional
- `<!-- harness:permisos -->`: qué permisos necesita quien lo ejecuta (y que un agente no los tiene).
- Frontmatter con `propietario` y `revisado` (fecha del último ensayo).
- Runbooks de incidentes y de despliegue manual, con las mismas anclas.

## Contenido excluido
| No incluir | Va en |
|---|---|
| Secretos, tokens o URL con credenciales | Gestor de secretos de la plataforma |
| Decisiones de arquitectura | `decisions.dir` (ADR) |
| Pasos que un agente ejecuta solo con permisos de despliegue | No: desplegar y revertir lo hace el workflow o una persona (D-069) |

## Formato y convenciones
Markdown, un procedimiento por archivo, pasos imperativos y comprobables. Idioma libre (D-020).

## Ejemplo canónico
`catalog/workflow/despliegue-pages/src/RUNBOOK-rollback.md`, que instala `harness components add despliegue-pages` en `docs/runbooks/rollback-pages.md`.

## Validaciones
| Validación | Capa | Estado |
|---|---|---|
| Existe un runbook de rollback con las cuatro anclas si el manifiesto declara `entorno_despliegue` | L4 (`core.runbooks.rollback`) | Desde 0.9.0 |
| El runbook se ha ensayado (`revisado` reciente) | Manual | Recomendado; F5.7 lo ensaya en el laboratorio |

## Criterios de aceptación
1. Una persona que no hizo el despliegue sigue el runbook y el sitio vuelve a servir la versión elegida.
2. `harness check` no da hallazgos de `core.runbooks.rollback`.

## Ciclo de vida y evolución
Se crea al empezar a desplegar. Se actualiza cuando cambian el workflow o el environment. Se revisa tras cada uso real o ensayo, actualizando `revisado`.
