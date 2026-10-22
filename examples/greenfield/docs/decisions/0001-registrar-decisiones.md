---
id: ADR-0001
titulo: Registrar decisiones como ADR
estado: aceptada
fecha: 2026-10-20
decisores: ["@AlbertoLacambra"]
---

# ADR-0001 · Registrar decisiones como ADR

## Contexto
Las decisiones de arquitectura se perdían en conversaciones y sesiones de agentes.

## Decisión
Las decisiones de arquitectura se registran en este directorio, una por archivo `NNNN-<slug>.md`.

## Consecuencias
Cada cambio de patrón enlaza su ADR; un ADR aceptado no se reescribe, se reemplaza.

## Alternativas consideradas
Wiki externa: descartada porque no se versiona con el código ni la leen los agentes.
