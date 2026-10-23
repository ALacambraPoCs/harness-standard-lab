---
documento: F3-INFORME
titulo: Informe de cierre de la Fase 3 — Componentes, catálogo y adaptador de Claude Code
estado: aprobado (D-040)
fecha: 2026-10-23
---

# Fase 3 · Informe de cierre

## 1. Entregado

| Incremento | Entregable | Aprobación |
|---|---|---|
| F3.1 | Modelo de componentes (6 tipos), esquema `catalog-entry`, ciclo de vida y ficha de 17 puntos; ADR-012 rev. 2 | D-034, D-035 |
| F3.2 | Adaptador de Claude Code, ficha `adapter.claude.settings` y `settings.json` deny-first | D-036 |
| F3.3 | Estándar 0.3.0: 16 requisitos (HS-CMP, HS-SEC-007…009, HS-CI-004), validador propio de skills y `harness catalog validate` | D-037 |
| F3.4 | Componentes semilla: hook `verificar-al-terminar`, subagente `verificador` y skill `cerrar-tarea` | D-038 |
| F3.5 | ADR-017: distribución por copia versionada (`harness components`, `components.lock`) y HS-CMP-009; estándar 0.4.0 | D-039 |
| F3.6 | Prueba en el laboratorio con Claude Code 2.1.308 (modelo Haiku 5.5, el predeterminado de la organización) | Este informe |

## 2. Evidencias de la F3.6 (`harness-example-greenfield`, 2026-10-23)

| ID | Evidencia | Resultado |
|---|---|---|
| E-014 | En modo *accept edits*, crear un archivo normal no pide confirmación; editar `AGENTS.md` **sí** la pide (diálogo solo Yes/No) | ✅ La regla `ask` de `settings.json` funciona y se distingue del comportamiento por defecto |
| E-015 | Con la prueba en rojo, el hook `Stop` bloqueó la parada 3 veces con el error exacto y después dejó parar; con `check` en verde, terminó sin mensaje | ✅ Hook y límite de reintentos según la ficha |
| E-016 | El subagente `verificador` se ejecutó en segundo plano (48 s) y obtuvo `check`, AC1, AC2 y `harness tasks validate` con código 0, sin editar nada | ✅ Con una salvedad (H-3) |
| E-017 | La skill `cerrar-tarea` se cargó desde `.claude/skills/` (valida ADR-012). PR #10: `done_pr` escrito después de crear el PR, validación local y commit de cierre en verde **al primer intento** | ✅ |
| E-018 | PR #9: adopción del estándar 0.4.0 con componentes instalados por `harness components add`; la conformidad (con HS-CMP-009, deriva) en verde | ✅ |
| E-019 | X-01: la issue #8 pasó a `in_progress`, se cerró por `Closes #8` y recibió `status:done` y un comentario con enlace a la ejecución, todo automáticamente | ✅ |

Estado final del ejemplo (`main` `6bbe505`): N1, estándar 0.4.0, 60 reglas sin errores ni avisos, 4 tareas en `done` y los 3 componentes al día.

**Coste en intervenciones humanas:** 26 confirmaciones en dos sesiones (3a 1, 3a-bis 1, 3b 1, implementación 1, verificador 5, cierre de T-0004 10, cierre de T-0003 7). La mayoría correspondieron a comandos seguros (`unittest`, `harness …`, `git status`). Es la primera línea base para la F6.

## 3. Hallazgos

| ID | Hallazgo | Gravedad |
|---|---|---|
| H-1 | El hook no distingue un rojo intencionado (TDD pedido por la persona) de trabajo sin terminar: gastó 3 turnos. Claude priorizó correctamente la instrucción humana | Media (coste) |
| H-2 | Las líneas de Progreso no siguen el formato de fecha y autor; nada lo comprueba | Baja |
| H-3 | El informe de formato fijo del verificador no llega literal: el agente principal lo resume | Media (evidencia) |
| H-4 | 26 confirmaciones, casi todas en comandos seguros: fatiga y presión hacia el modo automático | Alta (adopción) |
| H-5 | El verificador comprueba que las pruebas pasan, no que habrían fallado sin la implementación | Baja |
| H-6 | En la 3d, el agente pidió confirmación de su plan antes del push, aunque la regla `ask` ya la exige | Baja (coste) |
| H-7 | `gh pr edit` falló (aviso de Projects clásico) y Claude usó `gh api`, que puede escribir cualquier cosa en GitHub y no tiene una regla `ask` específica | **Alta (seguridad)** |
| H-8 | Con T-0003, Claude no siguió el orden de la skill: puso `status: done` antes de conocer el PR. La CI lo rechazó (`done_pr` requerido) y Claude lo corrigió en un segundo commit. El harness contuvo el error, pero la skill (L1) no basta para garantizar el orden | Media |
| H-9 | El diálogo de Claude Code empuja hacia el modo automático («Tip: auto mode…»); la configuración base desactiva el modo bypass pero no el automático | **Alta (seguridad)** |
| H-10 | `gh` 2.45 (el de Ubuntu) falló al iniciar sesión (`slow_down`); la skill depende de `gh` | Baja |

