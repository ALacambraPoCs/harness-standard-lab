---
documento: F4-01
titulo: F4.1 · Verificación de fuentes — worktrees, Claude Code en paralelo, merge queue y merge drivers
estado: aprobado (decisión 1: D-082)
fecha: 2026-11-13
---

# F4.1 · Verificación de fuentes

Leídas el 2026-11-11.

| ID | Fuente | Hecho verificado (cita o paráfrasis fiel) | Consecuencia para el diseño |
|---|---|---|---|
| W1 | git-scm.com/docs/git-worktree, `add` | `add` se niega a crear un worktree si la rama «is already checked out by another worktree» (salvo `--force`) | Exclusión mutua **local** por rama, gratis. No funciona entre máquinas: el *lease* sigue haciendo falta (ADR-011) |
| W2 | Ídem, REFS y CONFIGURATION FILE | Los worktrees comparten todo salvo los archivos propios como `HEAD` e `index`. Las refs `refs/` se comparten. `config` se comparte salvo con `extensions.worktreeConfig` | Un `git config` en un worktree afecta a todos. Ramas y tags se ven al momento entre worktrees |
| W3 | Ídem, `remove`, `prune`, `lock` | `remove` solo borra worktrees limpios (sin cambios ni archivos sin seguimiento), salvo `--force`. `prune` limpia los que desaparecieron. `lock` evita la limpieza | Base del procedimiento de **recuperación** de un worktree abandonado (criterio 5) |
| W4 | code.claude.com/docs/en/worktrees, «Start Claude in a worktree» | `claude --worktree <nombre>` crea `.claude/worktrees/<nombre>/` en la rama `worktree-<nombre>`, desde la rama por defecto del remoto (`worktree.baseRef: "fresh"`). Se recomienda ignorar `.claude/worktrees/` | La plantilla añade `.claude/worktrees/` a `.gitignore`. El nombre de rama `worktree-*` debe convivir con las ramas de tarea (`t-NNNN-…`) |
| W5 | Ídem, «Clean up worktrees» | Al salir: si el worktree está limpio y la sesión no tiene nombre, se borran el worktree y su rama; si tiene trabajo, pregunta. Con `-p` no limpia | La skill o el protocolo nombran la sesión o hacen commit y push antes de salir |
| W6 | Ídem, «How Claude Code enforces isolation» | Dentro de un worktree, Claude Code **bloquea**: ediciones en el checkout principal; comandos con el directorio en él; redirecciones de git hacia él (`git -C`, `GIT_DIR`…); comandos cuya forma no puede verificar. «None of them tracks which files a shell command writes» | El aislamiento es real para las herramientas y para git, no para cualquier escritura por shell: el sandbox sigue siendo necesario |
| W7 | Ídem, «Isolate subagents with worktrees» | `isolation: worktree` da a cada subagente un worktree temporal, que se borra si no hay cambios | Opción para la simulación de 3 tareas (F4.6): subagentes aislados frente a 3 sesiones |
| W8 | Ídem, «What worktrees share» | **«Yes, and don't ask again»** en un worktree se guarda en el `settings.local.json` del checkout principal y se aplica a **todos** los worktrees | Refuerza la regla de no usar «don't ask again» (R-15): una aprobación se propaga |
| W9 | Ídem, nota de hooks | Tras `EnterWorktree`, `${CLAUDE_PROJECT_DIR}` **sigue apuntando al checkout principal**; el `cwd` de la entrada del hook sí sigue al worktree. En sesiones con worktree del escritorio, los hooks se ejecutan en la raíz principal | **H-38:** el hook `verificar-al-terminar` usa primero `CLAUDE_PROJECT_DIR`, así que en esos casos verificaría el checkout principal, no el worktree. Debe usar el `cwd` del evento |
| W10 | code.claude.com/docs/en/large-codebases | `CLAUDE.md` por directorio, cargado bajo demanda; reglas por ruta (`.claude/rules/` con `paths:`); `claudeMdExcludes`; `worktree.sparsePaths` | Encaja con los `AGENTS.md` de segmento (HS-INS-011). `sparsePaths` por segmento es un derivado posible del mapa |
| W11 | docs.github.com, «Managing a merge queue» | Disponible en «any public repository owned by an organization» y en privados con Enterprise Cloud. Con Actions, `merge_group` es **obligatorio** | El laboratorio (público, organización, Free) **puede** usar merge queue. HS-CI-008 ya exige `merge_group` |
| W12 | git-scm.com/docs/gitattributes, merge drivers | `union` toma las líneas de las dos versiones en orden imprevisible («Do not use this if you do not understand the implications»). Un driver propio se **define en `.git/config` o `~/.gitconfig`**, no en el repositorio | Un *merge driver* no viaja con el repositorio: cada clon (y la CI) lo configuraría. **No verificado** si GitHub lo respeta al fusionar un PR. **Conclusión:** no basar la solución de `INDEX.md` en un merge driver (decisión 3) |

