---
rol: architecture.map
titulo: Mapa de arquitectura (ARCHITECTURE.md)
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas]
dependencias: [decisions.dir, instructions.root, segments.map, project.rules]
propietario: Tech lead del repositorio
requisitos: [HS-ARC-001, HS-INS-008, HS-ARC-003]
reglas: [core.architecture.map-exists]
ejemplo_canonico: template/core/docs/architecture/ARCHITECTURE.md
fuentes: [S-MATKLAD-ARCH, S-OAI-HE#p6, S-OAI-HE#p8, S-LHE#L03]
evolucion: >-
  MAJOR si se añade o elimina un ancla obligatoria; MINOR si se añade una opcional; PATCH editorial.
---

# Mapa de arquitectura

> Ruta (reubicable), obligatoriedad y nivel: `standard/roles.yaml#architecture.map`.

## Propósito

Responder rápidamente a dos preguntas, para personas y para agentes (S-MATKLAD-ARCH):

- *¿Dónde está lo que hace X?*
- *¿Qué hace esto que estoy mirando?*

Es *"un mapa del país, no un atlas de cada región"*. Fija además los **límites e invariantes** que el código no deja ver a simple vista y que los agentes tienden a romper por imitación de patrones (S-OAI-HE p.8 y p.11).

## Contenido requerido

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Visión: qué problema resuelve el sistema y sus piezas principales, en un párrafo | `<!-- harness:vision -->` | HS-ARC-003 | Ancla + revisión |
| Mapa del código: módulos o directorios de primer nivel con una línea cada uno. Se **nombran**, no se enlazan | `<!-- harness:mapa-codigo -->` | HS-ARC-003 | Ancla + revisión |
| Límites y dependencias permitidas: qué puede depender de qué, y qué está prohibido | `<!-- harness:limites -->` | HS-ARC-003 | Ancla + revisión. Desde N1, recomendado imponerlo con `.harness/rules/` o un linter |
| Invariantes: reglas que siempre se cumplen, sobre todo las que se expresan como **ausencia** ("X nunca llama a Y") | `<!-- harness:invariantes -->` | HS-ARC-003 | Ancla + revisión |

## Contenido recomendado y opcional

| Elemento | Ancla | Cuándo |
|---|---|---|
| Aspectos transversales: autenticación, logging, configuración, feature flags, errores | `<!-- harness:transversal -->` | Recomendado si existen |
| Diagrama de contexto o de contenedores (Mermaid u otro formato que se pueda leer como texto) | — | Opcional. El diagrama nunca sustituye a la lista |
| Puntos calientes: zonas frágiles o con mucho cambio | `<!-- harness:puntos-calientes -->` | Opcional. Útil para la segmentación (Fase 4) |

## Contenido excluido

| No incluir | Va en |
|---|---|
| Cómo funciona cada módulo por dentro | Documentación del módulo o comentarios en el código (S-MATKLAD-ARCH) |
| Enlaces a archivos, líneas o símbolos concretos | Nombres que se buscan con la búsqueda de símbolos: los enlaces caducan (S-MATKLAD-ARCH) |
| Por qué se eligió una tecnología | `decisions.dir` (ADR), enlazado desde aquí |
| Instrucciones operativas para el agente ("ejecuta…", "no hagas…") | `AGENTS.md` (`harness:restricciones`) |
| Estado de trabajo o deuda en curso | `plans.active` o `quality.doc` |
| Listados automáticos del árbol de directorios | Nada: el agente puede listar el árbol y la copia se queda obsoleta |

## Formato y convenciones

- Markdown, en un único archivo y **breve**. Recomendación: 150 líneas o menos. Lo tienen que leer todas las personas y agentes que contribuyen (S-MATKLAD-ARCH).
- Recoge solo lo que cambia poco. No se intenta sincronizar con cada cambio de código: se revisa un par de veces al año (S-MATKLAD-ARCH) y cuando cambian los límites.
- Idioma libre (D-020). Los nombres de módulos y tipos se escriben tal como aparecen en el código.

## Ejemplo canónico

Ver `template/core/docs/architecture/ARCHITECTURE.md`. Ejemplo resumido:

```markdown
<!-- harness:vision -->
## Visión
payments-api calcula y liquida pagos de comercios. Recibe órdenes del backoffice y emite eventos al ledger.

<!-- harness:mapa-codigo -->
## Mapa del código
- `api/`: endpoints HTTP; solo validación y traducción.
- `domain/`: reglas de cálculo (`Fee`, `Settlement`); sin E/S.
- `adapters/`: base de datos y cliente del ledger.

<!-- harness:limites -->
## Límites
- `domain` no importa `api` ni `adapters` (se comprueba con import-linter en `make check`).

<!-- harness:invariantes -->
## Invariantes
- Ningún importe es `float`.
- Ninguna escritura en `settlements` ocurre fuera de una transacción.
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe (en su ruta por defecto o reubicada) | L4 (`core.architecture.map-exists`) | Vigente |
| Enlazado desde `AGENTS.md` | L4 (`core.instructions.links-core-docs`) | Vigente (DEBERÍA) |
| Anclas obligatorias presentes | L4 | HS-ARC-003 (N1), `core.architecture.anchors` |
| Límites impuestos de forma mecánica | L4 (`.harness/rules/`, linters) | Fase 4 |
| Contenido correcto y actual | Revisión humana periódica | Manual |

## Criterios de aceptación

1. Una persona nueva localiza en menos de 5 minutos dónde vive la funcionalidad X. Criterio adaptado de S-LHE L01/L05; es un valor didáctico que se mide en el piloto.
2. Cada límite declarado en `harness:limites` tiene un control o un waiver explícito.
3. No contiene detalle interno de módulos ni enlaces a líneas de código.

## Ciclo de vida y evolución

- **Creación:** en la adopción (N0).
- **Actualización:** en el mismo PR que cambie un límite, un invariante o el mapa de primer nivel.
- **Revisión:** semestral, o al detectar en revisión que un agente ha violado un límite no documentado.
- **Retirada:** no aplica.
