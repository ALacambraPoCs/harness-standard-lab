# Token de GitHub de mínimo privilegio para el agente (F5.5-C, D-069)

El agente **no** usa la sesión de `gh` ni las credenciales de git de la persona (que suelen ser de administración). Usa un token fine-grained con lo justo para el flujo del estándar. Las reglas `deny`/`ask` de `gh` reducen riesgo; **este token es la frontera** (V11, R-16).

## Permisos

Repository access: **Only select repositories** (los del trabajo). Expiration: **≤ 90 días**.

| Permiso | Valor | Para qué |
|---|---|---|
| Contents | Read and write | Push de ramas (a la rama por defecto lo impide el ruleset) |
| Pull requests | Read and write | `gh pr create`, `gh pr ready`, comentarios |
| Issues | Read-only | Leer la issue de la tarea (X-01 la escribe la CI) |
| Metadata | Read-only | Obligatorio |
| **Todo lo demás** (Administration, Actions, Deployments, Environments, Secrets, Variables, **Workflows**…) | **No access** | No puede aprobar la puerta de riesgo alto, tocar rulesets, leer secretos ni subir cambios en `.github/workflows/` |

Sin *Workflows*, un push que modifique `.github/workflows/` se rechaza: esos cambios (riesgo `alto`) los sube una persona.

## Uso en WSL / Linux / macOS

```bash
# 1. Guardar el token fuera del repositorio, legible solo por ti (el sandbox deniega leer ~/.config/harness)
mkdir -p ~/.config/harness && chmod 700 ~/.config/harness
printf '%s' 'github_pat_…' > ~/.config/harness/agent-token && chmod 600 ~/.config/harness/agent-token

# 2. Arrancar la sesión del agente con ese token
GH_TOKEN="$(cat ~/.config/harness/agent-token)" claude
```

Para `git push` dentro de la sesión, que git use el mismo token mediante `gh` como credential helper (una vez por repositorio):

```bash
git config --local credential.https://github.com.helper ''
git config --local --add credential.https://github.com.helper '!gh auth git-credential'
```

## Lo que se comprueba en el laboratorio (F5.7) antes de normarlo

| Comprobación | Esperado | Estado |
|---|---|---|
| `GH_TOKEN=… gh auth status` muestra el token y no la sesión guardada | `GH_TOKEN` tiene precedencia | **No verificado** |
| `gh pr create` con el token | Funciona | Por probar |
| Aprobar la puerta (`gh api …/pending_deployments`) | HTTP 403 | Por probar (el permiso exacto, *Actions* o *Deployments*, no está documentado en la referencia consultada; el token no tiene ninguno) |
| Push de un cambio en `.github/workflows/` | Rechazado | Por probar |
| `gh api repos/{o}/{r}/actions/secrets` | HTTP 403 | Por probar |
| `git push` usa el token (credential helper) | Push de ramas funciona; a `main`, rechazado por el ruleset | Por probar |

## Rotación

Al caducar, crear uno nuevo con los mismos permisos y sustituir el archivo. Si se sospecha una filtración, revocarlo en *Settings → Developer settings → Fine-grained tokens*.

**Alternativa para equipos (N2+):** una GitHub App propia con estos permisos da identidad de bot y tokens de una hora. Se valorará con el piloto.
