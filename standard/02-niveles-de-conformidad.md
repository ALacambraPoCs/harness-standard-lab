---
documento: HS-02
titulo: Niveles de conformidad y waivers
version_estandar: 0.4.0
estado: borrador
fecha: 2026-10-19
adr: [ADR-004, ADR-007]
caracter: normativo
---

# 02 · Niveles de conformidad y waivers

## 1. Niveles

Los niveles son **acumulativos**: cumplir un nivel exige cumplir todos los inferiores. Cada requisito declara en `conformidad` los niveles en los que aplica.

| Nivel | Nombre | Garantía | Uso de agentes que habilita (máximo) | Estado en 0.2.0 |
|---|---|---|---|---|
| **N0** | Legible por agentes | Una persona o un agente sin contexto previo entiende el repositorio, lo prepara y lo verifica sin preguntar a nadie. La configuración de agentes está protegida. | Asistencia interactiva, con la persona responsable supervisando cada paso | **Requisitos definidos** (§3) |
| **N1** | Trabajo verificado | "Hecho" significa verificado por la CI con evidencia, no declarado por el agente. | Un agente por tarea; revisión humana del PR | **Requisitos definidos** en 0.2.0 (§3b) |
| **N2** | Concurrente | Varias personas y agentes trabajan en paralelo sin interferir. | Varios agentes en paralelo en segmentos distintos | Fase 4 |
| **N3** | Autonomía supervisada | La supervisión humana se aplica según el riesgo y las excepciones. | Loops y automatizaciones; merge sin intervención humana solo en clases de riesgo bajo | Fases 5–6 |

## 2. Reglas de los niveles

1. Toda instancia DEBE declarar su nivel en `standard.level` del manifiesto (HS-GOV-001).
2. Un repositorio que adopta el estándar por primera vez DEBERÍA declarar N0 y subir de nivel progresivamente. Es aceptable entrar directamente en N1 o superior en un greenfield creado con la plantilla.
3. Una instancia NO DEBE usar agentes en paralelo sobre el mismo repositorio (uso propio de N2) sin cumplir N1. Esta regla es organizativa hasta que la Fase 4 defina los controles técnicos.
4. El uso de agentes que habilita cada nivel es un **máximo**. Lo que pueda imponerse técnicamente se impondrá en las Fases 4 y 5. El resto se audita.
5. **Nivel efectivo.** La CLI calcula el nivel más alto en el que se cumplen todos los requisitos DEBE y NO DEBE aplicables, contando los waivers vigentes como cumplidos, y lo compara con el declarado.
6. **Degradación.** Si el check de conformidad falla de forma sostenida en la rama principal, el nivel efectivo baja y se notifica al propietario de la instancia. El umbral y el mecanismo se definen en la Fase 9.
7. **Versión declarada (D-029).** Un requisito solo aplica si su campo `desde` es menor o igual que `standard.version` del manifiesto. Cada nivel existe a partir de una versión (`niveles_desde` en `requirements.yaml`): N1 exige declarar 0.2.0 o posterior. Así, publicar requisitos nuevos no rompe instancias existentes: se adoptan al migrar la versión declarada.

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

El contenido mínimo de cada archivo se especifica en las fichas (`standard/04-archivos/`). En 0.1.0 solo se comprueba que existen; 0.2.0 añade las anclas obligatorias (§3b).

## 3b. Requisitos añadidos en 0.2.0 (F2.5) — estado: propuestos

Aplican solo a instancias que declaran `standard.version` ≥ 0.2.0 (regla 7). «En el PR» significa que los verifican `harness tasks validate --base` y `harness pr check` en el workflow `harness-tasks-lifecycle.yml`, no `harness check`.

**Nuevos en N0**

