---
documento: F0-01
titulo: Inventario de fuentes y análisis (patrones, contradicciones, lagunas)
estado: borrador para revisión
version: 0.1.0
fecha: 2026-10-19
---

# F0-01 · Inventario de fuentes y análisis

## 1. Alcance

Este documento hace tres cosas:

- Inventaría las fuentes que hay en la carpeta `Harness-engineering`.
- Clasifica su fiabilidad.
- Extrae los patrones que se repiten en ellas, sus contradicciones y lo que no cubren.

Sirve de base para la arquitectura (F0-02) y para las decisiones (F0-03).

Notación:

- **[Fuente]** significa que la fuente lo afirma.
- **[Inferencia]** es una conclusión propia.
- **[Verificado 2026-10-19]** indica que se ha comprobado en la documentación oficial en esa fecha.

## 2. Inventario y fiabilidad

### 2.1 Clasificación de fiabilidad

| Nivel | Tipo | Uso permitido en el estándar |
|---|---|---|
| **T1** | Especificación o documentación oficial vigente | Puede fundamentar formatos, rutas y capacidades. |
| **T2** | Informe de ingeniería del fabricante (experiencia propia) | Puede fundamentar principios y patrones. No sirve para fijar umbrales normativos. |
| **T3** | Análisis académico o de terceros con método declarado | Puede fundamentar principios y riesgos. Las capacidades de producto que mencione hay que verificarlas en T1. |
| **T4** | Material didáctico (curso) | Solo sirve como catálogo de patrones y plantillas de partida. Sus cifras no son evidencia. |
| **T5** | Comunidad (blogs, foros) | Complementaria. Nunca es base única. |

### 2.2 Corpus local

| ID | Documento | Nivel | Contenido útil | Advertencias |
|---|---|---|---|---|
| S-OAI-HE | *Harness engineering: leveraging Codex in an agent-first world* (OpenAI, R. Lopopolo, 11-02-2026). PDF en español. | T2 | `AGENTS.md` como índice (~100 líneas, p.5). `docs/` como sistema de registro (p.5-6). Planes de ejecución versionados (p.6). Arquitectura por capas impuesta con linters (p.8-9). Mensajes de error con remedio (p.9). Recolección de basura y *doc-gardening* (p.6, p.11-12). Worktree por cambio y observabilidad efímera (p.3-4). Revisión de agente a agente (p.3). | Es la experiencia de un solo equipo, sin grupo de control. Su filosofía de merge es "irresponsable en un entorno de bajo rendimiento" según el propio texto (p.10). El árbol de `docs/` aparece truncado en el PDF. |
| S-VILA | *Dive into Claude Code* (Liu et al., VILA Lab/MBZUAI-UCL, abr-2026), 46 p. | T3 | Separación entre *guidance* (probabilística) y *enforcement* (determinista) (p.20). Permisos deny-first en capas (p.9, p.13). Coste de contexto de cada mecanismo de extensión (Tabla 2, p.18). CVE por ejecución previa a la confianza (p.29). Coordinación con locks de archivo (p.23). Trece principios de diseño (Tabla 1, p.4). | Analiza una única versión (v2.1.88) obtenida del paquete npm. Hay feature flags. No es documentación oficial. |
| S-LHE | Curso *Learn Harness Engineering* (repo + 24 PDF que son copia del sitio): 14 lecciones, plantillas, *OpenAI advanced pack*, análisis de harness, skill `harness-creator`, `audit-harness.sh`. | T4 | Catálogo de artefactos (`AGENTS.md`, progreso, `feature_list`, `init.sh`, handoff, *clean state*, rúbrica, *sprint contract*, `goal.md`/`loop-state.md`, `graph.md`). Dos validadores reutilizables como arquitectura. | Muchas cifras están etiquetadas como "ejemplo didáctico" o "umbral didáctico ajustable". Hay párrafos de relleno (L01, L12, L13). Existen 4 esquemas incompatibles de lista de funciones. Las plantillas **no superan sus propios validadores**: 44, 20 y 56 sobre 100 (ejecución del 19-10-2026). |
| S-LHE-HD | Análisis de harness (Claude Code, Codex, DeepSeek, Pi) del curso | T4/T5 | Comparativa de mecanismos | Gran parte de lo que dicen de Claude Code y Codex procede de terceros o de la comunidad. El análisis de DeepSeek es el mejor fundamentado, porque cita la documentación oficial. |

