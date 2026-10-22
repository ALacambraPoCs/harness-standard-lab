# Matriz de trazabilidad

Generada por `harness matrix`. No editar a mano.

| Requisito | Nivel | Niveles | Naturaleza | Verificación | Reglas | Fixtures no conformes |
|---|---|---|---|---|---|---|
| HS-GOV-001 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.manifest.valid` | nc-comandos-no-declarados<br>nc-manifiesto-ausente<br>nc-manifiesto-esquema |
| HS-GOV-002 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.manifest.standard-version` | nc-n1-con-version-0-1<br>nc-nivel-no-definido<br>nc-version-no-soportada |
| HS-GOV-003 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.waivers.valid` | nc-waiver-caducado<br>nc-waiver-demasiado-largo<br>nc-waiver-no-exentable |
| HS-GOV-004 | DEBE | N0,N1,N2,N3 | enforcement | semiautomatica | `core.ci.conformance-workflow` | nc-ci-ausente<br>nc-ci-sin-pull-request |
| HS-GOV-005 | DEBE | — | enforcement | manual | — | — |
| HS-GOV-006 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.roles.relocation` | nc-rol-no-reubicable<br>nc-rol-ruta-inexistente |
| HS-INS-001 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.instructions.root-exists` | nc-agents-ausente |
| HS-INS-002 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.instructions.commands-match` | nc-comandos-no-citados |
| HS-INS-004 | NO DEBE | N0,N1,N2,N3 | guidance | manual | — | — |
| HS-INS-005 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.instructions.references-resolve` | nc-agents-ausente<br>nc-decisiones-ausentes<br>nc-enlace-roto-y-ruta-personal<br>nc-import-roto<br>nc-mapa-ausente<br>nc-seguridad-ausente<br>nc-waiver-caducado |
| HS-INS-006 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.imports-agents` | nc-claude-ausente<br>nc-claude-import-en-codigo<br>nc-claude-sin-import |
| HS-INS-007 | NO DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.no-duplication` | nc-claude-duplica |
| HS-INS-008 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.instructions.links-core-docs` | nc-rol-ruta-inexistente<br>nc-sin-enlaces-nucleo |
| HS-CTX-001 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.instructions.size-budget` | nc-presupuesto-superado |
| HS-ARC-001 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.architecture.map-exists` | nc-mapa-ausente<br>nc-rol-ruta-inexistente<br>nc-waiver-caducado |
| HS-ARC-002 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.decisions.exists` | nc-decisiones-ausentes |
| HS-SEC-001 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.security.doc-exists` | nc-seguridad-ausente |
| HS-SEC-002 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.codeowners.sensitive-paths` | nc-codeowners-anulado-por-ultimo-patron<br>nc-codeowners-ausente<br>nc-codeowners-sin-mcp |
| HS-SEC-003 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.local-files-ignored` | nc-gitignore-local |
| HS-SEC-004 | NO DEBE | N0,N1,N2,N3 | enforcement | manual | — | — |
| HS-VER-001 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.commands.declared` | nc-comandos-no-declarados |
| HS-VER-002 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.commands.execute` | nc-setup-falla |
| HS-VER-003 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.commands.idempotent` | nc-setup-falla<br>nc-setup-no-idempotente |
| HS-GOV-007 | DEBERÍA | N1,N2,N3 | guidance | automatica | `core.manifest.docs-language` | nc-sin-idioma |
| HS-GOV-008 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.paths.portable` | nc-ruta-no-portable |
| HS-INS-009 | DEBE | N1,N2,N3 | guidance | automatica | `core.instructions.root-anchors` | nc-agents-sin-anclas |
| HS-INS-010 | DEBERÍA | N1,N2,N3 | guidance | automatica | `core.instructions.flow-anchor` | nc-agents-sin-flujo |
| HS-INS-011 | DEBE | N0,N1,N2,N3 | guidance | automatica | `core.instructions.segment-anchors` | nc-segmento-sin-ambito |
| HS-INS-012 | NO DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.instructions.segment-no-duplication` | nc-segmento-duplica-raiz |
| HS-INS-013 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.segment-adapter` | nc-segmento-sin-claude |
| HS-INS-014 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.import-first` | nc-claude-import-no-primero |
| HS-INS-015 | NO DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.single-location` | nc-claude-dos-ubicaciones |
| HS-CTX-002 | DEBERÍA | N1,N2,N3 | guidance | automatica | `core.instructions.constraints-budget` | nc-demasiadas-restricciones |
| HS-CTX-003 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.instructions.chain-bytes` | nc-cadena-agents-32k |
| HS-CTX-004 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.references.provenance` | nc-referencias-sin-procedencia |
| HS-ARC-003 | DEBE | N1,N2,N3 | guidance | automatica | `core.architecture.anchors` | nc-arquitectura-sin-invariantes |
| HS-ARC-004 | DEBE | N1,N2,N3 | guidance | automatica | `core.decisions.index` | nc-adr-fuera-del-indice |
| HS-ARC-005 | DEBE | N1,N2,N3 | guidance | automatica | `core.decisions.frontmatter` | nc-adr-frontmatter |
| HS-ARC-006 | NO DEBERÍA | N1,N2,N3 | guidance | automatica | `pr.adr-immutable` | test_tasks.py |
| HS-SEC-005 | DEBE | N1,N2,N3 | guidance | automatica | `core.security.anchors` | nc-seguridad-sin-controles |
| HS-SEC-006 | NO DEBE | N1,N2,N3 | enforcement | automatica | `pr.sensitive`<br>`pr.risk-sensitive` | test_tasks.py |
| HS-CI-001 | DEBE | N1,N2,N3 | guidance | automatica | `core.pr.template` | nc-sin-plantilla-pr |
| HS-CI-002 | DEBE | N1,N2,N3 | enforcement | automatica | `pr.anchors`<br>`pr.task`<br>`pr.trivial`<br>`pr.risk` | test_tasks.py |
| HS-CI-003 | DEBE | N1,N2,N3 | enforcement | semiautomatica | `core.ci.tasks-workflow` | nc-sin-workflow-tareas |
| HS-STA-001 | DEBE | N1,N2,N3 | guidance | automatica | `core.plans.structure` | nc-sin-plans |
| HS-STA-002 | DEBE | N1,N2,N3 | enforcement | automatica | `tasks.schema`<br>`tasks.naming`<br>`tasks.unique`<br>`tasks.body`<br>`tasks.depends` | nc-tarea-invalida |
| HS-STA-003 | DEBE | N1,N2,N3 | enforcement | automatica | `tasks.location`<br>`tasks.deleted` | nc-tarea-mal-ubicada<br>test_tasks.py |
| HS-STA-004 | DEBE | N1,N2,N3 | enforcement | automatica | `tasks.transition` | test_tasks.py |
| HS-STA-005 | DEBE | N1,N2,N3 | enforcement | automatica | `tasks.acceptance`<br>`tasks.done-pr` | nc-tarea-manual-sin-verificador<br>test_tasks.py |
| HS-STA-006 | DEBERÍA | N1,N2,N3 | guidance | automatica | `tasks.index` | nc-indice-tareas-desactualizado<br>nc-tarea-invalida<br>nc-tarea-mal-ubicada<br>nc-tarea-manual-sin-verificador |
| HS-CMP-001 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.skills-spec` | nc-skill-invalida |
| HS-CMP-002 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.skills-profile` | nc-skill-perfil |
| HS-CMP-003 | NO DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.skills.no-agents-dir` | nc-agents-skills-versionado |
| HS-CMP-004 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.agents-valid` | nc-subagente-invalido |
| HS-CMP-005 | DEBERÍA | N1,N2,N3 | guidance | automatica | `adapter.claude.agents-tools` | nc-subagente-sin-tools |
| HS-CMP-006 | DEBE | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.hooks-scripts` | nc-hook-script-ausente |
| HS-CMP-007 | NO DEBE | N1,N2,N3 | guidance | semiautomatica | `adapter.claude.hooks-nondeterministic` | nc-hook-prompt-como-control |
| HS-CMP-008 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `adapter.claude.min-version` | nc-min-version-antigua |
| HS-SEC-007 | DEBE | N1,N2,N3 | enforcement | automatica | `adapter.claude.settings-secrets` | nc-settings-ausente<br>nc-settings-sin-deny-env |
| HS-SEC-008 | DEBE | N1,N2,N3 | enforcement | automatica | `adapter.claude.settings-sensitive` | nc-settings-ruta-sensible-sin-ask |
| HS-SEC-009 | DEBE | N1,N2,N3 | enforcement | automatica | `adapter.claude.settings-modes` | nc-settings-modos |
| HS-CI-004 | DEBE | N1,N2,N3 | enforcement | automatica | `core.ci.agent-bare` | nc-agente-ci-sin-bare |
| HS-CMP-010 | DEBE | — | enforcement | automatica | `catalog.entry` | test_catalog.py |
| HS-CMP-011 | DEBE | — | enforcement | automatica | `catalog.ficha` | test_catalog.py |
| HS-CMP-012 | DEBE | — | enforcement | automatica | `catalog.skill` | test_catalog.py |
| HS-CMP-013 | DEBE | — | enforcement | automatica | `catalog.transition`<br>`catalog.version` | test_catalog.py |
| HS-CMP-009 | DEBERÍA | N0,N1,N2,N3 | guidance | automatica | `core.components.drift` | nc-componente-borrado<br>nc-componente-config-quitada<br>nc-componente-modificado<br>nc-lock-invalido |

## Autotest de fixtures

| Caso | Resultado | Detalle |
|---|---|---|
| c-n0-basico | ✅ | conforme |
| c-n0-reubicado-con-waiver | ✅ | conforme |
| nc-manifiesto-ausente | ✅ | ok |
| nc-manifiesto-esquema | ✅ | ok |
| nc-version-no-soportada | ✅ | ok |
| nc-nivel-no-definido | ✅ | ok |
| nc-waiver-no-exentable | ✅ | ok |
| nc-waiver-caducado | ✅ | ok |
| nc-waiver-demasiado-largo | ✅ | ok |
| nc-rol-no-reubicable | ✅ | ok |
| nc-rol-ruta-inexistente | ✅ | ok |
| nc-ci-ausente | ✅ | ok |
| nc-ci-sin-pull-request | ✅ | ok |
| nc-agents-ausente | ✅ | ok |
| nc-comandos-no-citados | ✅ | ok |
| nc-import-roto | ✅ | ok |
| nc-enlace-roto-y-ruta-personal | ✅ | ok |
| nc-sin-enlaces-nucleo | ✅ | ok |
| nc-presupuesto-superado | ✅ | ok |
| nc-claude-sin-import | ✅ | ok |
| nc-claude-import-en-codigo | ✅ | ok |
| nc-claude-duplica | ✅ | ok |
| nc-claude-ausente | ✅ | ok |
| nc-mapa-ausente | ✅ | ok |
| nc-decisiones-ausentes | ✅ | ok |
| nc-seguridad-ausente | ✅ | ok |
| nc-codeowners-ausente | ✅ | ok |
| nc-codeowners-anulado-por-ultimo-patron | ✅ | ok |
| nc-codeowners-sin-mcp | ✅ | ok |
| nc-gitignore-local | ✅ | ok |
| nc-comandos-no-declarados | ✅ | ok |
| nc-setup-falla | ✅ | ok |
| nc-setup-no-idempotente | ✅ | ok |
| c-n1-basico | ✅ | conforme |
| c-n0-basico-version-0-2 | ✅ | conforme |
| nc-n1-con-version-0-1 | ✅ | ok |
| nc-ruta-no-portable | ✅ | ok |
| nc-sin-idioma | ✅ | ok |
| nc-agents-sin-anclas | ✅ | ok |
| nc-agents-sin-flujo | ✅ | ok |
| nc-demasiadas-restricciones | ✅ | ok |
| nc-cadena-agents-32k | ✅ | ok |
| nc-segmento-sin-ambito | ✅ | ok |
| nc-segmento-duplica-raiz | ✅ | ok |
| nc-segmento-sin-claude | ✅ | ok |
| nc-claude-import-no-primero | ✅ | ok |
| nc-claude-dos-ubicaciones | ✅ | ok |
| nc-referencias-sin-procedencia | ✅ | ok |
| nc-arquitectura-sin-invariantes | ✅ | ok |
| nc-adr-fuera-del-indice | ✅ | ok |
| nc-adr-frontmatter | ✅ | ok |
| nc-seguridad-sin-controles | ✅ | ok |
| nc-sin-plantilla-pr | ✅ | ok |
| nc-sin-workflow-tareas | ✅ | ok |
| nc-sin-plans | ✅ | ok |
| nc-tarea-invalida | ✅ | ok |
| nc-tarea-mal-ubicada | ✅ | ok |
| nc-tarea-manual-sin-verificador | ✅ | ok |
| nc-indice-tareas-desactualizado | ✅ | ok |
| c-n1-componentes | ✅ | conforme |
| c-n1-basico-sigue-en-0-2 | ✅ | conforme |
| nc-skill-invalida | ✅ | ok |
| nc-skill-perfil | ✅ | ok |
| nc-agents-skills-versionado | ✅ | ok |
| nc-subagente-invalido | ✅ | ok |
| nc-subagente-sin-tools | ✅ | ok |
| nc-hook-script-ausente | ✅ | ok |
| nc-hook-prompt-como-control | ✅ | ok |
| nc-min-version-antigua | ✅ | ok |
| nc-settings-ausente | ✅ | ok |
| nc-settings-sin-deny-env | ✅ | ok |
| nc-settings-ruta-sensible-sin-ask | ✅ | ok |
| nc-settings-modos | ✅ | ok |
| nc-agente-ci-sin-bare | ✅ | ok |
| c-n1-distribucion | ✅ | conforme |
| c-componentes-con-crlf | ✅ | conforme |
| nc-componente-modificado | ✅ | ok |
| nc-componente-borrado | ✅ | ok |
| nc-componente-config-quitada | ✅ | ok |
| nc-lock-invalido | ✅ | ok |

## Incidencias

- HS-SEC-004: aviso — enforcement verificado solo manualmente (pendiente de control L4/L5).
