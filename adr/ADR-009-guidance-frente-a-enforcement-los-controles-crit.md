---
id: ADR-009
titulo: "Guidance frente a enforcement: los controles críticos viven en la plataforma y en la CI"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-009 · Guidance frente a enforcement: los controles críticos viven en la plataforma y en la CI [APROBADO 2026-10-19]

**Recomendación**
- Las instrucciones (AGENTS.md, skills) **solo** guían.
- Todo requisito de seguridad, integridad o merge se impone en tres capas:
  1. Permisos y sandbox del agente (deny-first).
  2. Hooks `command` deterministas, como respuesta rápida en local.
  3. **CI y rulesets de GitHub como autoridad final.**
- Los hooks de tipo `prompt` o `agent` no cuentan como control.
- Se incluye un presupuesto de tamaño medible para las instrucciones (líneas o bytes por archivo y en total cargado), con valores por defecto ajustables.

**Justificación**
- S-CC-MEM: las instrucciones son "context, not enforced configuration".
- S-VILA p.20: el cumplimiento es probabilístico.
- S-CC-SET: las reglas de Bash no son una frontera de seguridad.
- Los hooks locales se pueden desactivar o eludir. La CI no, si es un check requerido.

**Alternativas**
- Confiar en los hooks locales: no se puede verificar desde el servidor.

**Riesgos**
- Si la CI es lenta, el ciclo de feedback se alarga.
- Mitigación: hooks locales con la misma lógica que la CI, que da la autoridad final.

**Evidencia**
- S-CC-MEM, S-CC-SET (permissions, hooks), S-VILA p.13-14 y p.20, S-OAI-HE p.8-10.

**Validación**
- Prueba adversarial: un agente intenta un cambio prohibido con el hook desactivado y la CI lo rechaza.
