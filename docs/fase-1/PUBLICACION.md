---
documento: F1-PUBLICACION
titulo: Runbook de publicación en GitHub y prueba de extremo a extremo
estado: listo para ejecutar
fecha: 2026-10-20
cierra: R-09 (CI y workflow reutilizable sin ejecutar en GitHub)
---

# Publicación en `ALacambraPoCs` y prueba de extremo a extremo

| Repositorio | Contenido | Origen |
|---|---|---|
| `ALacambraPoCs/harness-standard-lab` | Repositorio central: estándar (A) y plantilla/CLI (B) | `harness-standard.bundle` |
| `ALacambraPoCs/harness-example-greenfield` | Instancia N0 de ejemplo (C) que llama al workflow reutilizable | `harness-example-greenfield.bundle` |

Desde esta sesión no se puede hacer push: no tiene credenciales de GitHub y no conviene pegar tokens en el chat. Los pasos 2 y 3 se ejecutan en tu equipo con tu sesión de git.

## 1. Visibilidad (decisión)

| Opción | Rulesets y checks requeridos | Code owners obligatorios | Coste | Nota |
|---|---|---|---|---|
| **Público en una org Free** (recomendado para el laboratorio) | Sí | Sí | 0 | El contenido es genérico y no incluye datos de DXC. Tu email aparece en los commits. |
| Privado con plan Team | Sí | Sí | De pago | Permite reproducir la configuración corporativa. |
| Privado en Free | **No** | **No** | 0 | No se pueden probar los controles L5; R-09 quedaría parcialmente abierto. |

Fuente: [Managing rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets): "Rulesets are available in public repositories with GitHub Free and GitHub Free for organizations, and in public and private repositories with GitHub Pro, GitHub Team, and GitHub Enterprise Cloud". [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans): las ramas protegidas y los code owners en repositorios privados forman parte de Team.

**Si `harness-standard-lab` es privado**, hay que hacer dos cosas más:

- En *Settings → Actions → General → Access*, elegir "Accessible from repositories in the ALacambraPoCs organization". Sin esto, la instancia no puede llamar al workflow reutilizable.
- Crear un token fine-grained de solo lectura (Contents: Read) sobre `harness-standard-lab` y guardarlo en la instancia como secreto `HARNESS_STANDARD_TOKEN`. Después, añadir `secrets: { standard-token: ${{ secrets.HARNESS_STANDARD_TOKEN }} }` en el `uses:` de la instancia.

## 2. Subir el repositorio central (PowerShell)

`harness-standard-lab` debe existir **vacío**, sin README ni licencia.

```powershell
cd $HOME\Desktop\Harness-engineering
git clone harness-standard.bundle harness-standard-lab
cd harness-standard-lab
git remote set-url origin https://github.com/ALacambraPoCs/harness-standard-lab.git
git push -u origin main
git push origin --tags        # cli-v0.1.0 y standard-v0.1.0 (los usa el workflow reutilizable)
```

Comprobación: en *Actions* aparece el workflow `ci` en verde en sus tres versiones de Python. Si falla, envíame el log del job.

## 3. Crear y subir la instancia de ejemplo

Crea `ALacambraPoCs/harness-example-greenfield` vacío y con la **misma visibilidad** que el central. Después:

```powershell
cd $HOME\Desktop\Harness-engineering
git clone harness-example-greenfield.bundle harness-example-greenfield
cd harness-example-greenfield
git remote set-url origin https://github.com/ALacambraPoCs/harness-example-greenfield.git
git push -u origin main
```

## 4. Configuración de la plataforma (controles L5)

Ruta en GitHub: *Settings → Rules → Rulesets → New branch ruleset*, con objetivo `main` y estado **Active**.

| Regla | `harness-standard-lab` | `harness-example-greenfield` | Requisito |
|---|---|---|---|
| Restrict deletions / Block force pushes | ✅ | ✅ | ADR-013 |
| Require a pull request before merging | ✅ | ✅ | ADR-009 |
| Required approvals | **0 en el laboratorio** (ver §6) | **0 en el laboratorio** | ADR-013 |
| Require review from Code Owners | Solo cuando haya un segundo mantenedor | Ídem | HS-SEC-002 |
| Require status checks to pass | `test (3.11)`, `test (3.12)`, `test (3.13)` | `conformance / harness check` | HS-GOV-004 |
| Require branches to be up to date | ✅ | ✅ | — |

Además, en *Settings → Code security*, activar **Secret scanning** y **Push protection** en ambos repositorios (HS-SEC-004).

El nombre del check aparece en el selector **después de la primera ejecución**. Si no lo ves, abre antes el PR de la prueba del §5.

## 5. Prueba de extremo a extremo

Con esta prueba se cierran R-09 y la verificación manual de HS-GOV-004.

1. En `harness-example-greenfield`, crea una rama y edita `AGENTS.md`: sustituye `python3 -m unittest discover -s tests` por `pytest`. Abre un PR.
   - **Esperado:** `conformance / harness check` falla con `core.instructions.commands-match` (HS-INS-002) y el merge queda bloqueado. El resumen del job muestra el informe con QUÉ, POR QUÉ y CÓMO, y el artefacto `harness-report` contiene el JSON.
2. Deshaz el cambio en la misma rama.
   - **Esperado:** el check pasa y el merge queda permitido.
3. Opcional: en otro PR, borra `/.mcp.json` de `.github/CODEOWNERS`.
   - **Esperado:** falla `core.codeowners.sensitive-paths`.

Envíame el resultado de cada paso (captura del check o enlace al run) y lo registro como evidencia en `REGISTRO.md`.

## 6. Desviaciones del laboratorio

| Desviación | Motivo | Riesgo | Cuándo se corrige |
|---|---|---|---|
| Ninguna aprobación humana obligatoria y no se exige revisión de code owner | Hay un solo mantenedor y GitHub no permite aprobar un PR propio | Los controles L5 de revisión no se ejercitan, solo los checks requeridos | Cuando se incorpore un segundo mantenedor (Q-01) o en el piloto (F8) |
| CODEOWNERS con usuario personal (`@AlbertoLacambra`) en lugar de equipos | La organización no tiene equipos | Ninguno en el laboratorio | Al crear los equipos `harness-owners`, `platform` y `security` |
| Acciones referenciadas por tag (`@v4`, `@v5`) y no por SHA | Simplicidad en v0.1 | Que una acción comprometida cambie el tag | Fase 5 (requisito de fijar acciones por SHA) |
