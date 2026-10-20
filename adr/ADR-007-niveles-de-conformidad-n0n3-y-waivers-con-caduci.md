---
id: ADR-007
titulo: "Niveles de conformidad N0–N3 y waivers con caducidad"
estado: aprobado
fecha: 2026-10-19
aprobado_por: Usuario (Alberto Lacambra)
origen: docs/fase-0/03-decisiones-propuestas.md
---

## ADR-007 · Niveles de conformidad N0–N3 y waivers con caducidad [APROBADO 2026-10-19]

**Recomendación**
- Los cuatro niveles acumulativos de F0-02 §4.2.
- Un brownfield entra por N0.
- Ningún repositorio usa agentes en paralelo (N2) sin cumplir N1.

**Justificación**
- Permite adoptar el estándar de forma progresiva.
- Evita imponer el coste completo a repositorios pequeños.
- Liga la autonomía a las garantías que se han demostrado.

**Alternativas**
- Binario (cumple o no cumple): bloquea la adopción.
- Puntuación 0–100, como `validate-harness`: es manipulable y no indica qué garantías existen.

**Riesgos**
- Que N0 se perciba como "suficiente".
- Mitigación: el plan de adopción fija un nivel objetivo por repositorio y plazos.

**Evidencia**
- Decisión propia.
- La escalera de madurez de S-LHE L13 sirve de inspiración, pero sin datos que la respalden.

**Validación**
- Piloto con un greenfield (objetivo N2) y un brownfield (objetivo N1) en la Fase 8.
