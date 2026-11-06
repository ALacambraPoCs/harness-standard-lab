---
documento: F5-GUIA-CIERRE
titulo: Cierre de la Fase 5 · Adopción de 0.10.0 y medición C-8
fecha: 2026-11-06
depende_de: [D-077, D-078]
---

# Cierre de la Fase 5 · Adopción de 0.10.0 y medición C-8

**Objetivo.** Comprobar en el laboratorio las correcciones C-1…C-7. Ejercitar la clase de riesgo `medio` (criterio 4 del plan) y medir las confirmaciones con el sandbox activo y la sesión completa anotada (C-8, D-070).

**Archivos:** `/mnt/c/Users/alacambra/Desktop/Harness-engineering/f5-cierre/` (abajo, `$F`).

| Paso | Qué | Evidencia |
|---|---|---|
| 0 | Estándar 0.10.0 y `cli-v0.10.0-rc.1` | Tag y CLI local |
| 1 | PR de adopción T-0010 (riesgo alto) | Puerta, despliegue con `despliegue-pages` 0.2.2 |
| 2 | C-1 contra GitHub real | `platform check` y dos `gh api` |
| 3 | C-5: PR adversarial de nuevo | La puerta **espera** (antes se saltaba) |
| 4 | Sesión D: T-0011 (riesgo `medio`, `ready → done` en un PR) | Recuento completo de confirmaciones |
| 5 | Sesión E: cerrar T-0010 | Recuento completo |

**Durante las sesiones D y E:** apunta **todos** los diálogos, desde el primero, con el comando o archivo de cada uno.

## 0. Estándar

```bash
cd ~/Projects/harness-standard-lab
F=/mnt/c/Users/alacambra/Desktop/Harness-engineering/f5-cierre
git switch main && git pull && git switch -c f5-cierre
git am $F/f5-cierre.patch          # 2 commits: validación F5.7 y cierre C-1…C-7
git push -u origin f5-cierre       # PR → test (3.11/3.12/3.13) → merge
git switch main && git pull && git tag cli-v0.10.0-rc.1 && git push origin cli-v0.10.0-rc.1
~/.venvs/harness/bin/pip install --force-reinstall --no-deps \
  "git+https://github.com/ALacambraPoCs/harness-standard-lab@cli-v0.10.0-rc.1"
harness --version                  # 0.10.0rc1
```

## 1. Adopción en el ejemplo (T-0010, riesgo alto)

```bash
cd ~/Projects/harness-example-greenfield
git switch main && git pull && git switch -c adoptar-0-10
git am $F/ej-f5-cierre.patch && git push -u origin adoptar-0-10
gh pr create --base main --head adoptar-0-10 --title "T-0010: adoptar el estándar 0.10.0 (cierre de la Fase 5)" --body-file $F/pr-T0010.md
```

Lo esperado:
- `harness check` y `harness tasks` en ✅.
- La puerta ⏸. Apruébala con el comentario «F5 cierre: adopción 0.10.0» y fusiona.
- Tras el merge, `despliegue-pages` en verde. En sus jobs, el paso de `preparar` muestra el shell `bash --noprofile --norc -eo pipefail`.

## 2. C-1 contra GitHub real

```bash
R=ALacambraPoCs/harness-example-greenfield
harness platform check --repo $R
gh api repos/$R/environments/aprobacion-riesgo-alto --jq '{can_admins_bypass}'
gh api repos/$R/environments/github-pages --jq '{can_admins_bypass}'
gh api repos/$R/rules/branches/main --jq '.[] | select(.type=="required_status_checks") | .parameters.required_status_checks'
```

Lo esperado:
- **0 errores.** Si la API no devuelve `can_admins_bypass`, sale un **aviso** `platform.admin-bypass`.
- `can_admins_bypass: false` en los dos environments.
- Los tres checks con `integration_id`. Busco **15368**, que confirmaría el valor de las plantillas.

## 3. C-5: la puerta falla cerrada

Repite el PR adversarial de la F5.7:

```bash
git switch main && git pull && git switch -c prueba-adversarial-2
git am /mnt/c/Users/alacambra/Desktop/Harness-engineering/f5.7/ej-f5.7-adversarial.patch
git push -u origin prueba-adversarial-2
gh pr create --base main --head prueba-adversarial-2 --title "Ajuste menor de documentación" \
  --body-file /mnt/c/Users/alacambra/Desktop/Harness-engineering/f5.7/pr-adversarial.md
```

Lo esperado:
- Los mismos errores que en la F5.7.
- **La puerta ⏸ esperando**, no saltada: la clase `alto` se calcula aunque `pr check` falle.
- **No apruebes.** Cierra el PR y borra la rama:

```bash
git switch main && git branch -D prueba-adversarial-2 && git push origin --delete prueba-adversarial-2
```

## 4. Sesión D · T-0011 (riesgo `medio`)

```bash
git switch main && git pull
cat .claude/settings.local.json 2>/dev/null || echo "sin settings.local.json"
claude
```

Comprueba `/sandbox` (modo *auto-allow*) y pide:

> Trabaja en T-0011 (docs/plans/active/T-0011-pruebas-por-modulo.md) siguiendo AGENTS.md: impleméntala, abre el PR y ciérrala con cerrar-tarea en ese mismo PR.

Lo esperado:
- **Sin PR previo** para pasar a `in_progress`: `ready → done` en un PR (C-4).
- `harness pr risk` da **`medio`** («prueba renombrada»).
- La puerta, saltada.
- `harness tasks` vuelve a ejecutar AC1 y AC2.
- El cuerpo del PR copia las señales de riesgo (skill 0.3.1).
- Fusiona sin aprobación (N1, `medio`: checks y revisión informativa).

**Anota** cada diálogo, con el comando o archivo y su motivo.

## 5. Sesión E · cerrar T-0010

Sesión nueva:

> Cierra T-0010 con la skill cerrar-tarea en la rama `cerrar-t-0010`.

Lo esperado: riesgo `alto` por la tarea, así que la puerta espera. Apruébala y fusiona.

**Anota** los diálogos igual que en la sesión D.

## 6. Qué enviarme

| Paso | Evidencia |
|---|---|
| 1 | Checks del PR, enlace al run de `despliegue-pages` |
| 2 | Salida de los cuatro comandos |
| 3 | Captura de los checks, con la puerta esperando |
| 4 y 5 | Lista completa de diálogos de cada sesión, resumen final del agente y checks de cada PR |

Con esto escribo el **informe de la Fase 5** y el plan de la Fase 6.
