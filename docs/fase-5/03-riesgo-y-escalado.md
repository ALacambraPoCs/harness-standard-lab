---
documento: F5-03
titulo: F5.2 · Clases de riesgo, matriz de escalado y autorización (ADR-010)
estado: aprobado (D-058, D-059, D-060)
fecha: 2026-10-26
depende_de: [D-023, D-053, D-056, ADR-009, ADR-010, ADR-013, ADR-016, F5-01, F5-02]
---

# F5.2 · Riesgo, escalado y autorización

## 1. Clase de riesgo determinista (decisión R1)

**Hoy** la clase la declara una persona o un agente en el PR y en la tarea. Solo una regla la contrasta con el diff (rutas sensibles ⇒ no `bajo`). Si un agente se equivoca o se le induce a declarar `bajo`, nada lo impide (V7, V9).

**Propuesta:** la CLI **calcula** una clase mínima a partir del diff y de las tareas. La clase efectiva es la mayor entre la calculada, la declarada en el PR y la de las tareas que el PR cierra. Declarar puede **subir** la clase, nunca bajarla.

| Señal (determinista) | Clase mínima | Por qué |
|---|---|---|
| Solo rutas de `patrones_triviales` (docs, lockfiles) | bajo | D-023 |
| Cambios de código o de pruebas | bajo | Cubiertos por `check`, `test` y criterios (ADR-016) |
| Se borran o se renombran pruebas, o bajan las líneas de `tests/` más de un umbral | medio | Señal de debilitar la verificación (V8) |
| Cambian los `acceptance` de una tarea que el PR cierra (K-14) | medio | V8 |
| Rutas sensibles de agentes (`AGENTS.md`, `CLAUDE.md`, `.claude/**`, `.agents/**`, `.mcp.json`) | medio | ADR-013 (V1) |
| Rutas críticas de la autoridad: `.github/workflows/**`, `.github/CODEOWNERS`, `.harness/**` (manifiesto, lock), `rutas_criticas` declaradas por la instancia (p. ej. despliegue, infraestructura, migraciones) | **alto** | Cambian L4 o L5, o producción (V2, V10) |
| Una tarea cerrada por el PR declara `risk: alto` | alto | Declaración de la persona |
| Más de un segmento (cuando exista F4) | medio | ADR-014 |

- `rutas_criticas` es una lista nueva en `roles.yaml` (valores por defecto) que el manifiesto puede **ampliar**, pero no reducir.
- La salida es `harness pr risk --base <ref>`: la clase y las señales que la justifican, en texto y JSON. La regla `pr.risk` pasa a exigir que la clase declarada sea **≥ la calculada** (generaliza `pr.risk-sensitive`).
- Requisito candidato: **HS-CI-005** (DEBE, N1, desde 0.6.0).

## 2. Matriz de escalado (decisión R2)

### 2.1 Qué exige cada clase para fusionar

| | Bajo | Medio | Alto |
|---|---|---|---|
| Checks requeridos (conformidad, tareas, `check`/`test`) | ✅ | ✅ | ✅ |
| Check `harness / riesgo` (clase calculada ≤ declarada) | ✅ | ✅ | ✅ |
| Revisión humana del diff | La persona que fusiona | La persona que fusiona, que **lee** el diff de las rutas sensibles | **Puerta explícita**: confirmación registrada (§3) |
| Equipo (N2+) | 0 aprobaciones | 1 aprobación | 1 aprobación de Code Owner + aprobación del último push por otra persona + puerta explícita |
| Laboratorio (D-056, un solo mantenedor) | Merge | Merge | Merge + puerta explícita |
| Fusión automática | Solo N3 (ADR-010) | No | No |

### 2.2 Cuándo se escala a una persona (durante el trabajo del agente)

