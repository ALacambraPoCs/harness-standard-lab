---
id: ADR-016
titulo: "La transición a done ocurre en el propio PR y la verifica un check requerido"
estado: aprobado
fecha: 2026-10-21
origen: F2.4 (concreta ADR-005 sobre cómo "solo la CI marca done")
---

## ADR-016 · La transición a `done` ocurre en el propio PR y la verifica un check requerido

**Problema.** ADR-005 exige que solo la CI pueda marcar una tarea como `done`, con evidencia. La forma obvia de hacerlo (un job posterior al merge que escribe `done` en `main`) choca con dos hechos verificados:

- `main` está protegida por ruleset: todo cambio pasa por PR (E-003). Para que un bot escribiera directamente habría que darle permiso para saltarse el ruleset. Eso es más privilegio y un camino de escritura fuera de la revisión.
- Los commits o PR creados con el `GITHUB_TOKEN` no disparan otros workflows. Un PR automático "cerrar T-NNNN" nunca ejecutaría los checks requeridos y quedaría bloqueado. Lo indica la documentación de GitHub Actions, citada en la de `claude-code-action`, según el informe de especificaciones de F0.

**Recomendación**
- El PR que completa la tarea **incluye** la transición: mueve el archivo a `completed/`, pone `status: done` y `done_pr: <número del PR>`, y rellena la sección de resultado.
- La puede escribir una persona o un agente. **No vale como evidencia por sí misma**: el check requerido `harness tasks` del PR **vuelve a ejecutar** todos los criterios de aceptación ejecutables de esa tarea y solo pasa si todos terminan con código 0.
- Los criterios `manual` necesitan `verified_by` con una persona que haya **aprobado** el PR, comprobado por la API.
- El ruleset impide fusionar si el check falla (E-006). Así, `done` en `main` implica que la CI verificó la aceptación sobre ese mismo código.
- **Evidencia trazable:** `done_pr` lleva al PR; el PR lleva a su commit de merge y a las ejecuciones del check, que GitHub conserva y asocia al commit. Con X-01 activo, un job posterior al merge comenta en la issue el enlace al run. Ese job solo tiene `issues: write` y no escribe en el repositorio.

**Alternativas**

| Alternativa | Por qué se descarta |
|---|---|
| Job posterior al merge que hace commit de `done` en `main`, con el bot autorizado a saltarse el ruleset | Más privilegio, escritura sin revisión y dependencia de que el bot pueda figurar en la lista de excepciones del ruleset. No verificado en este plan |
| Job posterior al merge que abre un PR automático de cierre | Con `GITHUB_TOKEN` no se disparan los checks requeridos. Exigiría un token de usuario o una GitHub App con más alcance |
| Estado `done` calculado, nunca escrito: una tarea está hecha si existe un PR fusionado que la referencia | El repositorio deja de ser la fuente de verdad legible (P1). El agente no lo vería sin consultar la API |

**Riesgos y supuestos**
- **Pruebas frágiles o con estado.** Si un criterio pasa en el PR y falla después en `main`, la tarea debería pasar a `regressed`. La detección automática programada llega en la Fase 6. Hasta entonces el paso a `regressed` lo hace una persona mediante PR.
- **El agente ejecuta los comandos de aceptación del PR en CI.** Es lo mismo que ejecutar cualquier código del PR: el job tiene `contents: read`, ningún secreto y un tiempo máximo.
- **Criterios demasiado débiles** (por ejemplo, `check: "true"`). La CLI no puede juzgar si un criterio es bueno. Lo decide la revisión humana, ponderada por la clase de riesgo (Fase 5).

**Evidencia**
- E-003 y E-006: ruleset y check requerido.
- S-GH: las palabras de cierre de issues solo se aplican si el PR va a la rama por defecto.
- Patrón de *pass-gate* de S-LHE L08, ahora con verificación real en lugar de texto libre.

**Validación**
- Prueba en el laboratorio (F2.6):
  - un PR que marca `done` con un criterio que falla queda bloqueado;
  - con el criterio corregido, se puede fusionar;
  - la issue enlazada se cierra y recibe el enlace al run.
