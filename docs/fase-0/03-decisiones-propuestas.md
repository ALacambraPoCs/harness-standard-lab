---
documento: F0-03
titulo: Decisiones arquitectónicas propuestas (ADR-001 … ADR-015)
estado: ADR-001…007, 009 y 013 APROBADOS (2026-10-19); resto propuestos
version: 0.1.0
fecha: 2026-10-19
depende_de: [F0-01, F0-02]
---

# F0-03 · Decisiones arquitectónicas propuestas

Los ADR marcados [APROBADO] fueron aprobados por el usuario sin cambios el 2026-10-19 (ver REGISTRO, D-005…D-013); el resto siguen **propuestos**. Para cada una se indica cuándo hay que decidirla:

- **[Bloquea F1]**: hay que aprobarla antes de redactar los requisitos.
- **[Fase N]**: puede decidirse en esa fase.

Cada ADR recoge la recomendación, la justificación, las alternativas, los riesgos y supuestos, la evidencia disponible y cómo se validará.

---

## ADR-001 · Tres productos y un repositorio central con dos líneas de versión [APROBADO 2026-10-19]

**Recomendación**
- Separar A (estándar), B (plantilla, CLI y CI) y C (instancia).
- A y B viven en un único repositorio central.
- A y B se versionan por separado:
  - A lleva su propio SemVer.
  - B declara qué rango de versiones de A soporta.
- Si A y B se contradicen, prevalece A.

**Justificación**
- El usuario pide distinguir los tres productos.
- Tenerlos en un solo repositorio permite que un cambio normativo y su regla de validación entren en el mismo PR, lo que garantiza la trazabilidad.
- Versionarlos por separado permite corregir la CLI sin "cambiar la norma".

**Alternativas**
- (a) Repositorios separados para A y B: más gobierno y peor trazabilidad. Se pospone hasta que haya varios equipos manteniéndolos.
- (b) Una sola versión para todo: obligaría a publicar versiones del estándar por bugs de la CLI.

**Riesgos y supuestos**
- Exige disciplina para no meter normas en la plantilla sin reflejarlas en A.
- Supuesto: habrá un grupo de gobierno con autoridad para aprobar cambios en A.

**Evidencia**
- Decisión de diseño propia. No hay fuente externa.
- Lección del corpus: las plantillas del curso no superan sus propios validadores (F0-01 §6), por falta de acoplamiento entre normas y herramientas.

**Validación**
- La matriz de trazabilidad se genera en CI.
- Un PR que añada un requisito automatizable sin regla ni fixtures falla.

## ADR-002 · Lenguaje normativo con requisitos identificados [APROBADO 2026-10-19]

**Recomendación**
- Usar DEBE / DEBERÍA / PUEDE (RFC 2119/8174 en español).
- Cada requisito tiene un ID `HS-<DOMINIO>-NNN` y lleva los atributos:
  - `naturaleza`: guidance o enforcement.
  - `verificacion`: automática, semiautomática o manual.
  - `conformidad`: niveles a los que aplica.
  - `fuentes`.
  - `retirada`.
- Todo ello se registra en `requirements.yaml`.

**Justificación**
- Permite comprobar la conformidad, generar informes y aplicar excepciones (waivers) a nivel de requisito.
- Hace explícito el principio del proyecto: "cada mecanismo tiene propósito, responsable, coste, validación y condición de retirada".

**Alternativas**
- Prosa sin IDs: no se puede verificar ni trazar.
- Usar solo el código de las reglas como norma: mezcla A con B.

**Riesgos**
- Burocracia si se definen demasiados requisitos.
- Mitigación: presupuesto de requisitos por dominio y revisión por ablación (ADR-015).

**Evidencia**
- RFC 2119/8174 es la práctica estándar en especificaciones.
- Las anotaciones `why/source/remove when` de `audit-harness.sh` (S-LHE) son un precedente.

**Validación**
- La CLI genera un informe de cobertura que indica el porcentaje de requisitos automatizables que tienen regla.