| Disparador | Detectado por | Acción del agente | Quién decide |
|---|---|---|---|
| El hook agota los reintentos (`verificar-al-terminar`) | L3 | Parar y explicar lo que falla | Responsable de la tarea |
| El verificador dice NO LISTO dos veces seguidas | Subagente (L1) | Parar; no cerrar la tarea | Responsable de la tarea |
| Un criterio de aceptación parece incorrecto | Agente (L1) | No cambiarlo; pedir decisión (skill) | Responsable de la tarea |
| Una regla `deny` bloquea algo necesario | L2 | No buscar rodeos (`gh api`, `sh -c`); explicar | Responsable y, si hace falta, propietario de plataforma |
| La clase calculada es **alto** | L4 | Seguir, pero el PR necesita la puerta explícita | Propietario de la ruta crítica |
| El mismo check falla en CI dos veces tras corregir | L4 | Parar y resumir | Responsable de la tarea |
| Secreto detectado (secret scanning, push protection) | L5 | Parar; no reintentar el push | Seguridad |
| El despliegue falla o la verificación posterior falla | L4/L5 | Rollback (F5.6) y avisar | Propietario del servicio |

Estas reglas se llevan a `AGENTS.md` (sección `harness:flujo`, breve) y a las skills. Las que dependen de L4 o L5 no requieren que el agente las siga: ya las impone la plataforma.

## 3. Autorización (decisión R3 · ADR-010)

**Recomendación (revisión de ADR-010):**
1. **La revisión de un agente es informativa**: comentarios o un check no requerido. Nunca aprueba ni fusiona.
2. **La autorización está en la plataforma**: ruleset de la rama por defecto con PR obligatorio, checks requeridos (incluido `harness / riesgo`), sin force push ni borrado, y aprobaciones según el nivel (§2.1).
3. **Puerta explícita para riesgo alto**: el job `riesgo` del workflow de tareas, cuando la clase es `alto`, se ejecuta en un **environment `aprobacion-riesgo-alto` con revisores obligatorios**. GitHub pausa el job hasta que un revisor lo aprueba en la interfaz y deja registrado quién y cuándo (L5).
   - **En el laboratorio:** revisor = tú, con «Prevent self-review» desactivado. No aporta independencia, pero sí una **confirmación deliberada y auditada**, distinta del merge.
   - **En equipos:** revisores = propietarios de plataforma o seguridad, con «Prevent self-review» activado.
   - Si la clase no es `alto`, el job no usa el environment y no hay pausa.
4. **Fusión automática** (sin persona): solo en N3, en clase `bajo` calculada y con auditoría. No se diseña en esta fase.
5. **Despliegue**: environment `github-pages` limitado a `main` y sin bypass de administradores (F5.6).

**Por qué una environment y no una etiqueta o un comentario:** una etiqueta o un comentario los puede escribir el agente con el token de la persona. Aprobar un environment también es posible por API (`pending_deployments`), pero pasa por `gh api`, que está en `ask` (D-042), y deja registro de quién aprobó. **Riesgo residual:** con el token completo de la persona, un agente podría aprobarlo si la persona acepta el diálogo. Se cierra con el token de mínimo privilegio de F5.5.

**Alternativas**

| Opción | Valoración |
|---|---|
| Aprobaciones fijas (≥ 1) para todo | Imposible con un mantenedor (G3) y fatiga en equipos (ADR-010, S-VILA) |
| Ruleset condicionado por etiquetas | Los rulesets no se condicionan por etiqueta (NV como imposibilidad, pero no está entre las reglas de G2) y la etiqueta es manipulable |
| GitHub App que aprueba los PR de riesgo bajo | Es «agente aprueba agente»; solo en N3 con un ADR propio |
| Merge queue | Útil con concurrencia (F4) y varios PR a la vez; opcional en N2+, no necesaria en el laboratorio |

**Supuestos que se validan en F5.7:**
- que un job de `pull_request` puede usar un environment con revisores obligatorios y queda en espera hasta la aprobación (S, G7);
- que «Prevent self-review» desactivado deja aprobar a quien abrió el PR.
