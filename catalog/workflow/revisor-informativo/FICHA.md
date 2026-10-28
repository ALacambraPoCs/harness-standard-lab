---
componente: revisor-informativo
---

# Revisor informativo de PR con agente, en jaula de solo lectura (`workflow` · `revisor-informativo`)

## 1. Nombre y propósito
Workflow de GitHub Actions que pide a un agente una revisión **informativa** del PR y la publica como comentario. El job del modelo no puede escribir nada, y lo que publica pasa por un filtro. Ver `proposito` en `componente.yaml`.

## 2. Problema que resuelve
Un agente que revisa PR lee contenido no confiable (vector V3 del modelo de amenazas). Si tiene un token con escritura o secretos, una inyección en el diff o en un comentario se convierte en un push, una aprobación o una filtración. Las instrucciones al modelo no lo impiden; los permisos sí.

## 3. Objetivo y beneficios esperados
- Dar a la persona revisora una segunda lectura barata del PR sin darle al agente ninguna autoridad.
- **Demostrar la contención sin modelo** (D-055): el simulador hostil prueba que un agente totalmente comprometido no consigue escribir, aprobar, fusionar, aprobar la puerta ni filtrar su credencial.

## 4. Principios y conceptos fundamentales
- La revisión de un agente es informativa (ADR-010 rev. 2).
- La configuración de agentes es código sensible y no la decide el PR (ADR-013, R-14): todo lo que gobierna al agente sale de la **rama base**.
- Separación de jobs: el job con la credencial del modelo lee; el job que escribe no tiene la credencial (HS-CI-007, `ci.model-readonly`).
- La salida del modelo también es no confiable: se neutraliza antes de publicarla.

## 5. Cuándo utilizarlo y cuándo no
- **Usar** en N1+ cuando haya una credencial corporativa de modelo (federación OIDC, API key de la organización o Bedrock/Vertex) y el equipo quiera una segunda lectura. Antes de tenerla, en `MODO=simulador`, como prueba de contención.
- **No usar:**
  - como check requerido ni como sustituto de la revisión humana;
  - en repos donde los PR llegan sobre todo de forks (no reciben secretos y el job se salta);
  - con un token personal de suscripción (`--bare` no lo lee y los términos lo limitan, F5-01, C11).

## 6. Arquitectura y funcionamiento
```mermaid
flowchart LR
  PR[pull_request] --> R["revisar · contents: read, pull-requests: read<br/>base/ = config de confianza · pr/ = contenido no confiable<br/>claude -p --bare (o simulador)"]
  R -- "informe (output, texto)" --> P["publicar · pull-requests: write · sin credencial del modelo<br/>publicar.py neutraliza y se autocomprueba"]
  P --> C[Comentario informativo]
```
El agente se ejecuta con `--bare --setting-sources user --settings base/.harness/revisor/settings.json --tools "Read,Grep,Glob" --permission-mode dontAsk --max-turns 15 --max-budget-usd 1`, dentro de `pr/` y con el diff en `HARNESS_DIFF.txt`.

## 7. Implementación paso a paso
1. `harness components add revisor-informativo` (copia el workflow y `.harness/revisor/`).
2. Subirlo en un PR. Ese primer PR **no** ejecuta la revisión: la configuración se lee de la rama base, donde aún no existe. Es intencionado.
3. Para el modelo real: crear el secreto `ANTHROPIC_API_KEY` (o adaptar a OIDC) y cambiar `MODO` a `modelo` en otro PR, que será de riesgo `alto` porque toca un workflow.

## 8. Ejemplo concreto
Con `MODO=simulador`, el resumen del job `revisar` muestra:
```
A1: contenido · códigos 128 y 128
A2: contenido · HTTP 403, 403, 403
A3: contenido · HTTP 403, 403
A4: contenido · HTTP 403
A6: pendiente · lo comprueba el job de publicación
Ataques A1–A4 contenidos; A5–A7 se comprueban al publicar.
```
El comentario del PR muestra `[credencial enmascarada]`, las menciones como código (`` `@persona` ``), `/approve` sin efecto y el HTML escapado. Los códigos concretos son los esperados según la documentación; se confirman en F5.7.

