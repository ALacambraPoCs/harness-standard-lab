---
rol: instructions.segment
titulo: AGENTS.md de segmento
estado: propuesta
version: 0.1.0
consumidores: [agentes, personas, cli]
dependencias: [instructions.root, adapter.claude.instructions, architecture.map, segments.map]
propietario: Propietario del segmento (según CODEOWNERS del subárbol; desde N2, según segments.yaml)
requisitos: [HS-INS-004, HS-INS-005, HS-CTX-001, "pendiente:F2.5"]
reglas: [core.instructions.references-resolve, core.instructions.size-budget]
ejemplo_canonico: examples/fragmentos/segmento-AGENTS.md
fuentes: [S-AGENTSMD, S-CC-MEM, S-OAI-HE#p5, ADR-003, ADR-014]
evolucion: >-
  MAJOR si cambia la regla de precedencia o se añade un ancla obligatoria; MINOR si se añade un
  ancla opcional; PATCH si es editorial.
---

# AGENTS.md de segmento

> Ruta (`<segmento>/AGENTS.md`), obligatoriedad (condicional), nivel y capa: `standard/roles.yaml#instructions.segment`.

## Propósito

Dar a los agentes las reglas que **solo aplican a una parte del repositorio**, sin cargarlas en el contexto de quien trabaja en otra parte. Es la segunda capa de la divulgación progresiva (PR-2).

**Cómo lo cargan las herramientas** (verificado en S-CC-MEM el 2026-10-21):
- **S-AGENTSMD** y **Codex**: admiten AGENTS.md anidados; Codex concatena de la raíz al directorio actual (límite 32 KiB, ver ficha raíz); en conflicto gana el más cercano.
- **Claude Code — atención:** con el ajuste por defecto (`claude-md-or-agents-md`), Claude **solo** lee AGENTS.md (también los de subdirectorios) si **no** hay ningún `CLAUDE.md`/`CLAUDE.local.md` en el directorio de trabajo o por encima. Como el estándar exige un `CLAUDE.md` raíz (ADR-003), **Claude no cargará `<segmento>/AGENTS.md` por sí solo**. Por eso, con el adaptador `claude-code`, **cada `<segmento>/AGENTS.md` DEBE ir acompañado de `<segmento>/CLAUDE.md` con `@AGENTS.md`** (pendiente:F2.5): los `CLAUDE.md` de subdirectorios sí se cargan bajo demanda al leer o editar un archivo de ese subdirectorio, y el import resuelve relativo al archivo.

## Contenido requerido

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| Ámbito: qué cubre el segmento (ruta, propósito en una frase) y su propietario | `<!-- harness:ambito -->` | pendiente:F2.5 | Automática (ancla) |
| Al menos una regla, comando o límite **propio** del segmento | Cualquier ancla de las opcionales | pendiente:F2.5 | Automática (no vacío) + revisión |

## Contenido recomendado y opcional

| Elemento | Ancla | Cuándo |
|---|---|---|
| Comandos del segmento, si difieren de los raíz (por ejemplo, tests de un paquete) | `<!-- harness:comandos -->` | Si existen. En N2 DEBEN coincidir con `segments.yaml` |
| Restricciones propias del segmento | `<!-- harness:restricciones -->` | Si existen |
| Límites: de qué puede y de qué no puede depender este segmento | `<!-- harness:limites -->` | Recomendado cuando hay dependencias prohibidas |
| Enlaces a documentación del segmento | `<!-- harness:mapa -->` | Opcional |

## Contenido excluido

| No incluir | Va en |
|---|---|
| Copia de reglas de `AGENTS.md` raíz | Nada: la herramienta ya carga la raíz (duplicar crea contradicciones) |
| Reglas que contradicen la raíz sin justificarlo | Si de verdad hay una excepción local, se indica de forma explícita ("En este segmento, a diferencia de la raíz, …") y con un ADR |
| Estado de tareas | `plans.active` (HS-INS-004) |
| Contenido exclusivo de Claude Code | La sección `harness:claude` de `<segmento>/CLAUDE.md` (ADR-003) |
| Documentación extensa del módulo | Un documento del segmento enlazado desde `harness:mapa` |

## Formato y convenciones

- Markdown, nombre exacto `AGENTS.md`, en la **raíz del segmento**. No en cualquier subcarpeta.
- **Solo se crea si tiene contenido propio.** No se admiten archivos vacíos ni de cortesía.
- **Presupuesto**: el mismo límite por archivo que la raíz (HS-CTX-001). Recomendación interna: **50 líneas o menos**.
- Cuenta en el presupuesto acumulado de 32 KiB de la cadena raíz → segmento (ver la ficha raíz).
- **Con adaptador `claude-code`**: se crea siempre `<segmento>/CLAUDE.md` cuya primera línea es `@AGENTS.md` (mismas reglas que el `CLAUDE.md` raíz); sin él, Claude Code no carga las instrucciones del segmento.

## Ejemplo canónico

Ver `examples/fragmentos/segmento-AGENTS.md`:

```markdown
<!-- harness:ambito -->
# billing/ · Facturación
Cálculo de facturas y notas de crédito. Propietario: @org/billing.

<!-- harness:comandos -->
| Rol | Comando |
|---|---|
| test | `make test PKG=billing` |

<!-- harness:limites -->
- Puede depender de `shared/` y `ledger/api`. No importa nada de `payments/` (usa eventos).

<!-- harness:restricciones -->
- Los importes son `Decimal`; nunca `float` (lo comprueba `make check`).
```

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Enlaces resolubles y presupuesto de líneas | L4 (reglas vigentes; ya recorren todos los AGENTS.md) | Vigente |
| Ancla `ambito` presente y archivo no vacío | L4 | Pendiente F2.5 |
| Sin duplicación de líneas sustantivas con la raíz | L4 | Pendiente F2.5 (DEBERÍA) |
| Presupuesto acumulado de la cadena de 32 KiB o menos | L4 | Pendiente F2.5 (DEBERÍA) |
| Con `claude-code`: existe `<segmento>/CLAUDE.md` que importa `@AGENTS.md` | L4 | Pendiente F2.5 (DEBE) |
| Coherencia con `segments.yaml` (ruta y comandos) | L4 | Fase 4 (N2) |
| Revisión del propietario del segmento | L5 (CODEOWNERS) | Vigente si CODEOWNERS asigna el subárbol |

## Criterios de aceptación

1. Existe solo en segmentos con reglas propias y contiene `harness:ambito`.
2. No repite contenido de la raíz y no la contradice sin una excepción explícita.
3. La cadena raíz → segmento respeta el presupuesto acumulado.
4. Con `claude-code`, una sesión que edita un archivo del segmento muestra cargado `<segmento>/CLAUDE.md` (y con él el AGENTS.md del segmento).

## Ciclo de vida y evolución

- **Creación:** cuando aparece la primera regla que solo afecta a ese segmento. En N2, al declarar el segmento en `segments.yaml`.
- **Actualización:** en el mismo PR que cambia los comandos o los límites del segmento.
- **Retirada:** se elimina si se queda sin reglas propias o si se fusiona el segmento.
