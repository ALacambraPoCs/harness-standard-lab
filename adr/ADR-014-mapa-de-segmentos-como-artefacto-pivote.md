---
id: ADR-014
titulo: "Mapa de segmentos como artefacto pivote"
estado: propuesto
fecha: 2026-10-19
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
