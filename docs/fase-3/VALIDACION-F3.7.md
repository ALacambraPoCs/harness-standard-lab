---
documento: F3-VALIDACION-F3.7
titulo: Validación de la F3.7 en el laboratorio
estado: aceptada (D-047)
fecha: 2026-10-24
guia: GUIA-F3.7-VALIDACION.md
---

# Validación de la F3.7 en el laboratorio

`harness-example-greenfield` con estándar 0.5.0, Claude Code 2.1.308 y el modelo Haiku 5.5 (el predeterminado de la organización). Tres sesiones en modo manual. Estado final: `main` `847f154`, N1, 63 reglas sin errores ni avisos, T-0001…T-0006 en `done`.

## 1. Evidencias

| ID | Evidencia | Resultado |
|---|---|---|
| E-020 | Con Shift+Tab los modos son *manual → accept edits → plan*; **no aparece `auto`** | ✅ `disableAutoMode` funciona desde el `settings.json` del proyecto (D-041) |
| E-021 | Con `HARNESS_STOP_MAX=0 claude` y la prueba en rojo a propósito, Claude terminó en un turno sin bloqueo (en la F3.6, 3 turnos). El aviso «suspendido» no se ve en la sesión (H-11) | ✅ D-045, con salvedad |
| E-022 | `gh api …` → diálogo «Permission rule Bash(gh api *) requires confirmation» (solo Yes/No). `gh auth status` → **denegado sin diálogo**. `gh auth token` → Claude se negó antes de intentarlo (L1) | ✅ D-042. Primera evidencia práctica de una regla `deny` de Bash |
| E-023 | PR #14 y #15: la skill abrió el PR, después ejecutó `harness tasks close T-NNNN --pr N` **sin editar a mano** el archivo de la tarea y no pidió confirmación propia antes del push. El cuerpo de los dos PR lleva el **bloque literal del verificador**. Pero `gh pr edit` falló en ambos y el cuerpo lo subió la persona con `gh api` (H-13) | ✅ D-044 y D-046 (H-3, H-6 y H-8 resueltos), con salvedad |
| E-024 | Confirmaciones por paso (§2) | ⚠️ Bajan poco: las reglas `allow` funcionan, pero la forma en que el agente compone los comandos las anula (H-12) |

X-01: la issue #12 recorrió `in_progress` → cerrada por `Closes #12` → `status:done` con comentario, sin intervención.

## 2. Confirmaciones

| Paso | Ediciones | Comandos | Comparable en la F3.6 |
|---|---|---|---|
| A · solo la prueba (TDD) | 2 | 1 | 3b: 1 (en *accept edits*) |
| B · implementación | 2 | 1 | 1 |
| B · `gh api` (prueba de la regla) | — | 1 | — |
| B · verificador | — | 4 | 5 |
| B · cierre de T-0006 | — | 7 | cierre de T-0004: 10 |
| C · cierre de T-0005 (verificador incluido) | — | 11 (3 del verificador) | cierre de T-0003: 7 (sin verificador) |
| **Total** | **4** | **25** | 26 (sin separar) |

Las ediciones dependen del modo elegido (manual), no de la configuración. De los 25 comandos:

| Causa | Nº | Evitable con |
|---|---|---|
| `check`/`test` de la instancia (D-043: fuera de `allow` por diseño) | 8 | Sandbox (F5) o decisión de la instancia |
| Reglas `ask` (push, `--run-acceptance`, `gh api`) | 7 | No: son el control |
| `git commit`, `gh pr create/ready/view` (sin regla) | 6 | Decisión sobre `allow` (P-12) |
| Envoltorios del agente (`; echo $?`, `command -v`, *heredoc*) sobre comandos permitidos | 4 | Instrucciones de forma (P-8) |
| Reintento por error mal atribuido | 1 | P-8 y P-9 |
| **Evitables sin tocar la seguridad** | **5** de 25 | |

## 3. Hallazgos

| ID | Hallazgo | Gravedad |
|---|---|---|
| H-11 | Con el hook suspendido no queda rastro visible en la sesión: la salida de error de un `Stop` que termina con código 0 no se muestra (inferencia, no verificado en la documentación). La ficha 0.3.0 dice lo contrario | Baja |
| H-12 | El agente envuelve los comandos (`…; echo "X=$?"`, `command -v harness && …`, `date; …`). En un compuesto, `allow` debe coincidir con cada parte, y `echo $?` no es de solo lectura: `harness tasks close` y `harness check` acabaron pidiendo confirmación | Media (coste) |
| H-13 | `gh pr edit` falla en este repositorio (aviso de Projects clásico, como en la F3.6) y el agente no lo detectó: con `… \| tail -2 && gh pr ready` la tubería devuelve el código de `tail`. El PR quedó listo para revisión con el cuerpo provisional | **Alta** (el flujo no se completa solo) |
| H-14 | Una tarea que solo hay que cerrar (sin cambios en la rama) no permite abrir el PR. Claude se detuvo y lo explicó; con un commit vacío funcionó | Baja |
| H-15 | En `gh pr edit … && harness pr check …; echo "exit=$?"` el código 1 era de `gh pr edit`, pero Claude lo atribuyó a `pr check` y lo repitió | Media (diagnóstico erróneo) |
| H-16 | En el #15 el cuerpo omite las etiquetas de la plantilla («Tarea:», «Riesgo:»…); deja solo las anclas y el valor. `pr check` lo acepta | Baja (legibilidad) |

Confirmado de la F3.6: H-2 (la línea de progreso del agente no tiene autor; la de `tasks close`, sí).

## 4. Conclusión

Los controles nuevos (`disableAutoMode`, reglas de `gh`, `ask` de las opciones que ejecutan, `tasks close`) **funcionan como se diseñaron**. Lo que falla está en dos sitios:
1. **La forma de los comandos del agente** (H-12, H-13, H-15), que anula los `allow` y oculta errores.
2. **`gh pr edit`**, que no funciona en este repositorio y del que la skill depende para el cuerpo del PR.

Las dos cosas se corrigen en la skill y en el verificador, sin tocar la seguridad. Propuestas P-8…P-12 en el REGISTRO.

**Resultado:** P-8…P-12 aprobadas como D-048…D-052 e implementadas en F3.8.
