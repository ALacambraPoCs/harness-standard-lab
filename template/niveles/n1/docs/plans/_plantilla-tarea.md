---
# Copia como docs/plans/active/T-NNNN-<slug>.md. Esquema: schemas/task.schema.json (ADR-005, ADR-016).
id: T-NNNN
title: <Resultado esperado, en una frase>
owner: "@persona-responsable"        # un agente siempre trabaja a nombre de una persona
status: proposed                     # proposed → ready → in_progress → in_review → done (lo verifica la CI)
risk: bajo                           # bajo | medio | alto
created: AAAA-MM-DD
# segments: [<segmento>]
# depends_on: [T-NNNN]
# issue: 123                         # X-01: issue espejo (opcional)
# lease: { holder: "agent:claude-code@persona", expires: "AAAA-MM-DDTHH:MM:SSZ" }
acceptance:
  - id: AC1
    description: <Comportamiento observable que debe cumplirse>
    check: "<comando que termina en 0 si se cumple>"
  # - id: AC2
  #   description: <Comprobación que solo puede hacer una persona>
  #   check: manual
  #   verified_by: "@persona"          # debe aprobar el PR
# done_pr: <número del PR que la completa>  # obligatorio al pasar a done
---

# T-NNNN · <Título>

<!-- Autocontenido: alguien sin contexto previo debe poder continuar solo con este archivo y el repositorio. -->

<!-- harness:objetivo -->
## Objetivo
Qué cambia para quién y cómo se nota. Sin jerga sin definir.

<!-- harness:alcance -->
## Alcance
- Dentro: …
- Fuera de alcance: …
- No tocar: … (rutas o contratos que el cambio no debe modificar)

<!-- harness:plan -->
## Plan
Pasos concretos, en orden. Comandos exactos cuando proceda. La tarea se cierra en el PR que la completa: si después hace falta validar algo más, crea otra tarea.

<!-- harness:progreso -->
## Progreso
- [ ] AAAA-MM-DD HH:MM — <paso> (quien: persona | agente@persona)

<!-- harness:decisiones -->
## Decisiones
- AAAA-MM-DD — <decisión> — <motivo> — <autor>

<!-- harness:hallazgos -->
## Hallazgos
Comportamientos inesperados, con evidencia breve (salida de test, enlace).

<!-- harness:resultado -->
## Resultado
(Obligatorio al pasar a done.) Qué se logró frente al objetivo, qué queda pendiente.
