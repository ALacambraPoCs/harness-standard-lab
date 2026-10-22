# F2.6 · Prueba de extremo a extremo de N1 en el laboratorio

Objetivo: demostrar en GitHub, con evidencia, que una tarea solo llega a `done` si la CI vuelve a ejecutar sus criterios de aceptación (ADR-016), y que la issue espejo se actualiza y se cierra (X-01).

Numeración prevista (issues y PR comparten contador en GitHub; el último usado en el ejemplo es el #3):

| Nº | Qué |
|---|---|
| #4 | Issue de T-0002 |
| #5 | PR A — adoptar N1 (T-0001 en curso, T-0002 lista) |
| #6 | PR B — T-0001 a done, T-0002 en curso |
| #7 | PR C — T-0002: primero falla, luego pasa |

Si algún número no coincide, ajusta antes de hacer commit (ver «Si cambia la numeración»).

Carpeta de los archivos: `/mnt/c/Users/alacambra/Desktop/Harness-engineering/f2.6/` (abajo, `$F`).

---

## 0. Repo central: registrar la aprobación y el tag

```bash
cd ~/Projects/harness-standard-lab
git switch main && git pull
git tag cli-v0.2.0-rc.2 && git push origin cli-v0.2.0-rc.2      # lo necesita el ejemplo
F=/mnt/c/Users/alacambra/Desktop/Harness-engineering/f2.6
git switch -c f2.6
git apply --index $F/central-f2.6.patch
git commit -m "F2.6: aprobar requisitos 0.2.0 (D-029, D-030), ejemplo greenfield a N1, E-009"
git push -u origin f2.6       # PR → 3 checks verdes → merge
```

El tag apunta al commit de F2.5 ya fusionado; el PR de este paso solo cambia documentación, estados y la copia de referencia del ejemplo.

## 1. Issue #4 (antes que nada)

En `ALacambraPoCs/harness-example-greenfield` → *Issues* → *New issue*:
- Título: `T-0002 · Rechazar cantidades negativas en total()`
- Cuerpo: `Espejo de docs/plans/active/T-0002-cantidad-negativa.md. La fuente de verdad es el archivo (X-01).`

Comprueba que recibe el número **#4**.

## 2. PR A (#5) — adoptar N1

```bash
cd ~/Projects/harness-example-greenfield
git switch main && git pull
git switch -c adoptar-n1
git apply --index $F/ej-1-adoptar-n1.patch
git commit -m "T-0001: adoptar N1 del estándar 0.2.0"
git push -u origin adoptar-n1
```

Abre el PR y **pega como cuerpo** el contenido de `$F/pr-A.md`. GitHub aún no rellena la plantilla, porque solo la toma de la rama por defecto.

Esperado:
- `harness / conformance / harness check` en verde;
- `harness-tasks / tasks / harness tasks` en verde (es la primera vez que aparece).

**Antes de fusionar**, en el ruleset `main-protegida` → *Require status checks* → añade `tasks / harness tasks`. Así se evita repetir E-005 (fusionar antes de que exista el check requerido). Después, fusiona.

Tras el merge, el job `harness tasks · issues (X-01)` se ejecuta en `main`. La issue #4 debe quedar con la etiqueta `status:ready` y asignada a ti.

## 3. PR B (#6) — T-0001 pasa a done

```bash
git switch main && git pull
git switch -c cerrar-t-0001
git apply --index $F/ej-2-cerrar-t-0001.patch
git commit -m "T-0001 done; T-0002 en curso"
git push -u origin cerrar-t-0001
```

Cuerpo del PR: ahora la plantilla ya aparece sola. Sustitúyela por `$F/pr-B.md`.

Esperado: `harness tasks` en verde. En el log del paso «Validar tareas…» no hay errores, porque ha ejecutado `harness check --strict` y `harness tasks index --check` como criterios de T-0001. Fusiona. La issue #4 pasa a `status:in_progress`.

## 4. PR C (#7) — T-0002: la CI rechaza un done falso

**4a. Primer push: done declarado sin implementar.**

```bash
git switch main && git pull
git switch -c t-0002
git apply --index $F/ej-3a-t-0002-sin-implementar.patch
git commit -m "T-0002: prueba de cantidad negativa y paso a done (sin implementar)"
git push -u origin t-0002
```

Cuerpo: `$F/pr-C.md` (incluye `Closes #4`).

Esperado:
- `harness tasks` en **rojo**, con `tasks.acceptance`: AC1 y AC2 terminan con código 1;
- el merge queda **bloqueado**;
- `harness check` (conformidad) sigue en verde, porque la instancia es conforme: lo que falla es la verificación de terminado.

📸 Captura: PR con el check rojo y el merge bloqueado (evidencia principal de ADR-016).

**4b. Segundo push: implementación.**

```bash
git apply --index $F/ej-3b-t-0002-implementacion.patch
git commit -m "T-0002: validar cantidades en total()"
git push
```

Esperado: `harness tasks` en verde. Fusiona.

Tras el merge:
- GitHub cierra la issue #4 por `Closes #4`;
- el job X-01 pone `status:done` y añade un comentario «✅ T-0002 pasa a done … PR #7 … Ejecución: <enlace>».

📸 Captura: issue #4 cerrada con la etiqueta y el comentario.

## 5. Qué me tienes que enviar

1. Captura del PR #7 en rojo con el merge bloqueado (paso 4a).
2. Captura del PR #7 en verde o fusionado (paso 4b).
3. Captura de la issue #4 (etiqueta `status:done`, comentario y cerrada).
4. Si algo falla: el log del paso que falla.

Con eso registro las evidencias E-010 a E-012 y cierro la Fase 2.

## Si cambia la numeración

- Issue distinta de #4: en `ej-1`, antes del commit, `sed -i 's/^issue: 4$/issue: N/' docs/plans/active/T-0002-cantidad-negativa.md`. En `pr-C.md`, cambia `Closes #4`.
- PR B distinto de #6: después de abrirlo, `sed -i 's/^done_pr: 6$/done_pr: N/' docs/plans/completed/T-0001-adoptar-n1.md`, luego commit y push.
- PR C distinto de #7: igual, con `docs/plans/completed/T-0002-cantidad-negativa.md`. Aplícalo antes del commit 4b para que el `git apply` de 4b no falle; si ya lo has aplicado, edita el archivo y añade un commit más.

Si `done_pr` no coincide con el PR, `harness tasks` falla con `tasks.done-pr`. Es el comportamiento esperado.

## Limpieza pendiente

Con los repos públicos (D-018) ya no hace falta el secreto `HARNESS_STANDARD_TOKEN`. El PR A lo deja de usar. Después del paso 2:
- borra el secreto en *Settings → Secrets and variables → Actions*;
- revoca el PAT en tu cuenta (*Settings → Developer settings → Fine-grained tokens*).