## ADR-003 · AGENTS.md como fuente única de instrucciones; CLAUDE.md como adaptador fino [APROBADO 2026-10-19]

**Recomendación**
- El núcleo usa `AGENTS.md`, en la raíz y anidado por segmento.
- El adaptador de Claude Code es un `CLAUDE.md` que contiene `@AGENTS.md` más únicamente lo que es exclusivo de Claude Code, por ejemplo cómo usar sus subagentes.
- Se prohíbe duplicar contenido entre ambos archivos.

**Justificación**
- Según S-CC-MEM (verificado el 19-10-2026), Claude Code solo lee `AGENTS.md` de forma nativa si no existe ningún `CLAUDE.md`, `.claude/CLAUDE.md` o `CLAUDE.local.md`.
- Por tanto, un desarrollador que cree su `CLAUDE.local.md` personal desactiva sin darse cuenta la lectura de `AGENTS.md`.
- El import `@AGENTS.md` funciona con cualquier configuración y es la alternativa portable que documenta Claude Code.
- AGENTS.md lo leen también Codex, Copilot y Cursor (S-AGENTSMD), lo que deja abierta la puerta a futuros adaptadores.

**Alternativas**
- (a) Solo `CLAUDE.md`: ata el núcleo a un proveedor.
- (b) Lectura nativa sin `CLAUDE.md`: frágil, por el problema de `CLAUDE.local.md`.
- (c) Symlink: la documentación de Claude Code lo desaconseja con Windows, y el usuario trabaja en Windows.
- (d) Contenido duplicado, como en las plantillas del curso: provoca contradicciones (C3).

**Riesgos**
- El límite de 4 saltos de `@import` (S-CC-MEM).
- Los imports no ahorran contexto, porque se cargan al arrancar.
- Hay que vigilar el tamaño total: regla de presupuesto en ADR-009.

**Evidencia**
- S-CC-MEM, secciones "AGENTS.md" e "Import additional files".
- S-AGENTSMD.
- S-OAI-HE p.5.

**Validación**
- Regla de la CLI: `CLAUDE.md` contiene `@AGENTS.md` y no repite secciones del núcleo.
- Prueba manual en Claude Code: en una sesión interactiva se ve la línea de carga de instrucciones.

## ADR-004 · Manifiesto de instancia y descubrimiento por roles [APROBADO 2026-10-19]

**Recomendación**
- `.harness/manifest.yaml` es obligatorio y se valida con JSON Schema.
- Contiene: versión del estándar, nivel de conformidad, adaptadores con su versión mínima, contrato de comandos, roles cuya ruta difiere de la ruta por defecto, ruta del mapa de segmentos y waivers con caducidad.
- La CLI valida por **rol**, no por nombre fijo, y siempre con esquemas o anclas estructurales en lugar de títulos.

**Justificación**
- Los validadores existentes fallan por depender de nombres y del idioma (F0-01 §6).
- Los brownfield necesitan poder declarar dónde está ya cada cosa.

**Alternativas**
- (a) Convención estricta sin manifiesto: es más simple, pero bloquea la adopción en brownfield.
- (b) Configurar dentro de `package.json` o `pyproject`: depende del stack.

**Riesgos**
- Que el manifiesto se use para declarar excepciones sin límite.
- Mitigación: los waivers requieren aprobador y fecha de caducidad, y las rutas alternativas solo son válidas para roles que lo permitan.

**Evidencia**
- Los fallos de `validate-harness.mjs` y `audit-harness.sh` documentados en F0-01 §6.

**Validación**
- El mismo repositorio de ejemplo pasa la validación con rutas por defecto y con rutas alternativas declaradas.

## ADR-005 · Estado de tareas: un archivo por tarea en lugar de una lista compartida [APROBADO 2026-10-19]

