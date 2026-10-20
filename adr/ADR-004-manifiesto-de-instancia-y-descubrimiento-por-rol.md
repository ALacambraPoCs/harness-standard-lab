---
id: ADR-004
titulo: "Manifiesto de instancia y descubrimiento por roles"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-004 · Manifiesto de instancia y descubrimiento por roles [APROBADO 2026-10-19]

**Recomendación**
- `.harness/manifest.yaml` es obligatorio y se valida con JSON Schema.
- Contiene: versión del estándar, nivel de conformidad, adaptadores con su versión mínima, contrato de comandos, roles cuya ruta difiere de la ruta por defecto, ruta del mapa de segmentos y waivers con caducidad.
- La CLI valida por **rol**, no por nombre fijo, y siempre con esquemas o anclas estructurales en lugar de títulos.

**Justificación**
- Los validadores existentes fallan por depender de nombres y del idioma (F0-01 §6).
- Los brownfield necesitan poder declarar dónde está ya cada cosa.

**Alternativas**
- (a) Convención estricta sin manifiesto: es más simple, pero bloquea la adopción en brownfield.
- (b) Configurar dentro de `package.json` o `pyproject`: depende del stack.

**Riesgos**
- Que el manifiesto se use para declarar excepciones sin límite.
- Mitigación: los waivers requieren aprobador y fecha de caducidad, y las rutas alternativas solo son válidas para roles que lo permitan.

**Evidencia**
- Los fallos de `validate-harness.mjs` y `audit-harness.sh` documentados en F0-01 §6.

**Validación**
- El mismo repositorio de ejemplo pasa la validación con rutas por defecto y con rutas alternativas declaradas.
