---
documento: F3-GUIA-F3.6
titulo: F3.6 · Prueba en el laboratorio de los componentes con Claude Code
fecha: 2026-10-22
---

# F3.6 · Prueba en el laboratorio

**Objetivo:** demostrar en una sesión real de Claude Code (≥ 2.1.277) que los tres componentes del catálogo y la configuración deny-first funcionan como dicen sus fichas, con evidencia que se pueda comprobar.

| Evidencia | Qué demuestra | Componente o requisito |
|---|---|---|
| E-014 | Editar una ruta sensible pide confirmación | `settings.json` (HS-SEC-008) |
| E-015 | El agente no puede terminar con `check` en rojo | hook `verificar-al-terminar` |
| E-016 | El informe del verificador coincide con la CI | subagente `verificador` |
| E-017 | Claude carga la skill desde `.claude/skills/` y el PR de cierre pasa `harness tasks` en el primer push | skill `cerrar-tarea` (ADR-012, ADR-016) |
| E-018 | La CI de conformidad comprueba que no hay deriva | HS-CMP-009 (ADR-017) |

Archivos: `/mnt/c/Users/alacambra/Desktop/Harness-engineering/f3.6/` (abajo, `$F`).

---

## 0. Preparación en WSL (una sola vez)

```bash
# 0.1 Claude Code
claude --version                       # ≥ 2.1.277 (tienes 2.1.308)

# 0.2 CLI harness en local (la usan el hook y la skill)
python3 -m venv ~/.venvs/harness
~/.venvs/harness/bin/pip install "git+https://github.com/ALacambraPoCs/harness-standard-lab@cli-v0.4.0-rc.1"
mkdir -p ~/.local/bin && ln -sf ~/.venvs/harness/bin/harness ~/.local/bin/harness
harness --version                      # harness 0.4.0rc1
# Si `harness` no se encuentra, añade a ~/.bashrc:  export PATH="$HOME/.local/bin:$PATH"

# 0.3 GitHub CLI (la skill la usa para abrir el PR y conocer su número)
gh --version && gh auth status
```

Si no tienes `gh`, instálalo siguiendo las instrucciones de cli.github.com para Debian/Ubuntu, o abre tú el PR cuando la skill lo pida y dile a Claude su número.

**Claude Code se ejecuta en WSL, en la raíz del repositorio.** El hook usa `python3` y las reglas `/…` se anclan en el directorio donde arranca la sesión.

## 1. Issue de T-0004

`harness-example-greenfield` → **New issue**:
- **Título:** `T-0004 · Rechazar precios negativos en total()`
- **Cuerpo:** `Espejo de docs/plans/active/T-0004-precio-negativo.md (X-01).`

Debe salir con el número **#8**. Si no es así, antes del commit del paso 2 ejecuta `sed -i 's/^issue: 8$/issue: N/' docs/plans/active/T-0004-precio-negativo.md` y `harness tasks index --write`.

## 2. PR de adopción (será el #9)

```bash
cd ~/Projects/harness-example-greenfield
F=/mnt/c/Users/alacambra/Desktop/Harness-engineering/f3.6
git switch main && git pull && git switch -c adoptar-0.4
git apply --index $F/ej-4-adoptar-0.4.patch
git commit -m "T-0003: adoptar el estándar 0.4.0 y los componentes del catálogo"
git push -u origin adoptar-0.4
```

- **Cuerpo del PR:** el contenido de `$F/pr-adopcion.md`.
- **Resultado esperado:** los dos checks requeridos en verde. Fusiona.
- **Después:** la issue #8 pasa a `status:in_progress` (X-01).

📸 **E-018:** en el log de `harness / conformance / harness check`, la línea final con 0 errores. Si es posible, también la regla `core.components.drift` entre las ejecutadas (se ve con `-v`; si no aparece, no pasa nada).

## 3. Sesión de Claude Code: T-0004

```bash
git switch main && git pull && git switch -c t-0004
claude
```

Si aparece el diálogo de confianza de la carpeta, acéptalo: es tu repositorio.

**3a · Confirmación en una ruta sensible (E-014).** Escribe en Claude:

> Añade al final de AGENTS.md una línea que diga «prueba de permisos».

Esperado: Claude Code **pide confirmación** antes de editar AGENTS.md. Responde **No**.

📸 Captura del diálogo de confirmación.

**3b · El hook impide terminar con `check` en rojo (E-015).** Escribe:

> Trabaja en la tarea T-0004 (docs/plans/active/T-0004-precio-negativo.md). De momento escribe **solo** la prueba `test_precio_negativo` en tests/test_app.py, sin implementar la validación, y da el trabajo por terminado.

Esperado: al intentar terminar, el hook devuelve el error («No des el trabajo por terminado… intento 1 de 3» con la prueba que falla) y Claude **continúa**. Lo normal es que entonces implemente la validación. Déjale terminar.

📸 Captura del mensaje del hook en la sesión.

**3c · Verificador (E-016).** Escribe:

> Usa el subagente verificador para T-0004.

Esperado: un informe con el formato fijo (`check`, `test`, AC1 y AC2 con su código, y `RESULTADO: LISTO PARA REVISIÓN`).

📸 Captura del informe.

**3d · Cierre con la skill (E-017).** Escribe:

> Cierra la tarea T-0004 siguiendo la skill cerrar-tarea.

Esperado:
- Claude carga la skill.
- Pide confirmación para `git push`: apruébala (regla `ask`).
- Abre el PR en borrador (será el #10) y escribe `done_pr` con ese número.
- Mueve la tarea a `completed/`, regenera el índice y ejecuta en local `harness tasks validate … --run-acceptance` y `harness pr check`.
- Sube los cambios y marca el PR como listo.

Comprueba que el cuerpo del PR tiene `T-0004` y `Closes #8`. En GitHub, `tasks / harness tasks` debe salir **en verde en el primer push del cierre**.

📸 Captura de los checks del PR #10. Fusiónalo. La issue #8 se cierra y recibe el comentario de X-01.

## 4. Sesión de Claude Code: cerrar T-0003

```bash
git switch main && git pull && git switch -c cerrar-t-0003
claude
```

> Cierra la tarea T-0003 siguiendo la skill cerrar-tarea.

Su criterio AC1 es `harness check --strict`, así que la CI lo volverá a ejecutar en el PR (#11). Fusiona cuando esté en verde.

## 5. Qué me tienes que enviar

1. Las capturas E-014, E-015, E-016 y E-017 (más E-018 si la tienes).
2. Números de los PR y si alguno necesitó más de un push para ponerse en verde, y por qué.
3. Cuántas confirmaciones te pidió Claude en total y cuánto duró aproximadamente cada sesión. Son los primeros datos de coste e intervenciones humanas (F6).
4. Cualquier comportamiento inesperado: es tan valioso como lo que funciona.

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El hook no se ejecuta | La sesión no arrancó en la raíz, o falta `python3` | Sal y arranca `claude` en la raíz del repositorio desde WSL |
| `harness: command not found` dentro de la sesión | El `PATH` del terminal no incluye `~/.local/bin` | `export PATH="$HOME/.local/bin:$PATH"` y vuelve a arrancar `claude` |
| No pide confirmación al editar AGENTS.md | Ya existe un permiso guardado en `.claude/settings.local.json` o en la configuración de usuario | Revisa ese archivo; un `allow` personal **no** debería anular un `ask` (documentado). Anótalo como hallazgo |
| La skill no aparece | No se cargó `.claude/skills/` | Pregunta a Claude «¿qué skills tienes disponibles?» y envíame la respuesta |
