---
id: ADR-008
titulo: "Lenguaje y forma de distribución de la CLI"
estado: aprobado-parcial
aprobado_por: Usuario (Alberto Lacambra) — solo el lenguaje
fecha: 2026-10-19
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-008 · Lenguaje y forma de distribución de la CLI [Fase 7, recomendación provisional]

**Recomendación provisional**
- La CLI se distribuye como paquete versionado y como acción o workflow reutilizable de GitHub.
- Lenguaje: Python o Node/TypeScript, pendiente de decidir según el stack mayoritario del equipo.
- Para la actualización de instancias se propone evaluar **Copier**, que soporta actualizar proyectos derivados de una plantilla, frente a implementar `harness upgrade` propio.

**Justificación**
- Es lo que exige el punto 10 del encargo (actualizar y migrar).
- Las plantillas de GitHub y cookiecutter no permiten actualizar después de generar.

**Alternativas**
- Binario Go: no tiene dependencias, pero el equipo tendría que mantener otro lenguaje.
- Reutilizar `harness-creator`: no es viable porque sus reglas no sirven (F0-01 §6), aunque sí su arquitectura.

**Riesgos**
- La capacidad de actualización de Copier y su comportamiento con archivos modificados está **pendiente de verificar** en la Fase 7.

**Validación**
- Prueba de actualización de 0.x a 0.y sobre los ejemplos sin pérdida de cambios locales.

## Decisión parcial (2026-10-19)

- **Aprobado:** la CLI se implementa en **Python 3.11+** (dependencias: `pyyaml`, `jsonschema`). Aprobado por el usuario al iniciar la Fase 1 (REGISTRO D-014).
- **Implementado en F1:** se distribuye como paquete instalable desde el repositorio central (`pip install git+…@<tag>`) y mediante un workflow reutilizable de GitHub (`.github/workflows/harness-conformance.yml`, `on: workflow_call`).
- **Pendiente (Fase 7):** mecanismo de actualización de instancias (Copier frente a `harness upgrade` propio).
