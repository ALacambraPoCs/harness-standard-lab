---
id: ADR-015
titulo: "Cada mecanismo tiene condición de retirada y se evalúa por ablación"
estado: propuesto
fecha: 2026-10-19
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-015 · Cada mecanismo tiene condición de retirada y se evalúa por ablación [Fase 6]

**Recomendación**
- Cada requisito y cada componente del catálogo declara: propósito, propietario, coste estimado (contexto, latencia, mantenimiento), métrica de eficacia y condición de retirada.
- Una revisión periódica desactiva componentes en un conjunto de tareas de referencia y compara resultados.

**Justificación**
- Es un principio del proyecto.
- P10.
- S-LHE L12 aporta un procedimiento, aunque sin datos.

**Riesgos**
- Las evaluaciones con modelos son ruidosas.
- Hace falta un protocolo con repeticiones y varianza, que no existe en el corpus.

**Validación**
- Protocolo de evaluación definido en la Fase 6. Un primer ciclo de ablación se ejecuta en el piloto.
