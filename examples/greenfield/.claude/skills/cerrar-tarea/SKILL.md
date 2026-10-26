---
name: cerrar-tarea
description: Cierra una tarea T-NNNN en el PR que la completa, según ADR-016 (abrir el PR, harness tasks close, evidencia del verificador y Closes de la issue) y la verifica en local antes de subirla. Úsala cuando el trabajo de la tarea está hecho y sus criterios de aceptación pasan.
license: Propietaria (uso interno)
compatibility: Requiere git y la CLI harness (cli-v0.5.0 o posterior). gh es opcional; sin gh, la persona abre el PR y da su número.
metadata:
  harness-perfil: portable
  harness-componente: cerrar-tarea
  harness-version: 0.2.0
---

# Cerrar una tarea (ADR-016)

Una tarea solo llega a `done` en el PR que la completa. La CI vuelve a ejecutar sus criterios de aceptación y bloquea el merge si alguno falla. Esta skill prepara ese PR **sin errores de forma**. Que el trabajo sea correcto lo decide la CI, no esta skill.

## Antes de empezar (si algo no se cumple, para y avisa a la persona)
- La tarea está en `docs/plans/active/` con `status: in_progress` o `in_review`.
- Todos los criterios ejecutables pasan en local. Usa el subagente `verificador` si está instalado; si no, ejecuta cada `acceptance[].check`.
- Estás en la rama de la tarea, no en `main`.
- **No cambies los criterios de aceptación para que pasen.** Si un criterio es incorrecto, para y pídeselo a la persona responsable. Ese cambio va en su propio commit y se explica en el PR.

## Pasos (en este orden: el número del PR es necesario antes del paso 2)
1. **Abre el PR y conoce su número.** Haz commit del trabajo y `git push` (Claude Code te pedirá confirmación: **no pidas otra confirmación tú**).
   - Con `gh`: `gh pr create --draft --fill` y `gh pr view --json number -q .number`.
   - Sin `gh`, o si falla: pide a la persona que abra el PR en borrador y te diga su número. No uses `gh api` para rodearlo.
2. **Cierra la tarea con la CLI** (no edites el archivo a mano):
   `harness tasks close T-NNNN --pr <número> --resultado "<qué se logró frente al objetivo y qué queda pendiente>"`
   - Mueve el archivo a `completed/`, pone `status: done` y `done_pr`, añade la línea de progreso con fecha y autor, y regenera el índice. Lista los archivos que ha modificado.
   - Si la tarea tiene criterios `check: manual`, añade `--verified-by @persona` solo si sabes quién lo ha verificado y aprobará el PR. Si no lo sabes, no lo inventes: el comando se detendrá y debes avisar a la persona.
   - Si el comando termina con código 2, no ha modificado nada: lee el motivo, corrígelo o avisa.
3. **Cuerpo del PR** (plantilla):
   - `harness:tarea` con `T-NNNN`; si la tarea tiene `issue: <n>`, añade `Closes #<n>`;
   - en `harness:evidencia`, el informe del verificador **copiado literal**, de `<!-- verificador:inicio -->` a `<!-- verificador:fin -->`, sin resumirlo. Si no hay verificador, los comandos ejecutados con su código de salida.
4. **Verifica en local, igual que la CI:**
   - `harness tasks validate --base origin/main --pr-number <número> --run-acceptance`
   - `harness pr check --base origin/main --body-file <archivo con el cuerpo del PR>`
   - `harness tasks index --check`
5. **Sube y deja el PR listo para revisión:** commit de los archivos que listó el paso 2, `git push` y `gh pr ready` (o pide a la persona que lo marque como listo). **No fusiones:** la CI decide y una persona fusiona.

## Errores frecuentes
| Error de la CI | Causa | Arreglo |
|---|---|---|
| `tasks.done-pr` | `done_pr` no es el número de este PR | Paso 1 antes del 2 |
| `tasks.transition` | La tarea pasa de `ready` a `done` | Primero `in_progress`, en otro PR |
| `tasks.acceptance` | Un criterio falla en la CI o un `manual` sin aprobador | Corrige el código o consigue la aprobación; no el criterio |
| `pr.issue` | La tarea tiene `issue` y falta `Closes #n` | Paso 3 |
| `tasks.index` | Índice desactualizado | Lo regenera el paso 2; no edites `INDEX.md` a mano |
