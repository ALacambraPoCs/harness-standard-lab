---
name: cerrar-tarea
description: Cierra una tarea T-NNNN en el PR que la completa, según ADR-016 (cuerpo del PR desde la plantilla, PR en borrador, harness tasks close, evidencia del verificador y Closes de la issue) y la verifica en local antes de subirla. Úsala cuando el trabajo de la tarea está hecho y sus criterios de aceptación pasan.
license: Propietaria (uso interno)
compatibility: Requiere git y la CLI harness (cli-v0.5.0 o posterior). gh es opcional; sin gh, la persona abre el PR y da su número.
metadata:
  harness-perfil: portable
  harness-componente: cerrar-tarea
  harness-version: 0.3.0
---

# Cerrar una tarea (ADR-016)

Una tarea solo llega a `done` en el PR que la completa. La CI vuelve a ejecutar sus criterios de aceptación y bloquea el merge si alguno falla. Esta skill prepara ese PR **sin errores de forma**. Que el trabajo sea correcto lo decide la CI, no esta skill.

## Antes de empezar (si algo no se cumple, para y avisa a la persona)
- La tarea está en `docs/plans/active/` con `status: in_progress` o `in_review`.
- Todos los criterios ejecutables pasan en local. Usa el subagente `verificador` si está instalado; si no, ejecuta cada `acceptance[].check`.
- Estás en la rama de la tarea, no en `main`.
- **No cambies los criterios de aceptación para que pasen.** Si un criterio es incorrecto, para y pídeselo a la persona responsable. Ese cambio va en su propio commit y se explica en el PR.

## Cómo ejecutar comandos
- **Un comando por llamada**, tal como aparece en esta skill. La herramienta ya te devuelve el código de salida.
- **Sin envoltorios:** nada de `; echo $?`, `| tail`, `2>&1 |` ni `command -v`. Hacen que se pida confirmación aunque el comando esté permitido y pueden ocultar un fallo.
- **Sin encadenar** comandos distintos con `&&` o `;`: si uno falla, tienes que saber cuál.
- Para escribir archivos (el cuerpo del PR) usa la herramienta de edición de archivos, no `cat > archivo <<EOF`.
- Si un comando falla, lee su salida antes de seguir. No pases al paso siguiente dando por bueno el anterior.

## Pasos
1. **Escribe el cuerpo del PR** en un archivo temporal, a partir de `.github/pull_request_template.md`:
   - conserva las anclas `<!-- harness:… -->` **y las etiquetas** («Tarea:», «Riesgo:», «Evidencia:»…); rellena solo los valores;
   - `harness:tarea`: `T-NNNN` y, si la tarea tiene `issue: <n>`, `Closes #<n>`;
   - `harness:evidencia`: el informe del verificador **copiado literal**, de `<!-- verificador:inicio -->` a `<!-- verificador:fin -->`. Sin verificador, los comandos ejecutados con su código de salida.
2. **Valida el cuerpo:** `harness pr check --base origin/main --body-file <archivo>`.
3. **Sube la rama y abre el PR ya con su cuerpo:**
   - Si la rama no tiene commits respecto a `origin/main` (`git rev-list --count origin/main..HEAD` da 0, porque la tarea ya estaba hecha), crea uno vacío: `git commit --allow-empty -m "T-NNNN: abrir el PR de cierre"`.
   - `git push -u origin <rama>` (Claude Code te pedirá confirmación: **no pidas otra tú**).
   - `gh pr create --draft --title "T-NNNN: <título de la tarea>" --body-file <archivo>`. El número del PR aparece en la URL que devuelve.
   - Sin `gh`, o si falla: pide a la persona que abra el PR en borrador con ese cuerpo y te diga su número. No uses `gh api` para rodearlo.
4. **Cierra la tarea con la CLI** (no edites el archivo a mano):
   `harness tasks close T-NNNN --pr <número> --resultado "<qué se logró frente al objetivo y qué queda pendiente>"`
   - Mueve el archivo a `completed/`, pone `status: done` y `done_pr`, añade la línea de progreso con fecha y autor, y regenera el índice. Lista los archivos que ha modificado.
   - Si la tarea tiene criterios `check: manual`, añade `--verified-by @persona` solo si sabes quién lo ha verificado y aprobará el PR. Si no lo sabes, no lo inventes: el comando se detendrá y debes avisar a la persona.
   - Si termina con código 2, no ha modificado nada: lee el motivo, corrígelo o avisa.
5. **Verifica en local, igual que la CI:**
   - `git add` de los archivos que listó el paso 4 y `git commit -m "T-NNNN: cerrar la tarea (PR #<número>)"`
   - `harness tasks validate --base origin/main --pr-number <número> --run-acceptance`
   - `harness pr check --base origin/main --body-file <archivo>`
   - `harness tasks index --check`
6. **Sube y deja el PR listo para revisión:** `git push` y `gh pr ready <número>` (o pide a la persona que lo marque como listo). **No fusiones:** la CI decide y una persona fusiona.

**No uses `gh pr edit`.** Si el cuerpo tiene que cambiar después de abrir el PR, pide a la persona que lo edite en GitHub y dile la ruta del archivo con el cuerpo.

## Errores frecuentes
| Error de la CI | Causa | Arreglo |
|---|---|---|
| `tasks.done-pr` | `done_pr` no es el número de este PR | Paso 3 antes del 4 |
| `tasks.transition` | La tarea pasa de `ready` a `done` | Primero `in_progress`, en otro PR |
| `tasks.acceptance` | Un criterio falla en la CI o un `manual` sin aprobador | Corrige el código o consigue la aprobación; no el criterio |
| `pr.issue` | La tarea tiene `issue` y falta `Closes #n` | Paso 1 |
| `pr.anchors` o `pr.task` | El cuerpo del PR no sigue la plantilla | Paso 1; no lo cambies con `gh pr edit` |
| `tasks.index` | Índice desactualizado | Lo regenera el paso 4; no edites `INDEX.md` a mano |