**Recomendación**
- Sustituir el `feature_list.json` y el archivo de progreso globales por **un archivo por tarea o plan**: Markdown con frontmatter validado por esquema.
- Campos del frontmatter: id, título, propietario, segmento(s), estado, dependencias, clase de riesgo, criterios de aceptación ejecutables y evidencia (enlace a run de CI o commit).
- Los archivos viven en `docs/plans/active|completed/`, o en `.harness/tasks/` si se separa estado y plan (detalle en Fase 2).
- El índice se **genera**; no se edita a mano.
- Las transiciones a `done` solo las hace la CI o la CLI cuando la verificación pasa.

**Justificación**
- Un archivo compartido es un punto de conflicto garantizado cuando varias personas y agentes trabajan en paralelo (laguna 1 de F0-01).
- S-OAI-HE p.6 ya ubica el progreso y las decisiones dentro de cada plan de ejecución.
- Resuelve las contradicciones C1 y C2.
- Mantiene el principio P4: el agente no se certifica a sí mismo.

**Alternativas**
- (a) Lista JSON única con un esquema unificado: sirve para el nivel N1 en un repositorio pequeño, pero no escala a N2.
- (b) Estado fuera del repositorio (issues de GitHub): contradice P1, aunque **puede complementar** el archivo mediante enlaces. Decisión de detalle en la Fase 4.

**Riesgos**
- Más archivos.
- Hace falta un esquema de estados claro, que incluya `regressed`, porque el curso no lo contempla (contradicción C9 del informe de lecciones).

**Evidencia**
- S-OAI-HE p.6.
- S-LHE L07 y L08 (pass-gate).
- S-VILA p.23: una lista compartida coordinada mediante locks.

**Validación**
- Simulación con 3 o más tareas concurrentes en worktrees: no se producen conflictos de merge en los archivos de estado.

## ADR-006 · Contrato de comandos independiente del stack [APROBADO 2026-10-19]

**Recomendación**
- El estándar define **roles de comando**:
  - Obligatorios: `setup`, `check` (rápido: lint, tipos y tests unitarios) y `test`.
  - Condicionales: `e2e`, `build`, `dev`, `clean`.
- El manifiesto declara cómo se invoca cada uno: Make, just o scripts del gestor de paquetes.
- Cada comando debe:
  - ser idempotente;
  - no ser interactivo;
  - devolver un código de salida significativo;
  - imprimir errores en formato orientado a remedio.

**Justificación**
- Es la pieza portable más repetida en el corpus (`make setup|test|check`, `init.sh`).
- Hace que AGENTS.md, la CI y la CLI usen exactamente los mismos comandos.

**Alternativas**
- Exigir `init.sh` o un Makefile concreto: impone herramientas a stacks que ya tienen las suyas.

**Riesgos**
- En monorepos, los comandos pueden depender del segmento.
- El contrato debe admitir comandos por segmento (Fase 4).

**Evidencia**
- S-LHE L02, L03, L06.
- S-OAI-HE p.3: la aplicación se puede arrancar en cada worktree.

**Validación**
- Regla de ejecución en CI: `setup` y `check` terminan con código 0 en un runner limpio.

## ADR-007 · Niveles de conformidad N0–N3 y waivers con caducidad [APROBADO 2026-10-19]

**Recomendación**
- Los cuatro niveles acumulativos de F0-02 §4.2.
- Un brownfield entra por N0.
- Ningún repositorio usa agentes en paralelo (N2) sin cumplir N1.

**Justificación**
- Permite adoptar el estándar de forma progresiva.
- Evita imponer el coste completo a repositorios pequeños.
- Liga la autonomía a las garantías que se han demostrado.

**Alternativas**
- Binario (cumple o no cumple): bloquea la adopción.
- Puntuación 0–100, como `validate-harness`: es manipulable y no indica qué garantías existen.

**Riesgos**
- Que N0 se perciba como "suficiente".
- Mitigación: el plan de adopción fija un nivel objetivo por repositorio y plazos.

**Evidencia**
- Decisión propia.
- La escalera de madurez de S-LHE L13 sirve de inspiración, pero sin datos que la respalden.

