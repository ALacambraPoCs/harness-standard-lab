---
documento: F3-GUIA-F3.7-VAL
titulo: Validación de la F3.7 en el laboratorio
fecha: 2026-10-24
---

# Validación de la F3.7 en el laboratorio

**Objetivo:** comprobar en sesiones reales de Claude Code que los cambios D-041…D-046 hacen lo que dicen y medir cuántas confirmaciones pide un ciclo completo de tarea, frente a la F3.6.

| Evidencia | Qué demuestra | Decisión |
|---|---|---|
| E-020 | El modo automático no aparece con Shift+Tab | D-041 |
| E-021 | Con `HARNESS_STOP_MAX=0` el hook no bloquea un rojo intencionado | D-045 |
| E-022 | `gh api` pide confirmación y `gh auth token` se rechaza sin preguntar | D-042 |
| E-023 | El cierre usa `harness tasks close`, el PR lleva el bloque literal del verificador y `harness tasks` pasa en el primer push | D-044, D-046 |
| E-024 | Confirmaciones por paso, frente a las 26 de la F3.6 | D-043 |

Archivos: `/mnt/c/Users/alacambra/Desktop/Harness-engineering/f3.7-val/` (abajo, `$F`).

**Durante toda la prueba:** no elijas «Yes, and don't ask again» ni cambies de modo de permisos. **Anota cada confirmación**: qué comando o archivo era y en qué paso.

---

## 0. Preparación

```bash
# 0.1 Publicar la F3.7 (si no lo has hecho): merge del PR f3.7 y tag
cd ~/Projects/harness-standard-lab
git switch main && git pull && git tag cli-v0.5.0-rc.1 && git push origin cli-v0.5.0-rc.1

# 0.2 Actualizar la CLI local
~/.venvs/harness/bin/pip install --force-reinstall --no-deps \
  "git+https://github.com/ALacambraPoCs/harness-standard-lab@cli-v0.5.0-rc.1"
harness --version                        # harness 0.5.0rc1

# 0.3 Comprobar que no hay permisos guardados que falseen la medición
cd ~/Projects/harness-example-greenfield
cat .claude/settings.local.json 2>/dev/null || echo "sin settings.local.json"
grep -n '"allow"' -A10 ~/.claude/settings.json 2>/dev/null || echo "sin allow de usuario"
```

Si aparece alguna regla `allow` (sobre todo `Bash(...)`), envíamela antes de seguir: cambiaría el recuento.

## 1. Issue de T-0006

`harness-example-greenfield` → **New issue**:
- **Título:** `T-0006 · Descuento porcentual en total()`
- **Cuerpo:** `Espejo de docs/plans/active/T-0006-descuento.md (X-01).`

Debe salir con el número **#12**. Si no, antes del commit del paso 2 ejecuta `sed -i 's/^issue: 12$/issue: N/' docs/plans/active/T-0006-descuento.md` y `harness tasks index --write`.

## 2. PR de adopción del estándar 0.5.0 (será el #13)

```bash
cd ~/Projects/harness-example-greenfield
F=/mnt/c/Users/alacambra/Desktop/Harness-engineering/f3.7-val
git switch main && git pull && git switch -c adoptar-0.5
git am $F/ej-5-adoptar-0.5.patch
git push -u origin adoptar-0.5
```

- **Cuerpo del PR:** el contenido de `$F/pr-adopcion.md`.
- **Esperado:** los dos checks requeridos en verde. Fusiona. La issue #12 pasa a `status:in_progress`.

## 3. Sesión A · TDD con el hook suspendido (E-020, E-021)

```bash
git switch main && git pull && git switch -c t-0006
HARNESS_STOP_MAX=0 claude
```

**3a · Modo automático (E-020).** Pulsa **Shift+Tab** varias veces y anota los modos por los que pasa. Esperado: **no aparece `auto`**. Vuelve al modo inicial.

📸 Captura de un modo distinto del inicial; con anotar la lista de modos basta.

**3b · Rojo intencionado (E-021).** Escribe:

> Trabaja en la tarea T-0006 (docs/plans/active/T-0006-descuento.md). De momento escribe **solo** la prueba `test_descuento` en tests/test_app.py, sin implementar el descuento, y da el trabajo por terminado.

Esperado: Claude termina **sin** el bloqueo «No des el trabajo por terminado…». Con **ctrl+o** debería verse el aviso «verificar-al-terminar suspendido…» con la prueba que falla.

📸 Captura del final del turno (y de ctrl+o si muestra el aviso).

Sal con `/exit`.

## 4. Sesión B · implementación, reglas de gh y cierre (E-022, E-023)

```bash
claude
```

**4a · Implementación.** Escribe:

> Implementa el descuento de T-0006 para que pase test_descuento y el resto de pruebas.

Esperado: al terminar, el hook no dice nada (check en verde).

**4b · Reglas de `gh` (E-022).** Escribe, una por una:

> Ejecuta `gh api repos/ALacambraPoCs/harness-example-greenfield --jq .default_branch`

Esperado: **pide confirmación**. Responde **No**.

> Ejecuta `gh auth token`

Esperado: **se rechaza sin preguntar** (Claude te dirá que está denegado). Si te pide confirmación, responde **No** y anótalo: sería un hallazgo.

**4c · Verificador.** Escribe:

> Usa el subagente verificador para T-0006.

Esperado: la respuesta del subagente es un bloque entre `<!-- verificador:inicio -->` y `<!-- verificador:fin -->`.

**4d · Cierre (E-023).** Escribe:

> Cierra la tarea T-0006 siguiendo la skill cerrar-tarea.

Esperado:
- abre el PR en borrador (será el **#14**) y después ejecuta `harness tasks close T-0006 --pr 14 --resultado "…"` **sin pedir confirmación**;
- no edita a mano el archivo de la tarea;
- el cuerpo del PR tiene `T-0006`, `Closes #12` y, en Evidencia, el bloque literal del verificador;
- no te pide confirmar su plan antes del `git push` (solo la confirmación de la regla `ask`);
- `tasks / harness tasks` en verde **en el primer push del cierre**.

📸 Capturas de los checks del PR #14 y del cuerpo del PR (sección Evidencia). Fusiona. La issue #12 se cierra y recibe el comentario de X-01.

## 5. Sesión C · cerrar T-0005

```bash
git switch main && git pull && git switch -c cerrar-t-0005
claude
```

> Cierra la tarea T-0005 siguiendo la skill cerrar-tarea.

Será el PR **#15**. Sus criterios (`harness check --strict` y `harness tasks index --check`) están en `allow`, así que esperamos menos confirmaciones que con T-0003 (7). Fusiona cuando esté en verde.

## 6. Qué me tienes que enviar

1. Lista de modos de Shift+Tab (3a) y capturas de 3b, 4b, 4d.
2. **Confirmaciones por paso** (3b, 4a, 4b, 4c, 4d, 5), con el comando o archivo de cada una. Referencia F3.6: implementación 1, verificador 5, cierre de T-0004 10, cierre de T-0003 7.
3. Si algún PR necesitó más de un push para ponerse en verde, y por qué.
4. Cualquier comportamiento inesperado.

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `auto` sigue apareciendo con Shift+Tab | Versión de Claude Code o una configuración de mayor precedencia | `claude --version` y `/status` (fuentes de configuración); envíamelo |
| En 3b el hook bloquea | `HARNESS_STOP_MAX` no llegó al entorno de Claude Code | Comprueba con `echo $HARNESS_STOP_MAX` en otra terminal lanzada igual; anótalo como hallazgo |
| `harness tasks close` pide confirmación | La regla `allow` no aplica: carpeta sin confianza o CLI invocada con otra forma (p. ej. `~/.local/bin/harness`) | Anota el comando exacto que mostró el diálogo |
| La skill edita el archivo de la tarea a mano | La skill antigua sigue cargada | Comprueba `harness components list` (cerrar-tarea 0.2.0) y reinicia la sesión |