| ID | Nivel | Requisito (resumen) | Verificación | Exentable |
|---|---|---|---|---|
| HS-GOV-008 | DEBE | Las rutas versionadas son portables | automática | no |
| HS-INS-011 | DEBE | Las instrucciones de segmento declaran su ámbito | automática | sí |
| HS-INS-012 | NO DEBERÍA | Las instrucciones de segmento no duplican la raíz | automática | sí |
| HS-INS-013 | DEBE | (claude-code) Cada segmento con AGENTS.md tiene su adaptador CLAUDE.md | automática | no |
| HS-INS-014 | DEBERÍA | (claude-code) @AGENTS.md es la primera línea de cada CLAUDE.md | automática | sí |
| HS-INS-015 | NO DEBERÍA | (claude-code) El adaptador de Claude Code tiene una sola ubicación | automática | sí |
| HS-CTX-003 | DEBERÍA | La cadena de AGENTS.md cabe en 32 KiB | automática | sí |
| HS-CTX-004 | DEBERÍA | Las referencias externas indican su procedencia | automática | sí |

**Nivel N1** (además de todos los de N0)

| ID | Nivel | Requisito (resumen) | Verificación | Exentable |
|---|---|---|---|---|
| HS-GOV-007 | DEBERÍA | El manifiesto declara el idioma de la documentación | automática | sí |
| HS-INS-009 | DEBE | AGENTS.md raíz tiene las secciones obligatorias | automática | sí |
| HS-INS-010 | DEBERÍA | AGENTS.md raíz describe el flujo de trabajo | automática | sí |
| HS-CTX-002 | DEBERÍA | Las restricciones duras caben en su presupuesto | automática | sí |
| HS-ARC-003 | DEBE | El mapa de arquitectura tiene las secciones obligatorias | automática | sí |
| HS-ARC-004 | DEBE | El índice de decisiones enumera todos los ADR | automática | sí |
| HS-ARC-005 | DEBE | Cada ADR tiene frontmatter válido | automática | sí |
| HS-ARC-006 | NO DEBERÍA | Un ADR aceptado no se reescribe | automática · en el PR | sí |
| HS-SEC-005 | DEBE | La política de seguridad tiene las secciones obligatorias | automática | sí |
| HS-SEC-006 | NO DEBE | Un PR no oculta que toca rutas sensibles | automática · en el PR | no |
| HS-CI-001 | DEBE | Existe la plantilla de PR | automática | sí |
| HS-CI-002 | DEBE | El cuerpo del PR declara tarea y riesgo | automática · en el PR | no |
| HS-CI-003 | DEBE | El ciclo de vida de tareas es un check requerido | semiautomática | no |
| HS-STA-001 | DEBE | Existe la estructura de tareas | automática | sí |
| HS-STA-002 | DEBE | Cada tarea es válida | automática | no |
| HS-STA-003 | DEBE | Las tareas están en su carpeta y no se borran | automática | no |
| HS-STA-004 | DEBE | Solo hay transiciones de estado permitidas | automática · en el PR | no |
| HS-STA-005 | DEBE | done solo con aceptación verificada por la CI | automática · en el PR | no |
| HS-STA-006 | DEBERÍA | El índice de tareas está al día | automática | sí |

## 3c. Requisitos añadidos en 0.3.0 (F3.3) — estado: aprobados (D-037)

Aplican a instancias que declaran `standard.version` ≥ 0.3.0 (regla 7). Los de ámbito «repo central» los verifica `harness catalog validate` en la CI del repositorio del estándar.

