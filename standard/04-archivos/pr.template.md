---
rol: pr.template
titulo: Plantilla de pull request
estado: propuesta
version: 0.1.0
consumidores: [personas, agentes, ci]
dependencias: [plans.active, security.policy, codeowners]
propietario: Equipo de plataforma/harness
requisitos: [HS-CI-001, HS-CI-002, HS-SEC-006]
reglas: []
ejemplo_canonico: template/adapters/github/.github/pull_request_template.md
fuentes: [S-GH-PRTEMPLATE, ADR-005, ADR-010, D-023, X-01]
evolucion: >-
  MAJOR si se añade una sección obligatoria verificada por CI; MINOR si se añade una opcional; PATCH editorial.
---

# Plantilla de pull request

> Ruta y alternativas reconocidas por GitHub: `standard/roles.yaml#pr.template`.

## Propósito

Conseguir que cada PR declare, de forma que la CI pueda leerlo:

- **qué tarea cumple** (o que es trivial, según D-023);
- **qué riesgo tiene**;
- **qué evidencia aporta**.

Con eso la revisión se apoya en el riesgo y en la evidencia, y no en la impresión que deja el diff (objetivo 5 del proyecto).

## Contenido requerido

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Tarea: `T-NNNN` (archivo en `plans.active`) **o** la palabra `trivial` con su motivo (D-023) | `<!-- harness:tarea -->` | HS-CI-002 | Automática en la CI de tareas (F2.4) |
| Clase de riesgo: `bajo`, `medio` o `alto`, con una línea de justificación | `<!-- harness:riesgo -->` | HS-CI-002 | Automática (valor válido) |
| Evidencia: comandos ejecutados y resultado, o enlace al run de CI | `<!-- harness:evidencia -->` | HS-CI-001 (ancla) | Revisión. La evidencia que cuenta para `done` la escribe la CI (F2.4) |
| ¿Toca configuración de agentes, CI o seguridad? (sí/no) | `<!-- harness:sensible -->` | HS-SEC-006 | Automática: se contrasta con las rutas del diff |
| Línea `Closes #<n>` si la tarea tiene `issue:` (X-01) | dentro de `harness:tarea` | pendiente:F2.4 | Automática (X-01) |

## Contenido recomendado y opcional

- Quién o qué produjo el cambio: persona, o agente y versión, a nombre de una persona responsable.
- Puntos que conviene revisar con más atención.
- Capturas o vídeos para cambios de interfaz.

## Contenido excluido

| No incluir | Va en |
|---|---|
| La discusión completa del diseño | ADR o archivo de tarea |
| Instrucciones para agentes revisores | `AGENTS.md` y adaptador. El cuerpo de un PR es entrada no confiable (PR-7, ADR-013) |
| Secretos o datos de clientes en capturas | En ningún sitio |

## Formato y convenciones

- Archivo único `.github/pull_request_template.md`. GitHub también admite la raíz, `docs/` y `PULL_REQUEST_TEMPLATE/` para varias plantillas (S-GH-PRTEMPLATE). El estándar usa una sola.
- GitHub solo la ofrece si está en la **rama por defecto** (S-GH-PRTEMPLATE).
- Las anclas son comentarios HTML: no se ven en el PR renderizado, pero la CI las lee en el cuerpo.
- **La plantilla no es un control.** El cuerpo del PR lo edita el autor. Las comprobaciones que importan (tarea existente, rutas sensibles reales, evidencia de CI) se calculan a partir del repositorio y del diff, y lo declarado solo se contrasta con eso (ADR-009).

## Ejemplo canónico

Ver `template/adapters/github/.github/pull_request_template.md`.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe en la rama por defecto | L4 | HS-CI-001 (N1), `core.pr.template` |
| `tarea` apunta a un archivo existente, o es `trivial` y el diff solo toca rutas permitidas (D-023) | L4 (workflow de tareas) | F2.4 |
| `riesgo` válido; `sensible` coherente con el diff | L4 | F2.4/F2.5 |
| La aprobación humana depende del riesgo | L5 | Fase 5 (ADR-010) |

## Criterios de aceptación

1. Todos los PR del repositorio en N1 llevan `tarea`, `riesgo`, `evidencia` y `sensible`.
2. La CI rechaza un PR con `tarea: trivial` que toca código de producción.

## Ciclo de vida y evolución

- **Creación:** al pasar a N1.
- **Actualización:** cuando cambien las clases de riesgo (Fase 5) o termine X-01.
- **Retirada:** no aplica.
