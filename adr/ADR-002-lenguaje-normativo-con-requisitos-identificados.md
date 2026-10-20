---
id: ADR-002
titulo: "Lenguaje normativo con requisitos identificados"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-002 · Lenguaje normativo con requisitos identificados [APROBADO 2026-10-19]

**Recomendación**
- Usar DEBE / DEBERÍA / PUEDE (RFC 2119/8174 en español).
- Cada requisito tiene un ID `HS-<DOMINIO>-NNN` y lleva los atributos:
  - `naturaleza`: guidance o enforcement.
  - `verificacion`: automática, semiautomática o manual.
  - `conformidad`: niveles a los que aplica.
  - `fuentes`.
  - `retirada`.
- Todo ello se registra en `requirements.yaml`.

**Justificación**
- Permite comprobar la conformidad, generar informes y aplicar excepciones (waivers) a nivel de requisito.
- Hace explícito el principio del proyecto: "cada mecanismo tiene propósito, responsable, coste, validación y condición de retirada".

**Alternativas**
- Prosa sin IDs: no se puede verificar ni trazar.
- Usar solo el código de las reglas como norma: mezcla A con B.

**Riesgos**
- Burocracia si se definen demasiados requisitos.
- Mitigación: presupuesto de requisitos por dominio y revisión por ablación (ADR-015).

**Evidencia**
- RFC 2119/8174 es la práctica estándar en especificaciones.
- Las anotaciones `why/source/remove when` de `audit-harness.sh` (S-LHE) son un precedente.

**Validación**
- La CLI genera un informe de cobertura que indica el porcentaje de requisitos automatizables que tienen regla.
