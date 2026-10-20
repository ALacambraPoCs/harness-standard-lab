---
id: ADR-010
titulo: "Autorización de merge y despliegue separada de la revisión por agentes"
estado: propuesto
fecha: 2026-10-19
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-010 · Autorización de merge y despliegue separada de la revisión por agentes [Fase 5, principio en F1]

**Recomendación**
- La revisión de un agente es **informativa**: produce comentarios o checks.
- La autorización la dan los rulesets de GitHub:
  - checks requeridos;
  - revisión de code owner;
  - "aprobación del último push por alguien distinto de quien lo hizo";
  - merge queue con el evento `merge_group`.
- La aprobación humana obligatoria se fija según la clase de riesgo del cambio.
- El despliegue a producción requiere un environment protegido.

**Justificación**
- Es un principio del proyecto.
- S-GH: las reglas existen y son verificables.
- La filosofía de merge de S-OAI-HE p.10 depende explícitamente del contexto y no se puede trasladar tal cual a entornos corporativos.

**Alternativas**
- Merge automático sin humano en cambios de bajo riesgo: **posible en N3**, solo con una clasificación de riesgo determinista y auditoría.

**Riesgos**
- Fatiga de aprobación (S-VILA p.3, p.29: aprox. 93 % de aprobaciones).
- Mitigación: aprobar por riesgo y no por volumen.

**Validación**
- Los rulesets se exportan como código o checklist y la CLI comprueba su estado vía API. Está por verificar si es viable en la Fase 5.
