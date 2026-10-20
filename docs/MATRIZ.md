# Matriz de trazabilidad

Generada por `harness matrix`. No editar a mano.

| Requisito | Nivel | Niveles | Naturaleza | Verificación | Reglas | Fixtures no conformes |
|---|---|---|---|---|---|---|
| HS-GOV-001 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.manifest.valid` | nc-comandos-no-declarados<br>nc-manifiesto-ausente<br>nc-manifiesto-esquema |
| HS-GOV-002 | DEBE | N0,N1,N2,N3 | enforcement | automatica | `core.manifest.standard-version` | nc-nivel-no-definido<br>nc-version-no-soportada |
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

## Incidencias

- HS-SEC-004: aviso — enforcement verificado solo manualmente (pendiente de control L4/L5).