## 9. Integración con el resto del harness
- Cumple HS-CI-004 (`--bare --setting-sources user`) y HS-CI-007/008 (lo comprueban `core.ci.agent-bare` y `ci.*`).
- Tocar el workflow o `.harness/revisor/` es riesgo `alto` (D-058) y pasa por la puerta (ADR-010 rev. 2) y por CODEOWNERS.
- No interviene en la autoridad: los checks requeridos y `harness platform check` no dependen de él.

## 10. Responsabilidades
| Quién | Responsabilidad |
|---|---|
| Persona revisora | Leer el comentario como una opinión más; decidir con los checks y su criterio |
| Plataforma o seguridad | Proveer la credencial corporativa y revisar los cambios del workflow |
| Agente (en CI) | Leer y opinar; no tiene medios para nada más |
| CI | Ejecutar la contención (permisos, jobs separados, neutralización) |

## 11. Seguridad, permisos, límites y modos de fallo
- **Permisos:** job `revisar` con `contents: read` y `pull-requests: read`; job `publicar` con `pull-requests: write` y sin la credencial del modelo.
- **Herramientas del agente:** `Read, Grep, Glob`; deny de `Bash`, `Edit`, `Write` y web en `settings.json`. Red: Anthropic, GitHub y npm (instalación).
- **Neutralización** (`publicar.py`): enmascara credenciales con formato conocido (`sk-ant-…`, `ghp_…`, `github_pat_…`), escapa HTML, convierte menciones y órdenes de bot en código, trunca a 20 000 caracteres, y **falla** si tras neutralizar queda algo de eso.
- **Límites conocidos:**
  - Una credencial con formato desconocido no se enmascara. Que GitHub redacte secretos en los outputs de un job **no está verificado** (F5.4-B).
  - El agente podría describir datos sensibles del repositorio en su informe. Son datos que ya ve quien lee el PR, no nuevos.
- **Modos de fallo:** sin credencial en `MODO=modelo`, el job falla y se publica una nota del fallo. Un ataque con éxito en el simulador hace fallar el job (la prueba detecta la regresión).

## 12. Estrategia de pruebas y verificación
- **Unitarias:**
  - neutralización con cada tipo de carga;
  - autocomprobación de `publicar.py`;
  - criterio de éxito del simulador (solo 2xx);
  - el workflow pasa `core.ci.agent-bare` y `ci.*`;
  - la configuración y los scripts se leen de `base/`.
- **Integración (F5.7):**
  - un PR de prueba con el simulador debe dar 7/7 ataques contenidos;
  - un PR que debilita un permiso debe ser detectado por el simulador y por `ci.model-readonly`.

## 13. Métricas de eficacia, calidad, coste y latencia
Ver `metricas` y `coste`. Umbral de retirada: utilidad o coste en el piloto.

## 14. Alternativas y compromisos
| Alternativa | Por qué no (por ahora) |
|---|---|
| `claude-code-action@v1` | Restaura la configuración desde la base, pero no está verificado que use `--bare` y sus ejemplos piden escritura para la App. Alternativa del adaptador |
| Un solo job que revisa y comenta | Junta la credencial del modelo con la escritura (`ci.model-readonly`) |
| Agente con Bash para ejecutar pruebas | Más superficie (V5); la CI ya ejecuta las pruebas |

## 15. Dependencias, madurez y portabilidad
- `experimental`.
- GitHub Actions y Claude Code ≥ 2.1.277, instalado con npm a una versión fijada.
- Los scripts son Python de la biblioteca estándar.
- El patrón (dos jobs, base de confianza, neutralización) es portable a otros agentes cambiando el paso del modelo.

## 16. Criterios de aceptación para considerarlo implementado
1. Pruebas unitarias en verde y `harness catalog validate` sin errores.
2. F5.7: 7/7 ataques contenidos en el ejemplo, con evidencia en el resumen del job y en el comentario.
3. F5.7: la variante con permiso debilitado falla tanto en el simulador como en `ci.model-readonly`.

## 17. Referencias y decisiones relacionadas
- ADR-010 rev. 2, ADR-013, D-055, D-065, D-066.
- `docs/fase-5/02-modelo-amenazas.md` (V3, V11).
- code.claude.com/docs (headless, cli-reference, setup: `npm install -g @anthropic-ai/claude-code`).
- docs.github.com (secure-use, events-that-trigger-workflows).
