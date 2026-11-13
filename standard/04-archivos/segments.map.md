---
rol: segments.map
titulo: Mapa de segmentos (.harness/segments.yaml)
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas, cli, ci]
dependencias: [architecture.map, codeowners, instructions.segment, plans.dir]
propietario: Tech lead del repositorio, con revisión de plataforma (ruta sensible)
requisitos: [pendiente:F4.3]
reglas: []
ejemplo_canonico: examples/fragmentos/segments.yaml
fuentes: [ADR-014, D-083, S-MATKLAD-ARCH, fase-4/02-segmentos.md]
evolucion: >-
  MAJOR si cambia el significado de un campo o se añade uno obligatorio (sube `version`); MINOR si se añade un
  campo opcional; PATCH editorial.
---

# Mapa de segmentos

> Ruta (`.harness/segments.yaml`, no reubicable), obligatoriedad y nivel: `standard/roles.yaml#segments.map`. Formato: `schemas/segments.schema.json`.

## Propósito

Declarar en un solo sitio, de forma verificable, **qué partes tiene la codebase**, de quién es cada una, de qué puede depender, qué riesgo tiene y **cómo se puede trabajar en paralelo** en ella (ADR-014 rev. 2). Es el artefacto pivote del que se validan CODEOWNERS, los `AGENTS.md` de segmento, las reglas de dependencias y la detección de solapamientos entre tareas (F4.3 y F4.4).

Describe la arquitectura **real**, no la deseada. Lo que no se quiere se registra como deuda con caducidad y no puede empeorar (trinquete, 2c).

## Contenido requerido

| Elemento | Campo | Verificación |
|---|---|---|
| Versión del formato | `version: 1` | Esquema |
| Segmentos: id, propósito, rutas, propietario, riesgo y política de paralelización | `segmentos[]` | Esquema; ids únicos y referencias válidas (CLI) |
| Dependencias aceptadas entre segmentos | `segmentos[].depende_de` | `segments graph` (F4.2); trinquete en `segments check` (F4.3) |
| Todo archivo versionado pertenece a un segmento o está excluido de forma explícita | `segmentos[].rutas`, `excluidos[]` | `segments graph` informa; `segments check` falla (F4.3) |
| Dependencias reales no deseadas, con motivo y caducidad | `deuda[]` | Aviso mientras está vigente; error al caducar (F4.3) |

**Opcional:** `excluir` (rutas que se restan dentro del segmento), `lenguaje`, `contrato` (interfaz pública que usan otros segmentos), `comandos` (deben coincidir con el `AGENTS.md` del segmento), `puntos_calientes` (rutas con política propia, p. ej. migraciones en `serializada`) y `python.raices`.

**Políticas de paralelización:**
- `libre`: tareas concurrentes sin coordinación especial.
- `contrato`: concurrencia permitida si las tareas no cambian el `contrato` o declaran el cambio (F4.5).
- `serializada`: una tarea activa a la vez (F4.4).

## Contenido excluido

| No incluir | Va en |
|---|---|
| Estructura interna de cada segmento o explicación del código | `ARCHITECTURE.md` (límites e invariantes) o documentación del módulo |
| Instrucciones para el agente | `AGENTS.md` del segmento |
| Estado de tareas o quién trabaja ahora en un segmento | Archivos de tarea (`segments`, `lease`) |
| Un segmento por paquete | Agrupar: un segmento es una unidad de propiedad y paralelización (2d; orientación 5–12 por repositorio) |
| Rutas sin ancla para directorios de primer nivel (`tests/`) | `/tests/`: sin ancla, el patrón cubre cualquier `tests/` anidado (semántica gitignore/CODEOWNERS) |

## Formato y convenciones

- YAML. Los patrones de `rutas` siguen la semántica de CODEOWNERS de `matchers.py`: con `/` inicial o intermedia se anclan a la raíz, una barra final cubre todo el contenido y `**` cruza directorios.
- Un archivo debe pertenecer a un único segmento: los solapes se informan (F4.2) y fallan (F4.3). `excluir` resuelve los anidamientos (`/keep/api/` excluye `/keep/api/models/`).
- Las fechas de `caduca` pueden ir con o sin comillas.
- **Solo Python** se verifica (imports estáticos, sin ejecutar). Los segmentos en otro lenguaje aparecen como «no verificados» (2e).
- Ruta sensible: se modifica por PR con revisión de plataforma (ADR-013), como el resto de `.harness/`.

## Ejemplo canónico

Ver `examples/fragmentos/segments.yaml`. Flujo de creación en un brownfield:

```bash
harness segments propose --dividir app --format md     # informe: tamaños, cambio, imports, ciclos
harness segments propose --dividir app --format yaml > /tmp/borrador.yaml   # falla el esquema a propósito (TODO)
# Una persona agrupa, completa y guarda .harness/segments.yaml
harness segments graph                                 # matriz real: declarada, deuda o no declarada (X)
harness segments graph --sugerir-deuda 2027-06-30      # entradas de deuda para revisar
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Esquema, ids únicos y referencias de `depende_de` y `deuda` | L4 (CLI, `load_map`) | F4.2 |
| Matriz de dependencias reales frente a las declaradas | L4 (`segments graph`, informativo) | F4.2 |
| Cobertura de rutas, solapes, CODEOWNERS coherente, `AGENTS.md` de segmento, trinquete de dependencias | L4 (`segments check`) | F4.3 |
| Riesgo del segmento en `pr risk` | L4 | F4.3 |
| Paralelización (`serializada`, `contrato`) entre tareas activas | L4 (`tasks.overlap`) | F4.4 |
| Propósito correcto y agrupación sensata | Revisión humana en el PR | Manual |

## Criterios de aceptación

1. `segments graph` informa 0 archivos sin segmento ni exclusión y 0 solapes.
2. Toda arista real entre segmentos está en `depende_de` o en `deuda` vigente.
3. Cada segmento con `paralelizacion: serializada` o con `puntos_calientes` tiene un motivo que una persona nueva entiende.
4. El mapa lo aprobó una persona en un PR; no es la salida de `propose` sin editar (que falla el esquema).

## Ciclo de vida y evolución

- **Creación:** al adoptar N2, a partir de `harness segments propose`. En N0 y N1 es opcional y, si existe, se valida igual.
- **Actualización:** en el mismo PR que crea, mueve o fusiona un directorio de primer nivel, cambia de propietario o introduce una dependencia nueva aceptada.
- **Revisión:** al caducar una deuda (falla `segments check`) y en la revisión semestral de `ARCHITECTURE.md`.
- **Retirada:** no aplica en N2.
