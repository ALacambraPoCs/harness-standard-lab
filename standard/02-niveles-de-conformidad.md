---
documento: HS-02
titulo: Niveles de conformidad y waivers
version_estandar: 0.1.0
estado: borrador
fecha: 2026-10-19
adr: [ADR-004, ADR-007]
caracter: normativo
---

# 02 · Niveles de conformidad y waivers

## 1. Niveles

Los niveles son **acumulativos**: cumplir un nivel exige cumplir todos los inferiores. Cada requisito declara en `conformidad` los niveles en los que aplica.

| Nivel | Nombre | Garantía | Uso de agentes que habilita (máximo) | Estado en v0.1 |
|---|---|---|---|---|
| **N0** | Legible por agentes | Una persona o un agente sin contexto previo entiende el repositorio, lo prepara y lo verifica sin preguntar a nadie. La configuración de agentes está protegida. | Asistencia interactiva, con la persona responsable supervisando cada paso | **Requisitos definidos** (§3) |
| **N1** | Trabajo verificado | "Hecho" significa verificado por la CI con evidencia, no declarado por el agente. | Un agente por tarea; revisión humana del PR | Fase 2 |
| **N2** | Concurrente | Varias personas y agentes trabajan en paralelo sin interferir. | Varios agentes en paralelo en segmentos distintos | Fase 4 |
| **N3** | Autonomía supervisada | La supervisión humana se aplica según el riesgo y las excepciones. | Loops y automatizaciones; merge sin intervención humana solo en clases de riesgo bajo | Fases 5–6 |

## 2. Reglas de los niveles

1. Toda instancia DEBE declarar su nivel en `standard.level` del manifiesto (HS-GOV-001).
2. Un repositorio que adopta el estándar por primera vez DEBERÍA declarar N0 y subir de nivel progresivamente. Es aceptable entrar directamente en N1 o superior en un greenfield creado con la plantilla.
3. Una instancia NO DEBE usar agentes en paralelo sobre el mismo repositorio (uso propio de N2) sin cumplir N1. Esta regla es organizativa hasta que la Fase 4 defina los controles técnicos.
4. El uso de agentes que habilita cada nivel es un **máximo**. Lo que pueda imponerse técnicamente se impondrá en las Fases 4 y 5. El resto se audita.
5. **Nivel efectivo.** La CLI calcula el nivel más alto en el que se cumplen todos los requisitos DEBE y NO DEBE aplicables, contando los waivers vigentes como cumplidos, y lo compara con el declarado.
6. **Degradación.** Si el check de conformidad falla de forma sostenida en la rama principal, el nivel efectivo baja y se notifica al propietario de la instancia. El umbral y el mecanismo se definen en la Fase 9.

## 3. Requisitos del nivel N0 (v0.1.0)

La fuente de verdad es `requirements.yaml`. Esta tabla es una vista resumida.

| ID | Nivel | Requisito (resumen) | Verificación | Exentable |
|---|---|---|---|---|
| HS-GOV-001 | DEBE | Existe `.harness/manifest.yaml` válido contra su esquema | automática | no |
| HS-GOV-002 | DEBE | El manifiesto declara una versión del estándar soportada por la CLI | automática | no |
| HS-GOV-003 | DEBE | Los waivers son válidos, están vigentes y solo afectan a requisitos exentables | automática | no |
| HS-GOV-004 | DEBE | La CI ejecuta el check de conformidad en cada PR, como check requerido | semiautomática | no |
| HS-GOV-006 | DEBE | Los roles reubicados lo son solo si el rol lo permite y la ruta existe | automática | no |
| HS-INS-001 | DEBE | `AGENTS.md` existe en la raíz | automática | no |
| HS-INS-002 | DEBE | `AGENTS.md` cita literalmente los comandos `setup`, `check` y `test` del manifiesto | automática | sí |
| HS-INS-004 | NO DEBE | Los archivos de instrucciones no contienen estado de tareas | manual | sí |
| HS-INS-005 | DEBE | Los `@imports` y enlaces relativos de los archivos de instrucciones se resuelven | automática | sí |
| HS-INS-006 | DEBE | (claude-code) `CLAUDE.md` raíz existe e importa `@AGENTS.md` | automática | no |
| HS-INS-007 | NO DEBE | (claude-code) `CLAUDE.md` duplica contenido de `AGENTS.md` | automática | sí |
| HS-INS-008 | DEBERÍA | `AGENTS.md` enlaza al mapa de arquitectura, a las decisiones y a la política de seguridad | automática | sí |
| HS-CTX-001 | DEBERÍA | Cada archivo de instrucciones respeta el presupuesto de tamaño (200 líneas por defecto) | automática | sí |
| HS-ARC-001 | DEBE | Existe el mapa de arquitectura | automática | sí |
| HS-ARC-002 | DEBE | Existe el registro de decisiones del proyecto | automática | sí |
| HS-SEC-001 | DEBE | Existe la política de seguridad del repositorio | automática | sí |
| HS-SEC-002 | DEBE | CODEOWNERS asigna propietario a todas las rutas sensibles de configuración de agentes | automática | no |
| HS-SEC-003 | DEBE | (claude-code) Los archivos personales del agente están en `.gitignore` | automática | sí |
| HS-SEC-004 | NO DEBE | Hay secretos versionados en el repositorio | manual (regla en Fase 5) | no |
| HS-VER-001 | DEBE | El manifiesto declara los comandos `setup`, `check` y `test` | automática | no |
| HS-VER-002 | DEBE | `setup` y `check` terminan con código 0 sin interacción en un entorno limpio | automática (con `--run-commands`) | sí |
| HS-VER-003 | DEBERÍA | `setup` es idempotente | automática (con `--run-commands`) | sí |

El contenido mínimo de cada archivo (mapa de arquitectura, política de seguridad…) se especifica en las fichas de la Fase 2. En la v0.1 solo se comprueba que existen.

## 4. Waivers

1. Un waiver DEBE declararse en `waivers` del manifiesto con los campos `requirement`, `reason`, `approved_by`, `approved_on` y `expires` (HS-GOV-003).
2. Un waiver DEBE referirse a un requisito existente con `exentable: true`.
3. Entre `approved_on` y `expires` NO DEBE haber más de **90 días**. Se puede renovar con un nuevo `approved_on`.
4. Un waiver caducado es un error. La CLI avisa cuando faltan 14 días o menos.
5. El waiver suprime el fallo del requisito, pero el informe sigue mostrándolo como `waived` para que sea visible.
6. Las excepciones a requisitos no exentables solo puede autorizarlas el grupo de gobierno mediante un ADR (`GOVERNANCE.md` §5).

## 5. Severidad en la CLI

| Nivel del requisito | Severidad del hallazgo | ¿Hace fallar `harness check`? |
|---|---|---|
| DEBE / NO DEBE | `error` | Sí |
| DEBERÍA / NO DEBERÍA | `warning` | Solo con `--strict` |
| PUEDE | `info` | No |