**Validación**
- Piloto con un greenfield (objetivo N2) y un brownfield (objetivo N1) en la Fase 8.

## ADR-008 · Lenguaje y forma de distribución de la CLI [Fase 7, recomendación provisional]

**Recomendación provisional**
- La CLI se distribuye como paquete versionado y como acción o workflow reutilizable de GitHub.
- Lenguaje: Python o Node/TypeScript, pendiente de decidir según el stack mayoritario del equipo.
- Para la actualización de instancias se propone evaluar **Copier**, que soporta actualizar proyectos derivados de una plantilla, frente a implementar `harness upgrade` propio.

**Justificación**
- Es lo que exige el punto 10 del encargo (actualizar y migrar).
- Las plantillas de GitHub y cookiecutter no permiten actualizar después de generar.

**Alternativas**
- Binario Go: no tiene dependencias, pero el equipo tendría que mantener otro lenguaje.
- Reutilizar `harness-creator`: no es viable porque sus reglas no sirven (F0-01 §6), aunque sí su arquitectura.

**Riesgos**
- La capacidad de actualización de Copier y su comportamiento con archivos modificados está **pendiente de verificar** en la Fase 7.

**Validación**
- Prueba de actualización de 0.x a 0.y sobre los ejemplos sin pérdida de cambios locales.

## ADR-009 · Guidance frente a enforcement: los controles críticos viven en la plataforma y en la CI [APROBADO 2026-10-19]

**Recomendación**
- Las instrucciones (AGENTS.md, skills) **solo** guían.
- Todo requisito de seguridad, integridad o merge se impone en tres capas:
  1. Permisos y sandbox del agente (deny-first).
  2. Hooks `command` deterministas, como respuesta rápida en local.
  3. **CI y rulesets de GitHub como autoridad final.**
- Los hooks de tipo `prompt` o `agent` no cuentan como control.
- Se incluye un presupuesto de tamaño medible para las instrucciones (líneas o bytes por archivo y en total cargado), con valores por defecto ajustables.

**Justificación**
- S-CC-MEM: las instrucciones son "context, not enforced configuration".
- S-VILA p.20: el cumplimiento es probabilístico.
- S-CC-SET: las reglas de Bash no son una frontera de seguridad.
- Los hooks locales se pueden desactivar o eludir. La CI no, si es un check requerido.

**Alternativas**
- Confiar en los hooks locales: no se puede verificar desde el servidor.

**Riesgos**
- Si la CI es lenta, el ciclo de feedback se alarga.
- Mitigación: hooks locales con la misma lógica que la CI, que da la autoridad final.

**Evidencia**
- S-CC-MEM, S-CC-SET (permissions, hooks), S-VILA p.13-14 y p.20, S-OAI-HE p.8-10.

**Validación**
- Prueba adversarial: un agente intenta un cambio prohibido con el hook desactivado y la CI lo rechaza.

## ADR-010 · Autorización de merge y despliegue separada de la revisión por agentes [Fase 5, principio en F1]

**Recomendación**
- La revisión de un agente es **informativa**: produce comentarios o checks.
- La autorización la dan los rulesets de GitHub:
  - checks requeridos;
  - revisión de code owner;
  - "aprobación del último push por alguien distinto de quien lo hizo";
  - merge queue con el evento `merge_group`.
- La aprobación humana obligatoria se fija según la clase de riesgo del cambio.
- El despliegue a producción requiere un environment protegido.

**Justificación**
- Es un principio del proyecto.
- S-GH: las reglas existen y son verificables.
- La filosofía de merge de S-OAI-HE p.10 depende explícitamente del contexto y no se puede trasladar tal cual a entornos corporativos.

**Alternativas**
- Merge automático sin humano en cambios de bajo riesgo: **posible en N3**, solo con una clasificación de riesgo determinista y auditoría.

**Riesgos**
- Fatiga de aprobación (S-VILA p.3, p.29: aprox. 93 % de aprobaciones).
- Mitigación: aprobar por riesgo y no por volumen.

