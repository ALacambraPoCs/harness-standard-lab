---
rol: security.policy
titulo: Política de seguridad del repositorio (SECURITY.md)
estado: propuesta
version: 0.1.0
consumidores: [personas, agentes, ci]
dependencias: [instructions.root, adapter.claude.settings, codeowners]
propietario: Responsable de seguridad asignado al repositorio (CODEOWNERS), junto con el tech lead
requisitos: [HS-SEC-001, HS-SEC-004, "pendiente:F2.5"]
reglas: [core.security.doc-exists]
ejemplo_canonico: template/core/docs/security/SECURITY.md
fuentes: [S-MCP, S-VILA#p29, S-CC-SET, S-OAI-HE, ADR-009, ADR-013]
evolucion: >-
  MAJOR si se añade un ancla obligatoria; MINOR si se añade una opcional; PATCH editorial.
  El modelo de amenazas completo se amplía en la Fase 5.
---

# Política de seguridad del repositorio

> Ruta (reubicable), obligatoriedad y nivel: `standard/roles.yaml#security.policy`.

## Propósito

Dejar escrito, para personas y agentes:

- qué es sensible en este repositorio;
- qué entradas no son de fiar;
- qué acciones necesitan una aprobación humana.

Además, para cada riesgo dice **qué control lo impone de verdad**. Este documento **guía**; no protege por sí solo (ADR-009).

> Rol distinto del `SECURITY.md` de la comunidad de GitHub (cómo reportar vulnerabilidades). Si el repositorio lo necesita, puede ser el mismo archivo con ambas secciones (reubicando `security.policy` a `SECURITY.md`) o dos archivos.

## Contenido requerido

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Secretos: dónde viven, cómo se inyectan, qué hacer si se filtra uno | `<!-- harness:secretos -->` | HS-SEC-004 (guidance); ancla pendiente:F2.5 | Ancla + revisión |
| Entradas no confiables de este repositorio: issues, comentarios, web, MCP, datos de clientes… | `<!-- harness:entradas-no-confiables -->` | pendiente:F2.5 | Ancla + revisión |
| Acciones que requieren aprobación humana y quién la da (despliegue, migraciones, dependencias nuevas, cambios en `.github/` o `.claude/`) | `<!-- harness:aprobaciones -->` | pendiente:F2.5 | Ancla + revisión |
| Tabla riesgo → control: qué capa L2–L5 lo impone (permiso, hook, check, ruleset) | `<!-- harness:controles -->` | pendiente:F2.5 | Ancla + revisión. Cada fila con control L4/L5 o justificada |

## Contenido recomendado y opcional

| Elemento | Ancla | Cuándo |
|---|---|---|
| Clasificación de datos que maneja el sistema (personales, financieros…) | `<!-- harness:datos -->` | Recomendado si maneja datos personales o regulados |
| Servidores MCP y herramientas externas permitidas, con propietario | `<!-- harness:herramientas -->` | Si se usan (desde la Fase 3, enlace al catálogo) |
| Cómo reportar una vulnerabilidad | — | Si el repositorio es público o lo usan terceros |

## Contenido excluido

| No incluir | Va en |
|---|---|
| Secretos, hosts internos con credenciales, rutas de bóvedas con tokens | Gestor de secretos |
| Reglas de permisos del agente en lenguaje natural como única protección | `.claude/settings.json` (L2) más CI y ruleset (L4/L5) |
| Detalle de vulnerabilidades abiertas sin corregir | El canal privado de seguridad (advisories) |
| Políticas corporativas generales copiadas | Enlace a la política corporativa |

## Formato y convenciones

- Markdown, breve. Recomendación: 120 líneas o menos. El detalle va enlazado.
- La tabla `controles` tiene las columnas **riesgo · control · capa · dónde se verifica**.
- Idioma libre (D-020).

## Ejemplo canónico

Ver `template/core/docs/security/SECURITY.md`. Fragmento de la tabla de controles:

```markdown
<!-- harness:controles -->
| Riesgo | Control | Capa | Verificación |
|---|---|---|---|
| Un PR modifica la configuración de agentes para relajarla | CODEOWNERS de `.claude/`, `AGENTS.md`… + revisión de code owner | L5 | Ruleset de `main` |
| Secreto versionado | Secret scanning y push protection | L5 | Ajustes del repositorio (manual, HS-SEC-004) |
| El agente lee `.env` | `permissions.deny: Read(./.env*)` | L2 | `.claude/settings.json` (Fase 3) |
| Instrucciones inyectadas en una issue | Una issue no es una tarea hasta que una persona la convierte en archivo de tarea | Proceso + L5 (revisión del PR) | Plantilla de PR (`tarea`) |
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe | L4 (`core.security.doc-exists`) | Vigente |
| Anclas obligatorias presentes | L4 | Pendiente F2.5 (propuesta: N1) |
| Cada riesgo alto tiene un control L4/L5 | Revisión humana; automatizable en parte en la Fase 5 | Manual |
| Secret scanning y push protection activos | L5 (ajuste de la plataforma) | Manual (HS-SEC-004) |

## Criterios de aceptación

1. Un agente que lee el documento sabe qué no debe tocar sin aprobación y por qué.
2. Cada riesgo listado indica qué lo impone de verdad. No vale "el agente lo sabe".
3. Revisado por el responsable de seguridad (CODEOWNERS).

## Ciclo de vida y evolución

- **Creación:** en la adopción (N0).
- **Actualización:** al añadir una integración, una herramienta MCP, un tipo de dato sensible o un entorno de despliegue.
- **Revisión:** semestral y tras cualquier incidente de seguridad.
- **Ampliación:** la Fase 5 añadirá un modelo de amenazas formal y controles automatizados.