## 4. Propuestas (se deciden una a una)

| P | Hallazgo | Propuesta | Dónde |
|---|---|---|---|
| P-1 | H-9 | `permissions.disableAutoMode: "disable"` en la configuración base y como regla de HS-SEC-009, hasta que la F5 evalúe el clasificador. Verificado (2026-10-23): funciona desde cualquier archivo de configuración, también el del proyecto; en *managed* no se puede anular | F3.7 |
| P-2 | H-7 | `ask` para `Bash(gh api *)`; `deny` para `Bash(gh repo delete *)` y `Bash(gh secret *)`. Son reducción de riesgo, no frontera: la documentación avisa de que una regla Bash no detiene otras formas de invocar el programa (`sh -c …`) | F3.7 |
| P-3 | H-4 | `allow` en la base solo para comandos del contrato sin efectos: `harness check` (con `ask` para `--run-commands`, que ejecuta los comandos del manifiesto), `harness tasks index --check`, `harness pr check` y `harness components list`. Las formas de solo lectura de `git` ya no piden confirmación (lista interna de Claude Code). **No** se permite `harness tasks validate --run-acceptance`, porque ejecuta comandos arbitrarios de los archivos de tarea. Guía para que cada instancia añada sus `check` y `test`. Limitación verificada: un `allow` del proyecto solo aplica tras confiar en la carpeta y nunca en `-p` | F3.7 |
| P-4 | H-8 | `harness tasks close T-NNNN --pr N`: transición determinista (mover, `status`, `done_pr`, índice). La skill 0.2 lo usa y deja de describir el paso a mano | F3.7 |
| P-5 | H-1 | El hook 0.3 documenta `HARNESS_STOP_MAX=0` para suspenderlo en una sesión TDD y baja el límite por defecto a 2 | F3.7 |
| P-6 | H-3, H-6, H-10 | Verificador 0.2: devolver solo el bloque literal. Skill 0.2: pegar ese bloque en `harness:evidencia`, no pedir confirmación extra antes del push y aceptar el número del PR si no hay `gh` | F3.7 |
| P-7 | H-2, H-5 | Solo se registran; se reevalúan con datos del piloto (F6/F8) | — |

**Resultado:** P-1…P-6 aprobadas como D-041…D-046 e implementadas en F3.7 (estándar 0.5.0). H-2 queda resuelto en parte: `harness tasks close` escribe la línea de progreso con fecha y autor.

## 5. Criterios de aceptación de la fase (`PLAN.md`)

| # | Criterio | Estado |
|---|---|---|
| 1 | Contrato por tipo y `catalog-entry` con fixtures | ✅ |
| 2 | 3 semillas con ficha, entrada, pruebas y retirada | ✅ |
| 3 | Plantilla N1 con `settings.json` conforme | ✅ |
| 4 | Sin deriva tras la sincronización | ✅ (HS-CMP-009 en la CI del ejemplo; `components list` al día) |
| 5 | Evidencia en el laboratorio de los 3 componentes y de la regla `ask` | ✅ E-014…E-017 |

## 6. Hechos verificados al cerrar (2026-10-23, S-CC-SET)

- `permissions.disableAutoMode: "disable"` y `disableBypassPermissionsMode` «en cualquier archivo de configuración»; más útiles en *managed*, donde no se pueden anular (*permissions*, «Permission modes»).
- En modo automático un clasificador (por defecto Sonnet 5) revisa las acciones en lugar de la persona; las reglas `ask` siguen forzando el diálogo (*permission-modes*).
- Claude Code tiene una lista interna, no configurable, de comandos de solo lectura que nunca piden confirmación (`ls`, `cat`, `grep`, formas de solo lectura de `git`…) (*permissions*, «Read-only commands»).
- Las reglas Bash separan comandos compuestos (`&&`, `;`, `|`…): un `allow` debe coincidir con cada parte; `deny` y `ask` aplican si coincide cualquiera (*permissions*, «Compound commands»).

## 7. Limitaciones

- Una sola persona y un solo modelo (Haiku 5.5): el comportamiento de los componentes puede variar con otros modelos (H-8 podría ser menos frecuente con uno mayor; sin evidencia).
- R-10 sigue abierto: no se han probado criterios `manual` ni la revisión de code owner.
- No se midió el coste en tokens de las sesiones (la telemetría se aborda en F6, Q-06).
