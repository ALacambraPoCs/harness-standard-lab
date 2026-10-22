---
documento: F2-PLAN
titulo: Plan de la Fase 2 — Estructura canónica, fichas de archivo y nivel N1
estado: cerrado (D-031)
fecha: 2026-10-21
depende_de: [D-015, D-020, D-021, D-022, D-023, ADR-003, ADR-004, ADR-005, ADR-006]
---

# Fase 2 · Plan

## Objetivo
Definir la estructura canónica de una instancia para N0 y N1, la ficha normativa de cada archivo del núcleo y los requisitos N1, cada uno con su regla y sus fixtures.

La Fase 2 termina con una instancia que **puede demostrar N1 en GitHub**: una tarea con esquema, un PR que la referencia y la CI marcando `done` con evidencia.

## Incrementos

Cada incremento se cierra con la aprobación del usuario, igual que en la Fase 1.

| # | Entregable | Contenido | Depende de |
|---|---|---|---|
| **F2.1** | `standard/03-estructura-canonica.md` y la plantilla de ficha | Árbol de N0 y N1 con la obligatoriedad de cada elemento. Cada ruta se mapea a un rol (`roles.yaml`). Se añaden los roles nuevos de N1. | — |
| **F2.2** | Fichas de archivo de instrucciones | `AGENTS.md` raíz, `AGENTS.md` local de segmento y `CLAUDE.md`: secciones, contenido excluido, presupuesto y anclas. | F2.1 |
| **F2.3** | Fichas de documentos núcleo | Mapa de arquitectura, ADR del proyecto, política de seguridad (contenido mínimo verificable), contrato de comandos, CODEOWNERS y plantilla de PR. | F2.1 |
| **F2.4** | **Esquema de tarea y ciclo de vida** | `schemas/task.schema.json`: estados, transiciones, aceptación ejecutable, evidencia y `lease`. Campo `issue:` de X-01. Regla de tarea trivial (D-023). Workflow de CI que marca `done` y de sincronización con la issue (X-01). | F2.1 |
| **F2.5** | Requisitos N1, reglas y fixtures | Nuevos `HS-STA-*`, `HS-VER-*` y `HS-SEC-*` (incluido el de rutas portables, R-11). Se activa `niveles_definidos: [N0, N1]`. | F2.2–F2.4 |
| **F2.6** | Prueba en el laboratorio | `harness-example-greenfield` sube a N1 con una tarea real, del archivo al PR, la CI, `done` y la issue cerrada. Arranca la medición de X-01. | F2.5 |

## Criterios de aceptación de la fase

1. Cada archivo obligatorio u opcional de N0 y N1 tiene ficha completa, sin campos vacíos sin justificar.
2. `task.schema.json` valida los fixtures conformes y rechaza los no conformes, entre ellos las transiciones ilegales y un `done` sin evidencia.
3. `harness matrix --strict` pasa con N0 y N1.
4. La plantilla instanciada a N1 supera su propio validador.
5. El laboratorio tiene evidencia en GitHub de una tarea que pasa a `done` solo por la CI (E-0xx).

## Fuentes que se leerán en la fase

- Cookbook de planes de ejecución de OpenAI (F2.4).
- Estudio de ETH Zurich sobre AGENTS.md (F2.2, presupuesto de instrucciones).
- matklad, *ARCHITECTURE.md* (F2.3).
- Documentación de GitHub sobre las palabras clave de cierre de issues y los permisos de `GITHUB_TOKEN` para issues (F2.4).