**Validación**
- Los rulesets se exportan como código o checklist y la CLI comprueba su estado vía API. Está por verificar si es viable en la Fase 5.

## ADR-011 · Concurrencia: tarea → rama → worktree, con lease y propiedad por segmento [Fase 4]

**Recomendación**
- Por cada tarea: una rama y un worktree.
- Las tareas se reclaman con un *lease* (el propietario y la caducidad quedan en el archivo de la tarea, y se resuelve por merge en la rama principal o por la API de issues).
- Las tareas que tocan el mismo segmento se serializan, o se paralelizan solo con un contrato de interfaz explícito.
- Antes de integrar, rebase o merge contra la rama principal, y merge queue.

**Justificación**
- P7. S-GIT: una misma rama no puede estar activa en dos worktrees.
- S-VILA p.23: coordinación de tareas con locks de archivo.
- Claude Code tiene `--worktree` (S-CC-SET), aunque su aislamiento no detecta escrituras por la shell.

**Riesgos**
- Conflictos semánticos que git no detecta.
- Mitigación: checks de contrato y tests de integración en el merge queue.
- Riesgo adicional: entornos por worktree (puertos, `.env`, dependencias).

**Validación**
- Escenario de Fase 8: 3 agentes y 1 persona en paralelo, midiendo conflictos y retrabajo.

## ADR-012 · Skills: fuente neutra en `.agents/skills/` y copia generada en `.claude/skills/` [Fase 3, recomendación provisional]

**Recomendación**
- Las skills del núcleo se escriben con **solo los seis campos** de Agent Skills y viven en `.agents/skills/`.
- `harness sync` genera `.claude/skills/` (copia, no symlink, por Windows).
- La CI comprueba que no hay deriva entre ambas.
- Las extensiones exclusivas de Claude Code (`context: fork`, `paths`, etc.) solo se permiten en skills marcadas como de adaptador.

**Justificación**
- S-CC-SKILLS (verificado): Claude Code **no lee** `.agents/skills/`.
- Codex, Copilot y Cursor sí la leen (informe de especificaciones oficiales).
- Los campos extra de Claude producen error fuera de Claude Code (S-CC-SKILLS).

**Alternativa**
- En la v1 (solo Claude Code), escribir directamente en `.claude/skills/` limitándose a los campos de la especificación. Es más simple hoy, pero obliga a migrar cuando llegue el segundo adaptador.
- **Decisión pendiente:** simplicidad hoy frente a portabilidad mañana.

**Validación**
- `skills-ref validate` (S-SKILLS) en CI sobre `.agents/skills/`.

## ADR-013 · La configuración de agentes es código sensible [APROBADO 2026-10-19]

**Recomendación**
- `CODEOWNERS` con un propietario de seguridad o plataforma sobre:
  - `AGENTS.md` y todos los `**/AGENTS.md`;
  - `CLAUDE.md`;
  - `.claude/**`, `.agents/**`, `.mcp.json`, `.harness/**`;
  - `.github/workflows/**` y `.github/CODEOWNERS`.
- En CI, los agentes se ejecutan con `claude -p --bare` y configuración explícita.
- El job del agente tiene permisos `contents: read`. Los cambios se aplican en un job separado sin credenciales del modelo, siguiendo el patrón documentado por `openai/codex-action`.
- Los secretos se pasan solo al paso que los necesita.

**Justificación**
- S-VILA p.29: CVE por ejecución previa a la confianza.
- S-CC-SET: `-p` sin `--bare` ejecuta hooks y `.mcp.json` en carpetas no confiables.
- Copilot code review lee las instrucciones de la rama del PR, lo que permite a un PR modificar las reglas que revisan ese mismo PR.
- S-MCP: las descripciones de herramientas no son confiables.

**Riesgos**
- Fricción al cambiar instrucciones.
- Mitigación: propietarios por segmento para los `AGENTS.md` locales.

