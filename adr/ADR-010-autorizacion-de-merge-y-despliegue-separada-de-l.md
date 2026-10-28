---
id: ADR-010
titulo: "Autorización de merge y despliegue separada de la revisión por agentes"
estado: aprobado
fecha: 2026-10-26
revision: 2
origen: docs/fase-0/03-decisiones-propuestas.md; rev. 2 en docs/fase-5/03-riesgo-y-escalado.md
aprobado_por: Usuario (Alberto Lacambra), D-060
---

## ADR-010 · Autorización de merge y despliegue separada de la revisión por agentes [APROBADO 2026-10-26, rev. 2]

**Problema.** Hay que decidir quién o qué autoriza fusionar y desplegar cuando parte del trabajo lo hacen agentes. La rev. 1 suponía que siempre hay otra persona para aprobar. No es así en el laboratorio (D-056), y GitHub no permite aprobar el propio PR (`fase-5/01-verificacion-fuentes.md`, G3).

**Decisión**
1. **La revisión de un agente es informativa**: comentarios o un check no requerido. Nunca aprueba ni fusiona.
2. **La autorización está en la plataforma.** Un ruleset en la rama por defecto exige:
   - PR obligatorio;
   - checks requeridos (conformidad, `tasks / harness tasks` con la clase de riesgo calculada, `tasks / puerta riesgo alto`);
   - sin force push ni borrado;
   - aprobaciones según el nivel y la clase de riesgo (matriz en `fase-5/03-riesgo-y-escalado.md` §2.1).
3. **Puerta explícita para riesgo alto.** Si la clase calculada (D-058) es `alto`, el job `puerta-riesgo-alto` se ejecuta en el environment `aprobacion-riesgo-alto` con revisores obligatorios. GitHub lo pausa hasta que un revisor lo aprueba y registra quién y cuándo. En otras clases el job se salta y cuenta como éxito.
   - **Laboratorio:** el revisor es el mantenedor, con «Prevent self-review» desactivado. Es una confirmación deliberada y auditada, no una revisión independiente.
   - **Equipos:** propietarios de plataforma o seguridad, con «Prevent self-review» activado.
4. **Fusión automática sin persona:** solo en N3, con clase `bajo` calculada y auditoría. Requiere un ADR propio.
5. **Despliegue:** environment protegido, limitado a la rama por defecto y sin bypass de administradores (F5.6).

**Alternativas descartadas**
- Aprobaciones fijas (≥ 1) en todos los PR: imposibles con un mantenedor y generan fatiga de aprobación (S-VILA p.3, p.29).
- Ruleset condicionado por etiquetas: no existe esa regla y la etiqueta la puede poner el agente.
- GitHub App que aprueba los PR de bajo riesgo: sería «agente aprueba agente»; solo en N3 con un ADR propio.
- Merge queue: opcional en N2+ con concurrencia (F4).

**Riesgos y supuestos**
- **Riesgo residual:** con el token completo de la persona, un agente podría aprobar el environment por API (`gh api`, en `ask`) si la persona acepta el diálogo. Se cierra con el token de mínimo privilegio (F5.5).
- **Riesgo residual:** si el environment no existe, GitHub lo crea **sin protección** al primer uso. Lo comprueba `harness platform check` (F5.3).
- **Supuestos por validar en F5.7:** un job de `pull_request` (también desde un workflow reutilizable) queda en espera de aprobación; con «Prevent self-review» desactivado, quien abrió el PR puede aprobar.

**Evidencia.** Verificado a mano: G3, G5 y que «A job that is skipped will report its status as "Success". It will not prevent a pull request from merging, even if it is a required check.» Verificado por subagente: G2, G4 y G7.

**Validación**
- `harness platform check` comprueba el ruleset y el environment (F5.3).
- F5.7: un PR que toca un workflow queda en espera hasta la aprobación; un PR de código no.

**Condición de retirada.** Si la plataforma ofrece aprobaciones condicionadas por riesgo comprobables, o si el equipo adopta otro sistema de autorización con auditoría equivalente.
