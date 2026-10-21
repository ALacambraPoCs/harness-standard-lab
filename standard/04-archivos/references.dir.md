---
rol: references.dir
titulo: Referencias externas para el modelo (docs/references/)
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas]
dependencias: [instructions.root, security.policy]
propietario: Tech lead del repositorio
requisitos: [HS-CTX-004]
reglas: []
ejemplo_canonico: examples/fragmentos/references-README.md
fuentes: [S-OAI-HE#p5, S-LHE]
evolucion: >-
  MINOR si se añaden campos de procedencia obligatorios; PATCH editorial.
---

# Referencias externas para el modelo

> Ruta (reubicable), obligatoriedad (opcional) y nivel: `standard/roles.yaml#references.dir`.

## Propósito

Dar al agente, **bajo demanda**, documentación de terceros que necesita y que no está en sus datos de entrenamiento o puede estar desactualizada: una librería interna, la versión concreta de un framework, un sistema de diseño.

Es la práctica `*-llms.txt` de `docs/references/` descrita en S-OAI-HE p.5. Evita pegar esa documentación en las instrucciones.

## Contenido requerido

Si el directorio existe:

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| `README.md` índice: archivo · qué contiene · fuente (URL o repositorio) · versión o fecha de captura | `<!-- harness:indice -->` | HS-CTX-004 | Ancla + revisión |

## Contenido recomendado y opcional

- Versiones condensadas para modelos (`<tema>-llms.txt` o `.md`). Mejor que copias completas.
- Indicar en `AGENTS.md` (`harness:mapa`) cuándo consultar cada referencia.

## Contenido excluido

| No incluir | Va en |
|---|---|
| Documentación sin fuente ni fecha | En ningún sitio: no se puede verificar ni actualizar |
| Contenido con licencia que no permita redistribuirlo en el repositorio | Enlace externo en el índice |
| Instrucciones para el agente dentro de una referencia | `AGENTS.md`. Una referencia es **dato**, no instrucción (PR-7) |
| Documentación propia del proyecto | `architecture.map`, `decisions.dir` u otros roles |

## Formato y convenciones

- Texto plano o Markdown. Cada archivo empieza con la línea `Fuente: <URL> · Capturado: AAAA-MM-DD`.
- Un tema por archivo, con nombre en minúsculas y guiones.
- Las referencias son **entrada no confiable** (PR-7): se revisan en el PR que las añade, igual que el código.

## Ejemplo canónico

Ver `examples/fragmentos/references-README.md`.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Índice presente y archivos con fuente y fecha | L4 | HS-CTX-004 (DEBERÍA), `core.references.provenance` |
| Revisión de su contenido en el PR | L5 | Vigente (revisión normal) |

## Criterios de aceptación

1. Cada archivo tiene fuente y fecha de captura, y figura en el índice.
2. Ninguna referencia contiene instrucciones dirigidas al agente.

## Ciclo de vida y evolución

- **Creación:** cuando un agente falla de forma repetida por desconocer una librería o una versión.
- **Actualización:** al cambiar de versión la dependencia referenciada.
- **Retirada:** cuando la dependencia desaparece o el modelo ya la conoce bien. Se evalúa por ablación en la Fase 6 (ADR-015).