| ID | Nivel | Niveles | Requisito (resumen) | Verificación |
|---|---|---|---|---|
| HS-CMP-001 | DEBE | N0,N1,N2,N3 | (claude-code) Las skills cumplen la especificación de Agent Skills | automática |
| HS-CMP-002 | DEBERÍA | N0,N1,N2,N3 | (claude-code) Las skills usan solo los campos de su perfil | automática |
| HS-CMP-003 | NO DEBERÍA | N0,N1,N2,N3 | No se versiona .agents/skills en la v1 | automática |
| HS-CMP-004 | DEBE | N0,N1,N2,N3 | (claude-code) Los subagentes tienen frontmatter válido | automática |
| HS-CMP-005 | DEBERÍA | N1,N2,N3 | (claude-code) Los subagentes declaran sus herramientas | automática |
| HS-CMP-006 | DEBE | N0,N1,N2,N3 | (claude-code) Los hooks de comando referencian scripts versionados | automática |
| HS-CMP-007 | NO DEBE | N1,N2,N3 | (claude-code) Los hooks no deterministas no se presentan como control | semiautomática |
| HS-CMP-008 | DEBERÍA | N0,N1,N2,N3 | (claude-code) La versión mínima de Claude Code es la del adaptador | automática |
| HS-SEC-007 | DEBE | N1,N2,N3 | (claude-code) settings.json impide leer y editar .env | automática |
| HS-SEC-008 | DEBE | N1,N2,N3 | (claude-code) settings.json pide confirmación para editar rutas sensibles | automática |
| HS-SEC-009 | DEBE | N1,N2,N3 | (claude-code) settings.json no habilita modos ni MCP sin control | automática |
| HS-CI-004 | DEBE | N1,N2,N3 | El agente en CI no carga la configuración del repositorio | automática |
| HS-CMP-010 | DEBE | repo central | Las entradas del catálogo son válidas y coherentes | automática |
| HS-CMP-011 | DEBE | repo central | Cada componente tiene ficha de 17 puntos | automática |
| HS-CMP-012 | DEBE | repo central | Las skills del catálogo cumplen su especificación y perfil | automática |
| HS-CMP-013 | DEBE | repo central | El ciclo de vida y la versión de los componentes son coherentes | automática |

## 3d. Requisitos añadidos en 0.4.0 (F3.5) — estado: aprobados (D-039)

| ID | Nivel | Niveles | Requisito (resumen) | Verificación |
|---|---|---|---|---|
| HS-CMP-009 | DEBERÍA | N0,N1,N2,N3 | Los componentes de `.harness/components.lock` están instalados sin deriva (ADR-017) | automática |

## 3e. Requisitos añadidos en 0.5.0 (F3.7) — estado: aprobados (D-041…D-043)

Solo aplican a instancias que declaran `standard.version` ≥ 0.5.0 (regla 7, D-029).

| ID | Nivel | Niveles | Requisito (resumen) | Verificación |
|---|---|---|---|---|
| HS-SEC-010 | DEBE | N1,N2,N3 | `settings.json` fija `disableAutoMode: "disable"` | automática |
| HS-SEC-011 | DEBERÍA | N1,N2,N3 | `ask` para `gh api` y `deny` para `gh repo delete`, `gh secret`, `gh ruleset` y `gh auth` | automática |
| HS-SEC-012 | DEBERÍA | N1,N2,N3 | Las reglas `allow` no abren intérpretes, red, borrado, `git`/`gh` en general ni la ejecución del contrato | automática |

## 3f. Requisitos añadidos en 0.6.0 (F5.2) — estado: aprobados (D-058)

| ID | Nivel | Niveles | Requisito (resumen) | Verificación |
|---|---|---|---|---|
| HS-CI-005 | DEBE | N1,N2,N3 | El riesgo declarado en el PR no es menor que la clase que calcula `harness pr risk` (rutas críticas → alto; configuración de agentes, pruebas borradas o criterios cambiados → medio) | automática (PR) |

## 3g. Requisitos añadidos en 0.7.0 (F5.3) — estado: aprobados (D-062, D-063)

| ID | Nivel | Niveles | Requisito (resumen) | Verificación |
|---|---|---|---|---|
| HS-CI-006 | DEBE | N1,N2,N3 | `harness platform check` periódico y sin fallos: PR obligatorio, checks requeridos, sin force push ni borrado, puerta de riesgo alto con revisores; en N2+, aprobaciones, Code Owners y último push | semiautomática (plataforma) |
| HS-CI-007 | DEBE | N1,N2,N3 | Workflows sin `pull_request_target`, sin interpolar datos no confiables en `run:`, con `permissions:` de nivel superior en lectura, y sin escritura en jobs con credenciales del modelo | automática |
| HS-CI-008 | DEBERÍA | N1,N2,N3 | Actions fijadas a SHA (las del estándar, a `cli-v…`) y `merge_group` en los workflows de PR | automática |

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
