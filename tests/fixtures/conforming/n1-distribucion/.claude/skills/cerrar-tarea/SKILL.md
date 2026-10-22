---
name: cerrar-tarea
description: Cierra una tarea T-NNNN en el PR que la completa, según ADR-016 (mover a completed/, status done, done_pr, resultado, índice y Closes de la issue) y la verifica en local antes de subirla. Úsala cuando el trabajo de la tarea está hecho y sus criterios de aceptación pasan.
license: Propietaria (uso interno)
compatibility: Requiere git, la CLI harness (cli-v0.3.0 o posterior) y gh para conocer el número del PR.
metadata:
  harness-perfil: portable
  harness-componente: cerrar-tarea
  harness-version: 0.1.0
---

# Cerrar una tarea (ADR-016)

Una tarea solo llega a `done` en el PR que la completa. La CI vuelve a ejecutar sus criterios de aceptación y bloquea el merge si alguno falla. Esta skill prepara ese PR **sin errores de forma**. Que el trabajo sea correcto lo decide la CI, no esta skill.

## Antes de empezar (si algo no se cumple, para y avisa a la persona)
- La tarea está en `docs/plans/active/` con `status: in_progress` o `in_review`.
- Todos los criterios ejecutables pasan en local. Usa el subagente `verificador` si está instalado; si no, ejecuta cada `acceptance[].check`.
- Estás en la rama de la tarea, no en `main`.
- **No cambies los criterios de aceptación para que pasen.** Si un criterio es incorrecto, para y pídeselo a la persona responsable. Ese cambio va en su propio commit y se explica en el PR.

## Pasos
1. **Conoce el número del PR.** Si no existe, haz commit, `git push` (te pedirá confirmación) y ábrelo como borrador:
   `gh pr create --draft --fill`. Número: `gh pr view --json number -q .number`.
2. **Mueve el archivo:** `git mv docs/plans/active/T-NNNN-<slug>.md docs/plans/completed/`.
3. **Frontmatter:** `status: done` y `done_pr: <número>`.
   - En los criterios `check: manual`, pon en `verified_by` la persona que **lo ha verificado y aprobará el PR**. Si no lo sabes, no lo inventes: déjalo sin poner y avisa, y la CI lo bloqueará.
4. **Cuerpo de la tarea:**
   - en `harness:resultado`, qué se logró frente al objetivo y qué queda pendiente;
   - en `harness:progreso`, una línea con la fecha y «cerrada en el PR #N».
5. **Índice:** `harness tasks index --write`.
6. **Cuerpo del PR** (plantilla): `harness:tarea` con `T-NNNN`; si la tarea tiene `issue: <n>`, añade `Closes #<n>`; en `harness:evidencia`, el informe del verificador o los comandos con su resultado.
7. **Verifica en local, igual que la CI:**
   - `harness tasks validate --base origin/main --pr-number <número> --run-acceptance`
   - `harness pr check --base origin/main --body-file <archivo con el cuerpo del PR>`
   - `harness tasks index --check`
8. **Sube y deja el PR listo para revisión:** commit, `git push` y `gh pr ready`. **No fusiones:** la CI decide y una persona fusiona.

## Errores frecuentes
| Error de la CI | Causa | Arreglo |
|---|---|---|
| `tasks.done-pr` | `done_pr` no es el número de este PR | Paso 1 antes del 3 |
| `tasks.transition` | La tarea pasa de `ready` a `done` | Primero `in_progress`, en otro PR |
| `tasks.acceptance` | Un criterio falla en la CI o un `manual` sin aprobador | Corrige el código o consigue la aprobación; no el criterio |
| `pr.issue` | La tarea tiene `issue` y falta `Closes #n` | Paso 6 |
| `tasks.index` | Índice desactualizado | Paso 5 |
