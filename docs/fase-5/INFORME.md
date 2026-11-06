---
documento: F5-INFORME
titulo: Informe de cierre de la Fase 5 — Verificación, CI/CD, seguridad, despliegue y auditoría
estado: propuesta (pendiente de aprobación)
fecha: 2026-11-06
depende_de: [D-053…D-078]
---

# Fase 5 · Informe de cierre

**Resultado:** la autoridad del harness reside ahora en la plataforma, y está comprobada. Un PR solo se fusiona si superan los checks requeridos, con origen GitHub Actions. Si su riesgo es alto, además hace falta una aprobación humana registrada; la puerta falla cerrada y no admite bypass de administradores. Solo se despliega lo fusionado, se verifica lo que se sirve, el rollback está ensayado y cada cambio se puede auditar. Las instrucciones al agente quedan como reducción de riesgo, no como frontera (ADR-009).

**Versiones:**
- estándar **0.10.0**, 77 requisitos;
- CLI `cli-v0.10.0-rc.1`;
- 312 autotests;
- ejemplo greenfield en N1 con T-0001…T-0011 en `done`.

## 1. Entregado

| Incremento | Entregable | Aprobación |
|---|---|---|
| F5.1 | Verificación de fuentes (G1–G12, C1–C13) y **modelo de amenazas** (A1–A7, T1–T6, V1–V14) | D-057 |
| F5.2 | **Riesgo calculado** (`harness pr risk`, HS-CI-005), matriz de escalado y **ADR-010 rev. 2** (puerta `aprobacion-riesgo-alto`) | D-058…D-061 |
| F5.3 | **`harness platform check`** (HS-CI-006) y seguridad de workflows (HS-CI-007/008) | D-062…D-064 |
| F5.4 | **Revisor informativo** con agente en jaula de solo lectura y simulador hostil A1–A7 | D-065, D-066 |
| F5.5 | **Sandbox** (HS-SEC-013), configuración gestionada, token del agente de mínimo privilegio, modo automático desactivado | D-067…D-071 |
| F5.6 | **Despliegue en Pages** con verificación y rollback, **`harness audit`**, runbook (HS-CI-009) | D-072…D-074 |
| F5.7 | Prueba de extremo a extremo en el laboratorio y ensayo de rollback | D-075…D-077 |
| Cierre | C-1…C-7 (estándar 0.10.0) y medición C-8 | D-078 |

## 2. Criterios de aceptación de la fase

| # | Criterio (PLAN.md) | Estado | Evidencia |
|---|---|---|---|
| 1 | Prueba adversarial de ADR-009 superada | ✅ | E-029, E-030, E-040 |
| 2 | Ningún job con credenciales del modelo tiene escritura | ✅ | `ci.model-readonly`; E-029 |
| 3 | `harness platform check` informa del estado real | ✅ | E-026, E-039 (origen de checks y bypass, 0.10.0) |
| 4 | Cada clase de riesgo con checks, revisores, escalado y escenario de laboratorio | ✅ | `bajo`: PR #18 y #19 · `medio`: PR #27 (E-041) · `alto`: PR #16, #17, #22, #24, #25 y #28 |
| 5 | Despliegue y rollback con environment protegido | ✅ | E-028, E-031 (ensayo y corrección H-30), E-032 |
| 6 | Modelo de amenazas con control y capa por vector | ✅ | `02-modelo-amenazas.md` §6 |

## 3. Evidencias del cierre (E-038…E-043)