**No verificado:**
- *agent teams* y *cross-session messaging*: existen según la documentación, pero no se han leído. Se leerán solo si la F4.6 los usa;
- el valor por defecto de `gc.worktreePruneExpire`;
- cómo trata GitHub `.gitattributes merge=` al fusionar un PR.

## Hallazgo nuevo

- **H-38 (medio):** ver W9. Con `EnterWorktree` y en las sesiones con worktree del escritorio, el hook `verificar-al-terminar` ejecutaría `check` en el checkout principal y daría por buena una tarea sin verificarla en su worktree. Corrección: usar el `cwd` del evento. Va en la F4.4.

## Caso brownfield (decisión 1, D-082)

**Criterio del usuario:** que el ejemplo se parezca en forma a los repositorios de desarrollo de Nirvana (`nirvana_dxc`: backend FastAPI asíncrono, frontend React y TypeScript, workers, migraciones) **sin modificar ningún repositorio de terceros**.

| Candidato | Licencia | Forma | Motivo |
|---|---|---|---|
| **`keephq/keep`** (elegido) | MIT, salvo `ee/` | Monorepo Python (`keep/`) y Next.js (`keep-ui/`), workers ARQ, Alembic, Compose | El más parecido. Además, `keep-nirvana` es un fork de Keep, así que lo aprendido se transfiere al piloto |
| `fastapi/full-stack-fastapi-template` | MIT | FastAPI, SQLModel, React, Vite | Reserva: es una plantilla limpia, sin deuda real |
| `polarsource/polar` | Apache-2.0 | FastAPI, SQLAlchemy, Dramatiq, Next.js | Descartado: unos 18.800 commits, demasiado grande para el laboratorio |

**E-044 · Verificación en la copia local** (usuario, 2026-11-12):

| Aspecto | Resultado |
|---|---|
| Origen | `main` en `127a78d`, del 2026-11-10; 2.987 commits; unos 86 MB |
| Stack del backend | FastAPI ^0.115.6, SQLModel ^0.0.22, SQLAlchemy ^2.0.14, Alembic ^1.13.2 (`keep/alembic.ini`), ARQ 0.26.3 (`keep/api/arq_worker.py`); **pydantic ^1.10**, deuda real |
| Stack del frontend | Next.js 15.5.9, React 19.0.1, TypeScript ^5.7 |
| Despliegue | Sin Helm charts en el repositorio; 16 workflows propios |
| `ee/LICENSE` | **No es MIT:** «it is forbidden to copy, merge, publish, distribute, sublicense, and/or sell the Software». No hay más licencias propias en el repositorio |
| Dependencias de `ee/` | Solo `tests/test_auth_new.py` lo importa de forma estática. `keep/identitymanager/identitymanagerfactory.py:119` lo carga por nombre en tiempo de ejecución |

**Copia** `ALacambraPoCs/harness-example-brownfield`:
- **Historia sin `ee/`:** reescrita con `git filter-repo --path ee --invert-paths`. Quedan 2.975 commits; `git log --all -- ee` da 0.
- **Commit de procedencia:** añade `PROCEDENCIA.md` y retira `tests/test_auth_new.py`.
- **Salvaguarda local:** `url."no-push-a-terceros://".pushInsteadOf https://github.com/keephq/`.
- **Actions desactivado antes del primer push:** `enabled: false`.
- **Repo independiente:** `isFork: false`, público.
- **Punto de partida:** tag `base-f4`.
