---
id: ADR-014
titulo: "Mapa de segmentos como artefacto pivote"
estado: aprobado
fecha: 2026-10-19
revision: "2 (2026-11-13, D-083)"
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-014 · Mapa de segmentos como artefacto pivote [Fase 4]

**Recomendación**
- Un `.harness/segments.yaml` producido por el método de análisis de la codebase. Para cada segmento: rutas, propósito, propietario, dependencias permitidas, contratos o interfaces públicas, comandos propios, clase de riesgo y política de paralelización.
- A partir de él se **generan o validan**: CODEOWNERS, los `AGENTS.md` locales, las reglas por ruta del adaptador, las reglas de dependencias y la detección de conflictos entre tareas.

**Justificación**
- Convierte la segmentación (punto 6 del encargo) en algo verificable.
- Unifica cinco mecanismos que, si no, se mantendrían por separado y acabarían divergiendo.
- No impone ninguna arquitectura de aplicación: la describe y la hace verificable (P8).

**Riesgos**
- Que el mapa no refleje el código real.
- Mitigación: una regla compara los imports con las dependencias declaradas, cuando el lenguaje lo permita.

**Validación**
- Aplicarlo a un brownfield grande en la Fase 8 y medir la cobertura de rutas y las violaciones detectadas.

## Revisión 2 (D-083, 2026-11-13)

Aprobada con el análisis del brownfield (`docs/fase-4/02-segmentos.md`, E-045):
- **2a. Autoría:** `harness segments propose` propone y no escribe; una persona ajusta y versiona el mapa en un PR. Es ruta sensible (ADR-013).
- **2b. Derivados:** se validan, no se regeneran: CODEOWNERS, `AGENTS.md` de segmento y comandos.
- **2c. Dependencias:** línea base con trinquete. `depende_de` recoge las aceptadas; `deuda` las heredadas no deseadas, con motivo y caducidad (aviso mientras está vigente; error al caducar). Toda dependencia nueva no declarada es un error.
- **2d. Granularidad:** el segmento es una unidad de propiedad y de paralelización (orientación: 5–12 por repositorio), con `puntos_calientes` de política propia.
- **2e. Lenguajes:** solo Python verifica imports (AST, sin ejecutar); el resto se declara «no verificado».
- **Nivel:** DEBE en N2; PUEDE en N0 y N1, y si existe se valida.

Formato: `schemas/segments.schema.json`. Ficha: `standard/04-archivos/segments.map.md`.
