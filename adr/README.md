# Registro de decisiones de arquitectura (ADR) del estándar

Cada ADR tiene un `estado`: `propuesto`, `aprobado`, `aprobado-parcial`, `reemplazado` o `retirado`.
Solo el grupo de gobierno (ver `GOVERNANCE.md`) puede cambiar un ADR a `aprobado`.
Un ADR aprobado no se edita: se reemplaza por otro nuevo que lo cite en `reemplaza:`.

| ADR | Título | Estado |
|---|---|---|
| [ADR-001](ADR-001-tres-productos-y-un-repositorio-central-con-dos.md) | Tres productos y un repositorio central con dos líneas de versión | aprobado |
| [ADR-002](ADR-002-lenguaje-normativo-con-requisitos-identificados.md) | Lenguaje normativo con requisitos identificados | aprobado |
| [ADR-003](ADR-003-agents-md-como-fuente-unica-de-instrucciones-cla.md) | AGENTS.md como fuente única de instrucciones; CLAUDE.md como adaptador fino | aprobado |
| [ADR-004](ADR-004-manifiesto-de-instancia-y-descubrimiento-por-rol.md) | Manifiesto de instancia y descubrimiento por roles | aprobado |
| [ADR-005](ADR-005-estado-de-tareas-un-archivo-por-tarea-en-lugar-d.md) | Estado de tareas: un archivo por tarea en lugar de una lista compartida | aprobado |
| [ADR-006](ADR-006-contrato-de-comandos-independiente-del-stack.md) | Contrato de comandos independiente del stack | aprobado |
| [ADR-007](ADR-007-niveles-de-conformidad-n0n3-y-waivers-con-caduci.md) | Niveles de conformidad N0–N3 y waivers con caducidad | aprobado |
| [ADR-008](ADR-008-lenguaje-y-forma-de-distribucion-de-la-cli.md) | Lenguaje y forma de distribución de la CLI | aprobado-parcial |
| [ADR-009](ADR-009-guidance-frente-a-enforcement-los-controles-crit.md) | Guidance frente a enforcement: los controles críticos viven en la plataforma y en la CI | aprobado |
| [ADR-010](ADR-010-autorizacion-de-merge-y-despliegue-separada-de-l.md) | Autorización de merge y despliegue separada de la revisión por agentes | propuesto |
| [ADR-011](ADR-011-concurrencia-tarea-rama-worktree-con-lease-y-pro.md) | Concurrencia: tarea → rama → worktree, con lease y propiedad por segmento | propuesto |
| [ADR-012](ADR-012-skills-fuente-neutra-en-agents-skills-y-copia-ge.md) | Skills: fuente canónica en `.claude/skills/` con perfil portable (rev. 2) | aprobado |
| [ADR-013](ADR-013-la-configuracion-de-agentes-es-codigo-sensible.md) | La configuración de agentes es código sensible | aprobado |
| [ADR-014](ADR-014-mapa-de-segmentos-como-artefacto-pivote.md) | Mapa de segmentos como artefacto pivote | propuesto |
| [ADR-015](ADR-015-cada-mecanismo-tiene-condicion-de-retirada-y-se.md) | Cada mecanismo tiene condición de retirada y se evalúa por ablación | propuesto |
| [ADR-016](ADR-016-transicion-a-done-en-el-pr-verificada-por-check.md) | La transición a `done` ocurre en el propio PR y la verifica un check requerido | aprobado |
| [ADR-017](ADR-017-distribucion-de-componentes-por-copia-versionada.md) | Distribución de componentes por copia versionada con lockfile y control de deriva | propuesto |