**Validación**
- Regla de la CLI: CODEOWNERS cubre todas las rutas sensibles.
- Revisión del workflow con un linter de Actions. La herramienta concreta se decide en la Fase 5.

## ADR-014 · Mapa de segmentos como artefacto pivote [Fase 4]

**Recomendación**
- Un `.harness/segments.yaml` producido por el método de análisis de la codebase. Para cada segmento: rutas, propósito, propietario, dependencias permitidas, contratos o interfaces públicas, comandos propios, clase de riesgo y política de paralelización.
- A partir de él se **generan o validan**: CODEOWNERS, los `AGENTS.md` locales, las reglas por ruta del adaptador, las reglas de dependencias y la detección de conflictos entre tareas.

**Justificación**
- Convierte la segmentación (punto 6 del encargo) en algo verificable.
- Unifica cinco mecanismos que, si no, se mantendrían por separado y acabarían divergiendo.
- No impone ninguna arquitectura de aplicación: la describe y la hace verificable (P8).

**Riesgos**
- Que el mapa no refleje el código real.
- Mitigación: una regla compara los imports con las dependencias declaradas, cuando el lenguaje lo permita.

**Validación**
- Aplicarlo a un brownfield grande en la Fase 8 y medir la cobertura de rutas y las violaciones detectadas.

## ADR-015 · Cada mecanismo tiene condición de retirada y se evalúa por ablación [Fase 6]

**Recomendación**
- Cada requisito y cada componente del catálogo declara: propósito, propietario, coste estimado (contexto, latencia, mantenimiento), métrica de eficacia y condición de retirada.
- Una revisión periódica desactiva componentes en un conjunto de tareas de referencia y compara resultados.

**Justificación**
- Es un principio del proyecto.
- P10.
- S-LHE L12 aporta un procedimiento, aunque sin datos.

**Riesgos**
- Las evaluaciones con modelos son ruidosas.
- Hace falta un protocolo con repeticiones y varianza, que no existe en el corpus.

**Validación**
- Protocolo de evaluación definido en la Fase 6. Un primer ciclo de ablación se ejecuta en el piloto.

---

## Resumen

| ADR | Tema | Cuándo decidir | Recomendación en una línea |
|---|---|---|---|
| 001 | Productos A/B/C | **Aprobado** | Un repositorio central, dos líneas de versión, A prevalece |
| 002 | Lenguaje normativo | **Aprobado** | DEBE/DEBERÍA/PUEDE con IDs y `requirements.yaml` |
| 003 | Instrucciones | **Aprobado** | AGENTS.md fuente; CLAUDE.md = `@AGENTS.md` + extras |
| 004 | Manifiesto | **Aprobado** | `.harness/manifest.yaml`, validación por roles |
| 005 | Estado de tareas | **Aprobado** | Un archivo por tarea; "hecho" lo marca la CI |
| 006 | Comandos | **Aprobado** | Contrato de roles de comando declarado en el manifiesto |
| 007 | Niveles | **Aprobado** | N0–N3 acumulativos con waivers que caducan |
| 008 | CLI | Fase 7 | Python o TS según el stack; evaluar Copier para actualizar |
| 009 | Guidance frente a enforcement | **Aprobado** | Lo crítico se impone en permisos, CI y rulesets |
| 010 | Merge y despliegue | Principio en F1, detalle en Fase 5 | La revisión del agente informa; los rulesets autorizan |
| 011 | Concurrencia | Fase 4 | Tarea → rama → worktree, con lease y segmentos |
| 012 | Skills | Fase 3 | `.agents/skills` fuente, `.claude/skills` generada |
| 013 | Configuración de agentes sensible | **Aprobado** | CODEOWNERS y CI con `--bare` y mínimo privilegio |
| 014 | Mapa de segmentos | Fase 4 | `segments.yaml` genera o valida CODEOWNERS, AGENTS locales y reglas |
| 015 | Retirada y ablación | Fase 6 | Todo mecanismo con métrica y condición de retirada |