Los PDF del curso no añaden nada al markdown del repositorio. Se comparó enlace por enlace y en bloques de texto, así que la fuente canónica de S-LHE es `learn-harness-engineering-main/docs/es/`.

### 2.3 Fuentes oficiales verificadas (T1, 19-10-2026)

| ID | Fuente | Relevancia |
|---|---|---|
| S-AGENTSMD | https://agents.md/ | Formato libre, anidamiento ("gana el más cercano"). Lo gobierna la Agentic AI Foundation (Linux Foundation). |
| S-SKILLS | https://agentskills.io/specification | `SKILL.md`: `name` (≤64 caracteres, igual al nombre del directorio), `description` (≤1024), `license`, `compatibility`, `metadata` y `allowed-tools` (experimental). Divulgación progresiva. Se valida con `skills-ref validate`. |
| S-CC-MEM | https://code.claude.com/docs/en/memory | Jerarquía de `CLAUDE.md`. `@imports` con un máximo de 4 saltos. Recomendación de <200 líneas. `.claude/rules/` con `paths:`. **Lee `AGENTS.md` solo si no existe ningún `CLAUDE.md`, `.claude/CLAUDE.md` ni `CLAUDE.local.md`** (desde v2.1.277). Alternativa portable documentada: `CLAUDE.md` con `@AGENTS.md`. |
| S-CC-SKILLS | https://code.claude.com/docs/en/skills | Skills en `.claude/skills/`, anidadas por subdirectorio, o en plugins. **No figura `.agents/skills/`** como ubicación. Admite campos de frontmatter adicionales, que fuera de Claude Code producen error. |
| S-CC-SET | code.claude.com/docs/en/{settings,permissions,sandboxing,hooks,sub-agents,plugins-reference,mcp,headless,github-actions,worktrees} | Precedencia de settings. Orden deny → ask → allow. Sandbox desactivado por defecto. Hooks (exit 2 bloquea; `onFailure: block`). Subagentes en `.claude/agents/`. Plugins y marketplace. `.mcp.json`. `claude -p --bare` para CI. `anthropics/claude-code-action@v1`. `--worktree`. |
| S-GH | docs.github.com: CODEOWNERS, rulesets, merge queue, `permissions:` de Actions | Controles de merge verificables. Incluye la regla "aprobación del último push por otra persona". |
| S-GIT | https://git-scm.com/docs/git-worktree | Una misma rama no puede estar activa en dos worktrees. Soporte de submódulos incompleto. |
| S-ETH-AGENTSMD | Gloaguen et al., *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*, ICLR 2026 MemAgents (https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd), leído 2026-10-21 | T3. Sin mejora de éxito; > 20 % más coste de inferencia; recomienda requisitos mínimos. Fundamenta el presupuesto de AGENTS.md (F2.2). |
| S-LULLA-AGENTSMD | Lulla et al., *On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents*, arXiv:2601.20404v2, leído 2026-10-21 | T3. 124 PR / 10 repos: −28,64 % tiempo mediano, −16,58 % tokens de salida, corrección comparable (asociación, no causalidad). |
| S-MATKLAD-ARCH | A. Kladov, *ARCHITECTURE.md* (https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), leído 2026-10-21 | T4/T5 (práctica reconocida). Mapa breve, invariantes, límites; nombrar en vez de enlazar. Base de la ficha `architecture.map`. |
| S-NYGARD-ADR | M. Nygard, *Documenting Architecture Decisions* (2011, https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | T4/T5 (práctica reconocida). Formato ADR: contexto, decisión, consecuencias; inmutables. Base de `decisions.dir`. |
| S-GH-PRTEMPLATE | docs.github.com: *Creating a pull request template for your repository*, leído 2026-10-21 | T1. Ubicaciones (`.github/`, raíz, `docs/`, `PULL_REQUEST_TEMPLATE/`); debe estar en la rama por defecto. |
| S-MCP | https://modelcontextprotocol.io/specification/latest (2026-07-28) | Buenas prácticas de seguridad: consentimiento, descripciones de herramientas no confiables, prohibición de *token passthrough*. |

Hay fuentes T1 y T2 que el corpus **cita pero no contiene**: los posts de ingeniería de Anthropic (*Effective harnesses for long-running agents*, *Harness design for long-running apps*, *Claude Code sandboxing*), el *cookbook* de planes de ejecución de OpenAI y el estudio de ETH Zurich sobre AGENTS.md. Se leerán en la fase en que cada una sea necesaria (ver F0-04).

Las capacidades de Codex, Copilot, Cursor y Gemini CLI también se verificaron (informe de subagente, 19-10-2026). Quedan fuera de la v1 por decisión del usuario, pero sirven para diseñar el núcleo de forma portable.

## 3. Patrones recurrentes

Un patrón entra aquí si aparece en al menos dos fuentes independientes.

| # | Patrón | Fuentes | Fuerza de la evidencia | Implicación para el estándar [Inferencia] |
|---|---|---|---|---|
| P1 | **El repositorio es el sistema de registro.** Lo que no está versionado en el repo no existe para el agente. | S-OAI-HE p.7; S-LHE L03; S-VILA p.20 ("transparent file-based configuration") | Alta (convergente) | El estándar define dónde vive cada tipo de conocimiento y prohíbe que la fuente de verdad esté fuera del repo. |
| P2 | **Archivo de entrada corto que funciona como índice, con detalle bajo demanda** (divulgación progresiva). | S-OAI-HE p.5; S-CC-MEM ("<200 líneas"); S-SKILLS (niveles de carga); S-LHE L04 | Alta en el principio. **Baja en el umbral exacto**: 100, 50-200 o <200 según la fuente, y ETH Zurich no encuentra mejora general con archivos de contexto, que además suben el coste más de un 20%. | Se norma la **función** (índice más restricciones duras). El tamaño se norma como presupuesto medible y ajustable, no como verdad empírica. |
| P3 | **Las instrucciones guían y los controles imponen.** Lo crítico se impone de forma mecánica. | S-VILA p.20; S-CC-MEM ("context, not enforced configuration"); S-OAI-HE p.8-10 (linters, "promovemos la regla al código") | Alta | Cada requisito del estándar se clasifica como *guidance* o *enforcement*. Ningún control crítico puede depender solo de lenguaje natural. |
| P4 | **El agente no certifica su propio trabajo.** La verificación es externa, con revisión separada de la ejecución. | S-LHE L08-L11; S-VILA p.22 (agente Verification), p.31; S-OAI-HE p.3 (revisión de agente a agente) | Media-alta | Las transiciones de estado ("hecho") solo las hace la CI o un script determinista, con evidencia enlazada. |
| P5 | **El feedback de revisión se convierte en reglas mecánicas**, con mensajes de error que indican el remedio. | S-OAI-HE p.9-10; S-LHE L10 (`ERROR/WHY/FIX`) | Media | Las reglas de arquitectura viven en un registro con campos *qué / por qué / cómo arreglar / fuente / condición de retirada*. |
| P6 | **El estado persiste fuera del contexto**: planes, progreso y decisiones en archivos. | S-OAI-HE p.6 (exec-plans); S-LHE L05, L12, L13; S-VILA p.23-24 | Alta | Se separan el conocimiento estable (arquitectura, decisiones) del estado de cada tarea (plan, progreso, evidencia). |
| P7 | **Aislamiento con un git worktree por tarea.** | S-OAI-HE p.3; S-VILA p.22; S-CC-SET (worktrees); S-LHE L13 | Alta | Es el mecanismo base de concurrencia. Faltan las convenciones de rama, entorno, puertos y limpieza. |
| P8 | **Arquitectura con límites explícitos impuestos por linters o tests estructurales.** | S-OAI-HE p.8-9; S-LHE L10; S-VILA p.30 (predice duplicación y violaciones de convenciones) | Media | No se impone una arquitectura de aplicación. Sí se exige que **los límites que el proyecto declare sean verificables**. |
| P9 | **La entropía crece: hace falta limpieza periódica y un registro de calidad.** | S-OAI-HE p.6, p.11-12; S-LHE L12 | Media | Se definen tareas de mantenimiento recurrentes (*doc-gardening*, deriva de reglas, documento de calidad) como workflows del catálogo. |
| P10 | **Simplificación por ablación:** se retira un componente y se comprueba si el resultado empeora. | S-LHE L02, L12; S-VILA (principio "minimal scaffolding") | Baja-media (sin datos) | Cada componente tiene una condición de retirada y una métrica asociada. Coincide con los principios del proyecto. |
| P11 | **La configuración del agente es superficie de ataque.** | S-VILA p.29 (CVE previos a la confianza); S-CC-SET (`-p` ejecuta hooks y `.mcp.json` sin `--bare`); S-MCP | Alta | `CODEOWNERS` y revisión humana obligatoria en las rutas de configuración de agentes. En CI, modo `--bare` con configuración explícita. |
| P12 | **Coste: cada mecanismo de extensión consume contexto de forma distinta.** MCP es alto, skills bajo y hooks prácticamente nulo. | S-VILA Tabla 2 p.18; S-SKILLS (~100 tokens por skill en el arranque) | Media | Hay que justificar los MCP. Para conocimiento procedimental se prefieren skills y para imponer reglas, hooks o CI. |

## 4. Contradicciones que el estándar debe resolver

| # | Contradicción | Dónde | Propuesta de resolución (se detalla en F0-03) |
|---|---|---|---|
| C1 | Nombre del archivo de progreso: `PROGRESS.md`, `progress.md`, `claude-progress.md`, `HANDOFF.md`, o progreso dentro del plan. | S-LHE L02/L05/L13, plantillas, `audit-harness.sh`; S-OAI-HE | El progreso vive **dentro del plan de cada tarea**, como en S-OAI-HE. No hay un archivo de progreso global compartido (ADR-005). |
| C2 | Cuatro esquemas incompatibles de lista de funciones (campos, valores de estado, formato de id). | S-LHE L07, L08, plantillas, skill, `audit-harness.sh` | Un único JSON Schema, normativo y versionado, con estados y transiciones definidos (ADR-005). |
| C3 | `AGENTS.md` y `CLAUDE.md` duplicados (las plantillas del curso) frente a `CLAUDE.md` que importa `@AGENTS.md` (project-01). | S-LHE; S-CC-MEM | `AGENTS.md` es la fuente única y `CLAUDE.md` es un adaptador fino (ADR-003). |
| C4 | Tamaño del archivo de entrada: 100, 50-100, 50-200 o <200 líneas. | S-LHE L02-L04; S-OAI-HE; S-CC-MEM | Presupuesto configurable que se mide en CI (ADR-009, Fase 2). |
| C5 | E2E siempre obligatorio (L09) frente a obligatorio solo si el cambio cruza componentes (L10). | S-LHE | La exigencia de verificación depende del riesgo y del tipo de cambio que declare la tarea (Fase 5). |
| C6 | Arquitectura documentada junto al módulo o centralizada en `docs/`. | S-LHE L03 frente a código de L03/L04; S-OAI-HE | Mapa central (`ARCHITECTURE.md` y mapa de segmentos) más `AGENTS.md` local por segmento cuando haga falta (ADR-014). |
| C7 | Autonomía total ("nunca pidas ayuda", "merge to main") frente a pausa humana antes del merge y CI/CD declarado *hands off*. | S-LHE L13 frente a L14 y `goal-template`; S-OAI-HE p.10-11 | La autonomía se gradúa por nivel de conformidad y por clase de riesgo. El merge a ramas protegidas siempre pasa por controles de la plataforma (ADR-010). |
| C8 | Permisos por defecto *fail-closed* frente a "allow". | `harness-creator/references` | Deny-first, como dice S-CC-SET (orden deny → ask → allow) y S-VILA. |
| C9 | Hooks tratados como "deterministas" cuando también existen hooks de tipo `prompt` y `agent`. | S-LHE-HD frente a S-VILA p.17 y S-CC-SET | El estándar distingue los hooks deterministas (`command`) de los no deterministas. Solo los primeros cuentan como control. |
| C10 | Cifras atribuidas de forma inconsistente: el experimento 20 min / 9 USD frente a 6 h / 200 USD se presenta como "aislado" en L09 y como "no aislado" en L01. | S-LHE | No se usan cifras del curso como justificación normativa. |

## 5. Lagunas: lo que ninguna fuente del corpus resuelve

Son precisamente las áreas que el usuario pide normar. Tendrán que diseñarse con fuentes T1 y con decisiones propias.

1. **Concurrencia entre personas y agentes.** Todas las plantillas suponen un único `feature_list.json` y un único archivo de progreso compartidos, lo que garantiza conflictos de merge. No hay propiedad de archivos, *leases* sobre tareas, contratos entre tareas ni tratamiento de conflictos semánticos.
2. **CI/CD y autorización de merge.** No se distingue entre la revisión informativa de un agente y la aprobación efectiva. No hay checks requeridos, *rulesets*, merge queue, despliegue ni *rollback*.
3. **Seguridad.** `SECURITY.md` es un marcador de posición. No hay modelo de amenazas de *prompt injection*, política de secretos, catálogo de acciones irreversibles ni auditoría.
4. **Segmentación de la codebase.** No existe un procedimiento. Solo aparece la arquitectura por capas de OpenAI, que es un caso concreto y no un método.
5. **Monorepo y multi-repo.** Los validadores solo miran la raíz. No hay herencia por paquete ni agregación.
6. **Gobierno del propio estándar.** No hay versión del estándar en la instancia, manifiesto de conformidad, excepciones (*waivers*) ni procedimiento de migración.
7. **Catálogo de componentes.** No hay contrato común para skills, agentes, hooks, plugins y workflows (propietario, versión, permisos, pruebas, retirada).
8. **Evidencia.** El campo `evidence` es texto libre, y la solución de referencia acepta como evidencia "lo revisé en el código". Falta enlazar cada evidencia a un run de CI, un commit o un artefacto.
9. **Medición.** No hay métricas instrumentadas de coste, tokens, intervenciones humanas, retrabajo ni tasa de reintentos, ni un protocolo de evaluación con repeticiones.
10. **Validación independiente del idioma.** Los validadores existentes buscan palabras clave en inglés. Las plantillas en español suspenden por los títulos, no por el contenido.

## 6. Lecciones de los validadores existentes

Ejecución sobre copias temporales, 19-10-2026.

| Objetivo | `validate-harness.mjs` | `audit-harness.sh` (CRITICAL) |
|---|---|---|
| Plantillas `docs/es/resources/templates` | 44/100 | 1/7 superados |
| `openai-advanced/repo-template` | 20/100 (todo en el mínimo) | 1/7 superados |
| `project-01/solution` | 56/100 | 4/7 superados |
| Scaffold generado por `create-harness` | 100/100 | 4/7 superados |

Conclusiones para el diseño de la herramienta de conformidad [Inferencia]:

- **Se reutiliza la arquitectura y no las reglas.** De ambos validadores sirve el pipeline carga → reglas → informe JSON/HTML → umbral, los niveles de severidad con su remedio, la autocomprobación (generar un scaffold y validarlo) y las anotaciones `why/source/remove when`.
- **Se descubren los archivos por rol, declarados en un manifiesto, y no por nombre fijo.** La validación usa esquemas (JSON Schema, frontmatter) y anclas estructurales, no títulos ni palabras clave.
- **La plantilla debe superar su propio validador en CI.** Es un criterio de aceptación del producto B.
