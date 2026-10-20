---
id: ADR-001
titulo: "Tres productos y un repositorio central con dos líneas de versión"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-001 · Tres productos y un repositorio central con dos líneas de versión [APROBADO 2026-10-19]

**Recomendación**
- Separar A (estándar), B (plantilla, CLI y CI) y C (instancia).
- A y B viven en un único repositorio central.
- A y B se versionan por separado:
  - A lleva su propio SemVer.
  - B declara qué rango de versiones de A soporta.
- Si A y B se contradicen, prevalece A.

**Justificación**
- El usuario pide distinguir los tres productos.
- Tenerlos en un solo repositorio permite que un cambio normativo y su regla de validación entren en el mismo PR, lo que garantiza la trazabilidad.
- Versionarlos por separado permite corregir la CLI sin "cambiar la norma".

**Alternativas**
- (a) Repositorios separados para A y B: más gobierno y peor trazabilidad. Se pospone hasta que haya varios equipos manteniéndolos.
- (b) Una sola versión para todo: obligaría a publicar versiones del estándar por bugs de la CLI.

**Riesgos y supuestos**
- Exige disciplina para no meter normas en la plantilla sin reflejarlas en A.
- Supuesto: habrá un grupo de gobierno con autoridad para aprobar cambios en A.

**Evidencia**
- Decisión de diseño propia. No hay fuente externa.
- Lección del corpus: las plantillas del curso no superan sus propios validadores (F0-01 §6), por falta de acoplamiento entre normas y herramientas.

**Validación**
- La matriz de trazabilidad se genera en CI.
- Un PR que añada un requisito automatizable sin regla ni fixtures falla.
