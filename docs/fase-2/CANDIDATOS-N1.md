---
documento: F2-CANDIDATOS
titulo: Requisitos candidatos que surgen de las fichas (se formalizan en F2.5)
estado: lista viva
actualizado: 2026-10-21 (F2.2)
---

# Requisitos candidatos para la F2.5

Cada candidato tiene su origen en una ficha. En la F2.5 recibirá ID, regla y fixtures, y se someterá a aprobación. Nada de esta lista es normativo todavía.

| # | Candidato | Nivel normativo propuesto | Niveles | Verificación | Origen |
|---|---|---|---|---|---|
| C-01 | AGENTS.md raíz contiene las anclas `resumen`, `comandos`, `restricciones` y `mapa` | DEBE | N1+ | automática | instructions.root |
| C-02 | N.º de restricciones duras como máximo el presupuesto (15 por defecto, ajustable en el manifiesto) | DEBERÍA | N1+ | automática | instructions.root |
| C-03 | AGENTS.md raíz contiene el ancla `flujo` (dónde está la tarea, quién marca `done`) | DEBERÍA | N1+ | automática | instructions.root |
| C-04 | Bytes acumulados de la cadena raíz → segmento más profundo ≤ 32 KiB (límite de Codex) | DEBERÍA | N0+ | automática | instructions.root / segment |
| C-05 | `<segmento>/AGENTS.md` contiene `ambito` y al menos otra ancla con contenido | DEBE | N0+ | automática | instructions.segment |
| C-06 | `<segmento>/AGENTS.md` no duplica líneas sustantivas de la raíz | DEBERÍA | N0+ | automática | instructions.segment |
| C-07 | Con `claude-code`, cada `<segmento>/AGENTS.md` tiene `<segmento>/CLAUDE.md` con `@AGENTS.md` | DEBE | N0+ | automática | instructions.segment / adapter.claude (S-CC-MEM) |
| C-08 | `@AGENTS.md` es la primera línea no vacía de cada CLAUDE.md | DEBERÍA | N0+ | automática | adapter.claude |
| C-09 | No existe `.claude/CLAUDE.md` (una sola ubicación del adaptador) | DEBERÍA | N0+ | automática | adapter.claude |
| C-10 | Rutas versionadas portables: sin `:<>"\|?*\` y sin segmentos acabados en espacio o punto | DEBE | N0+ | automática | 03 §5, R-11 |

Nota sobre compatibilidad: añadir un DEBE a N0 es un cambio MAJOR (`GOVERNANCE.md` §3), admitido mientras el estándar sea 0.x. C-05, C-07 y C-10 no rompen ninguna instancia actual: ninguna tiene segmentos y todas las rutas son portables.
