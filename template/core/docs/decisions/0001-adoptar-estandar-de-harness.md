---
id: ADR-0001
titulo: Adoptar el Estándar de Harness
estado: aceptada
fecha: {{DATE}}
decisores: ["{{OWNER}}"]
---

# ADR-0001 · Adoptar el Estándar de Harness

## Contexto
El equipo trabaja con agentes de programación y necesita normas comunes y verificables.

## Decisión
El repositorio adopta el Estándar de Harness 0.3.0, nivel {{LEVEL}}.

## Consecuencias
`harness check` es un check requerido en los PR; la configuración de agentes queda bajo CODEOWNERS.

## Alternativas consideradas
Seguir sin normas comunes: descartado por la variabilidad de resultados entre personas y agentes.