| ID | Evidencia | Resultado |
|---|---|---|
| E-038 | Adopción de 0.10.0 (PR #25 del ejemplo) | Puerta aprobada y despliegue verificado (`f1b0d9f`). Los pasos corren con `bash --noprofile --norc -e -o pipefail` (C-6) |
| E-039 | **C-1 contra GitHub real** | `platform check` 0/0. `can_admins_bypass: false` en los dos environments: la API lo devuelve aunque la referencia no lo documente. `integration_id: 15368` en los tres checks: **el valor de las plantillas queda verificado** |
| E-040 | **C-5:** PR adversarial #26 | Con `pr check` en rojo, la puerta **espera** (en la F5.7 se saltaba) |
| E-041 | **Escenario `medio`** y **C-4** (PR #27, T-0011) | Riesgo `medio` («prueba renombrada»), puerta saltada, `ready → done` en un PR aceptado por la CI. El cuerpo copia la señal de `harness pr risk` (skill 0.3.1) |
| E-042 | **Medición C-8** | Ver §4 |
| E-043 | **C-7** | `harness audit`: «firmado; no verificable aquí…». Hook 0.3.2 probado con pruebas unitarias |

## 4. Confirmaciones por cierre de tarea (D-070, F3.8)

| Sesión | Sandbox | Diálogos | Deliberados (`git push`, `--run-acceptance`) | Evitables | Fuente |
|---|---|---|---|---|---|
| B (F5.7, cierre de T-0007) | No (H-26) | 9 | 3 | 6 | Anotada |
| D (cierre, T-0011) | Sí | 5 | 3 | 2: edición de estado (H-33) y red por push encadenado (H-34) | Reconstruida de la transcripción |
| **E (cierre, T-0010)** | Sí | **4** | 3 | 1: edición de texto por iniciativa del agente | **Anotada** |

**Conclusión:** con sandbox, permisos de 0.10.0 y push suelto, un cierre pide 3 confirmaciones deliberadas y como mucho 1 más. **Se cumple el objetivo de ≤ 4.** Según D-070, el modo automático **sigue desactivado**: no hay más de 3 confirmaciones por tarea fuera de las `ask` deliberadas.

**Salvedades:**
- modelo Haiku 5.5;
- una persona;
- configuración gestionada de DXC sin inspeccionar;
- tres sesiones medidas, que no son una muestra estadística.

La medición sistemática pasa a la F6.

## 5. Hallazgos de la fase

Corregidos durante la fase: H-17, H-18, H-19, H-20 (tag), H-22, **H-23 a H-32** (C-1…C-7) y **H-30 (crítico: el rollback no se ejecutaba)**.

**Nuevos en el cierre, sin corregir:**

| ID | Hallazgo | Gravedad | Propuesta |
|---|---|---|---|
| H-33 | La skill `cerrar-tarea` sigue diciendo que solo se cierra desde `in_progress`/`in_review`: no se actualizó con C-4 y el agente editó el estado a mano | Baja | Skill 0.3.2: `ready` también |
| H-34 | El agente encadenó `; git push` pese a la instrucción de la skill; con la instrucción repetida en el prompt, no lo hizo. **Las instrucciones no bastan** (R-17) | Media | Hook `PreToolUse` que rechace un `git push` compuesto y diga la forma correcta (L3) |
| H-35 | La skill escribe el cuerpo del PR **antes** de cerrar la tarea; con la rama vacía, `harness pr risk` da `bajo` y la CI falla con `pr.risk-min` (PR #28). La CI lo detectó | Media | `harness pr risk` incluye el `risk:` de las tareas que el PR referencia, o la skill declara al menos ese valor |
| H-36 | Al editar el cuerpo del PR se lanza un run nuevo, pero el anterior queda **esperando** en el environment de la puerta | Baja | `concurrency` con `cancel-in-progress` por PR en el workflow de tareas |

**Riesgos residuales aceptados:**
- **R-10:** un único mantenedor; CODEOWNERS y las aprobaciones sin independencia hasta F8.
- **D-055:** revisor probado con simulador; el modelo real, en el piloto.
- **V12:** tags `cli-v*` mutables si no se aplica su ruleset.
- **Q-08:** requisitos regulatorios sin respuesta.

## 6. Decisiones que se piden

**1. Cerrar la Fase 5.**
- **Recomendación:** aprobar el cierre con H-33…H-36 como pendientes.
- **Justificación:** los seis criterios se cumplen con evidencia, y los cuatro hallazgos son de usabilidad o higiene. Ninguno abre una vía de fusión o despliegue no autorizado: la CI detectó H-35 y bloqueó.
- **Alternativa:** corregirlos antes de cerrar. Mi recomendación es hacerlo en un parche 0.10.1 al empezar la siguiente fase, porque no cambian la arquitectura.

**2. Siguiente fase.** La tabla está en `ESTADO.md`.

| Opción | A favor | En contra |
|---|---|---|
| **F4 · Segmentación y concurrencia** (recomendada) | Es el mayor hueco de diseño que queda: objetivos 4 y 6 del encargo, ADR-011 y ADR-014. F7 depende de ella. Se puede usar como «brownfield» un repositorio público mediano mientras se designan los del piloto (Q-09) | Necesita elegir ese repositorio y la simulación de concurrencia lleva trabajo |
| F6 · Contexto, coste y evaluación | Las métricas sirven de línea base para el piloto. La medición de confirmaciones ya está iniciada | Depende de la telemetría (Q-06), por verificar |

**3. Pedir ya lo externo de la ruta crítica:**
- repositorios del piloto (Q-09);
- segunda persona mantenedora (R-10);
- grupo de gobierno (Q-01);
- credencial de modelo corporativa (D-055).
