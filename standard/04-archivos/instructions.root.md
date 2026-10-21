---
rol: instructions.root
titulo: AGENTS.md raíz
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas, cli]
dependencias: [manifest, architecture.map, decisions.dir, security.policy, plans.dir, instructions.segment]
propietario: Tech lead del repositorio (revisión obligatoria de plataforma/harness por CODEOWNERS, ADR-013)
requisitos: [HS-INS-001, HS-INS-002, HS-INS-004, HS-INS-005, HS-INS-008, HS-CTX-001, "pendiente:F2.5"]
reglas: [core.instructions.root-exists, core.instructions.commands-match, core.instructions.references-resolve, core.instructions.links-core-docs, core.instructions.size-budget]
ejemplo_canonico: template/core/AGENTS.md
fuentes: [S-AGENTSMD, S-OAI-HE#p5, S-CC-MEM, S-ETH-AGENTSMD, S-LULLA-AGENTSMD, S-LHE#L04, ADR-003, ADR-009]
evolucion: >-
  MAJOR si se añade o elimina un ancla obligatoria o cambia el presupuesto por defecto; MINOR si se
  añade un ancla opcional; PATCH si es editorial.
---

# AGENTS.md raíz

> Ruta, obligatoriedad, nivel y capa: `standard/roles.yaml#instructions.root` (vista en `03-estructura-canonica.md`).

## Propósito

Es el **índice mínimo** que lee cualquier agente al empezar a trabajar en el repositorio. Le dice qué es el proyecto, cómo prepararlo y verificarlo, qué no debe hacer nunca y dónde está el detalle. **No es un manual.** El conocimiento extenso vive en los documentos enlazados (divulgación progresiva, PR-2).

**Fundamento de "mínimo":**

- El estudio de ETH Zurich (Gloaguen et al., ICLR 2026 MemAgents, S-ETH-AGENTSMD) no encontró mejora en la tasa de éxito con archivos de contexto. Observó un coste de inferencia más de un 20 % mayor y una exploración más amplia, y recomienda que los archivos escritos por personas describan *"only minimal requirements"*.
- Lulla et al. (arXiv 2601.20404, S-LULLA-AGENTSMD) midieron un 28,64 % menos de tiempo mediano y un 16,58 % menos de tokens de salida con AGENTS.md, con una corrección comparable. Los autores presentan esa relación como asociación, no como causalidad.
- Inferencia: el valor está en la información que el agente **no puede descubrir barato** (comandos canónicos, restricciones no evidentes, dónde está cada cosa). Repetir lo que el código ya dice solo añade coste.

## Contenido requerido

Las anclas son comentarios HTML en una línea propia, justo antes de la sección. No se ven al renderizar y no dependen del idioma (D-020). El título visible de la sección es libre.

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Qué es el proyecto, en 1–3 frases (propósito y usuarios), sin historia ni marketing | `<!-- harness:resumen -->` | pendiente:F2.5 | Automática (ancla presente) + revisión |
| Comandos canónicos `setup`, `check` y `test`, **literalmente** iguales a los del manifiesto, y cuándo ejecutar cada uno | `<!-- harness:comandos -->` | HS-INS-002 | Automática |
| Restricciones duras: lo que el agente **nunca** debe hacer, en imperativo, una por línea | `<!-- harness:restricciones -->` | pendiente:F2.5 | Automática (ancla y n.º de elementos) + revisión |
| Mapa: enlaces relativos al mapa de arquitectura, a las decisiones y a la política de seguridad, con una línea sobre cuándo leer cada uno | `<!-- harness:mapa -->` | HS-INS-008, HS-INS-005 | Automática |

## Contenido recomendado y opcional

| Elemento | Ancla | Cuándo |
|---|---|---|
| Flujo de trabajo: dónde está la tarea (`plans.active`), una tarea por rama y PR, quién marca `done` | `<!-- harness:flujo -->` | **Recomendado desde N1** (pendiente:F2.5) |
| Índice de instrucciones de segmento (`<segmento>/AGENTS.md`) | `<!-- harness:segmentos -->` | Si existen instrucciones de segmento (útil también para herramientas que no cargan AGENTS.md anidados) |
| Convenciones **no evidentes** del código (las que un linter no impone) | `<!-- harness:convenciones -->` | Opcional, solo si no caben en un linter |

**Restricciones duras: cómo escribirlas**

- Como máximo **15** por defecto, ajustable. Es un valor didáctico de S-LHE L04 y no está probado; se mide y se revisa en la Fase 6.
- Cada restricción DEBERÍA indicar qué control la impone. Ejemplo: `No modifiques .github/ (CODEOWNERS + ruleset)`. Si no la impone ningún control, es *guidance*. Las que protejan de un riesgo alto necesitan un control L4/L5 (ADR-009).
- Se escriben en positivo cuando hay alternativa. Ejemplo: "Usa `make check`; no ejecutes los tests uno a uno".

## Contenido excluido

| No incluir | Va en |
|---|---|
| Estado de tareas: progreso, pendientes, "estamos con…" | Archivo de tarea en `plans.active` (HS-INS-004) |
| Detalle de arquitectura, diagramas, listados de directorios | `architecture.map` |
| Justificación de decisiones | `decisions.dir` |
| Reglas de un solo segmento | `<segmento>/AGENTS.md` |
| Instrucciones exclusivas de una herramienta (subagentes de Claude, `/comandos`) | Su adaptador (`CLAUDE.md`, `.claude/`) |
| Consejos genéricos ("escribe código limpio", "sé cuidadoso") | En ningún sitio: consumen contexto sin aportar (S-ETH-AGENTSMD) |
| Lo que ya impone un linter, el tipado o la CI | En ningún sitio: la herramienta ya lo dice al fallar |
| Secretos, URLs internas con credenciales, datos personales | Gestor de secretos; nunca en el repositorio (HS-SEC-004) |
| Texto copiado de issues, tickets o webs sin revisar | Primero se revisa y se resume en un documento propio (PR-7) |
| Documentación de terceros extensa | `references.dir`, enlazada |

## Formato y convenciones

- **Markdown** según S-AGENTSMD, sin frontmatter. El nombre de archivo es exactamente `AGENTS.md`.
- **Presupuesto**: como máximo **200 líneas** por defecto (HS-CTX-001, alineado con S-CC-MEM). Recomendación interna: **100 líneas o menos**, el tamaño que describe S-OAI-HE p.5.
- **Presupuesto acumulado** (pendiente:F2.5): la suma de bytes de la cadena raíz más el segmento más profundo DEBERÍA ser como máximo **32 KiB**. Codex deja de cargar AGENTS.md al alcanzar ese límite y trunca en silencio los niveles más profundos (`project_doc_max_bytes`, verificado en la documentación oficial por el informe de especificaciones de F0).
- **Orden recomendado**: resumen → comandos → restricciones → flujo → mapa. Lo crítico va arriba (S-LHE L04, *lost in the middle*).
- **Idioma libre** (D-020); las anclas y los comandos no se traducen.
- **Enlaces relativos** al propio archivo. Sin rutas absolutas ni `~` (HS-INS-005).
- **Sin `@imports`** en AGENTS.md. Los imports son sintaxis de Claude Code y otras herramientas no los resuelven. El adaptador (`CLAUDE.md`) es quien importa.

## Ejemplo canónico

Plantilla completa en `template/core/AGENTS.md`. Ejemplo rellenado (unas 30 líneas):

```markdown
# payments-api

<!-- harness:resumen -->
API interna que calcula y liquida pagos de comercios. La consumen el backoffice y el servicio de conciliación.

<!-- harness:comandos -->
## Comandos
| Rol | Comando | Cuándo |
|---|---|---|
| setup | `make setup` | Al clonar o tras cambiar dependencias |
| check | `make check` | Tras cada cambio (lint, tipos, tests unitarios) |
| test  | `make test`  | Antes de pedir revisión |

<!-- harness:restricciones -->
## Nunca
- No modifiques `migrations/` ya publicadas; crea una nueva (revisión de DBA vía CODEOWNERS).
- No leas ni escribas `.env*` ni credenciales (deny en `.claude/settings.json`).
- No marques una tarea como `done`: lo hace la CI con evidencia.
- No añadas dependencias sin ADR.

<!-- harness:flujo -->
## Cómo trabajar
Tu tarea está en `docs/plans/active/T-NNNN-*.md`: respeta su alcance y criterios de aceptación. Una tarea = una rama = un PR.

<!-- harness:mapa -->
## Dónde está el detalle
- [Arquitectura y límites](docs/architecture/ARCHITECTURE.md): antes de tocar más de un módulo.
- [Decisiones](docs/decisions/README.md): antes de cambiar un patrón establecido.
- [Seguridad](docs/security/SECURITY.md): antes de tocar autenticación, datos o integraciones.
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe en la raíz | L4 (`core.instructions.root-exists`) | Vigente (N0) |
| Comandos literalmente iguales a los del manifiesto | L4 (`core.instructions.commands-match`) | Vigente (N0) |
| Enlaces e imports se resuelven | L4 (`core.instructions.references-resolve`) | Vigente (N0) |
| Enlaza los documentos núcleo | L4 (`core.instructions.links-core-docs`) | Vigente (N0, DEBERÍA) |
| Presupuesto de líneas | L4 (`core.instructions.size-budget`) | Vigente (N0, DEBERÍA) |
| Anclas `resumen`, `comandos`, `restricciones` y `mapa` presentes | L4 | Pendiente F2.5 (propuesta: N1) |
| N.º de restricciones como máximo el presupuesto | L4 | Pendiente F2.5 (DEBERÍA) |
| Presupuesto acumulado de 32 KiB | L4 | Pendiente F2.5 (DEBERÍA) |
| Sin estado de tareas ni consejos genéricos | Revisión humana (CODEOWNERS, L5) | Vigente (manual) |
| Cambios revisados por propietario de plataforma/harness | L5 (CODEOWNERS + ruleset) | Vigente (ADR-013) |

## Criterios de aceptación

1. `harness check` no reporta errores de las reglas `core.instructions.*`.
2. Las cuatro anclas obligatorias están presentes, cuando la F2.5 las active.
3. Una persona que no conoce el repositorio sabe, solo con este archivo, cómo prepararlo y verificarlo, qué no debe hacer y qué documento leer para cada tipo de cambio.
4. Ninguna línea repite información que ya esté en otro documento del núcleo o que imponga una herramienta.

## Ciclo de vida y evolución

- **Creación:** con `harness init` (Fase 7) o copiando `template/core/AGENTS.md`.
- **Actualización:** en el mismo PR que cambia un comando, una restricción o la ubicación de un documento. Una regla nueva solo entra si un fallo real la justifica: ¿qué error evita?
- **Revisión:** trimestral, o cuando cambie el modelo o la herramienta de agente. Cada restricción sin control asociado se cuestiona: se convierte en control (linter, CI, permiso) o se elimina (ADR-009, ADR-015).
- **Retirada:** el rol solo desaparece si AGENTS.md deja de ser un formato soportado por los adaptadores de la organización (HS-INS-001).
