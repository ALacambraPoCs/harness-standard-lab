---
componente: verificar-al-terminar
---

# No dar el trabajo por terminado si check o las tareas fallan (`hook` · `verificar-al-terminar`)

## 1. Nombre y propósito
Hook `Stop` de Claude Code. Cuando el agente va a terminar, ejecuta `commands.check` del manifiesto y, si existen, `harness tasks validate`. Si algo falla, impide que el agente termine y le muestra el error. Ver `proposito` en `componente.yaml`.

## 2. Problema que resuelve
Un agente puede afirmar que ha terminado con el código roto. Hoy la primera señal llega en la CI (E-011: en el PR #7 la tarea se declaró `done` sin implementar y la CI la rechazó). Cada ida y vuelta a la CI cuesta minutos y una intervención humana.

## 3. Objetivo y beneficios esperados
Que el agente reciba la misma señal **antes** de entregar. Beneficio esperado: menos PR con `check` en rojo y menos reintentos de CI. Se mide con `metricas` frente a la línea base del piloto (F6).

## 4. Principios y conceptos fundamentales
- P-verificación: no se acepta como evidencia la afirmación del agente.
- ADR-009: un hook `command` determinista *puede* ser control L3. Este se declara `es_control: false` porque tiene salida (2 intentos por defecto) y falla en abierto: es **retroalimentación** determinista, no un control ni una autoridad.
- ADR-016: la autoridad de `done` es la CI.
- ADR-015: tiene condición de retirada.

## 5. Cuándo utilizarlo y cuándo no
- **Usar** en instancias N1+ con un `check` rápido (segundos o pocos minutos).
- **No usar:**
  - si `check` tarda mucho: la alternativa más simple es un `check` rápido en el hook y el completo en CI;
  - en sesiones sobre código no confiable;
  - en CI (allí el agente va con `--bare`, que no carga hooks, y la verificación la hace el propio workflow);
  - en una sesión de TDD con rojo intencionado: se suspende con `HARNESS_STOP_MAX=0` (§8).

## 6. Arquitectura y funcionamiento
```
Agente decide terminar ──► Stop ──► verificar_al_terminar.py
                                     ├─ lee commands.check (.harness/manifest.yaml)
                                     ├─ ejecuta check  ─┐
                                     ├─ harness tasks validate (si hay CLI y docs/plans) ─┤
                                     │                   └► ¿todo 0? ── sí ─► exit 0 (para)
                                     │                                  no ─► ¿bloqueos < 3? ─ sí ─► exit 2 + errores (sigue)
                                     │                                                      no ─► exit 0 + aviso (para)
```

## 7. Implementación paso a paso
1. `harness components add verificar-al-terminar` (ADR-017). Copia el script a `.claude/hooks/`, fusiona en `.claude/settings.json` el bloque del §8 (`configuracion.claude_settings`) y lo registra en `.harness/components.lock`.
2. `harness check`: HS-CMP-006 comprueba que el script existe y HS-CMP-009 que no hay deriva.
3. Opcional: instalar la CLI `harness` en local para que también se validen las tareas.

## 8. Ejemplo concreto
```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command",
                     "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/verificar_al_terminar.py\"",
                     "timeout": 300 } ] }
    ]
  }
}
```
Variables opcionales: `HARNESS_STOP_MAX` (2) y `HARNESS_STOP_TIMEOUT` (240 s por comando).

**Suspensión en TDD (P-5, D-045).** Si la persona quiere terminar con pruebas en rojo a propósito, arranca la sesión con `HARNESS_STOP_MAX=0 claude`. El hook no bloquea, pero sigue escribiendo en stderr lo que falla (visible en el detalle de la sesión). La variable tiene que estar en el entorno de Claude Code: el agente no la controla, y la vía indirecta (`env` en `.claude/settings*.json`) está bajo la regla `ask` de `/.claude/**`.

## 9. Integración con el resto del harness
- Usa el contrato de comandos (manifiesto, HS-VER-001).
- Usa `harness tasks validate` (HS-STA-002/003).
- Complementa la CI de tareas (HS-CI-003, ADR-016).
- Lo protege CODEOWNERS (`/.claude/`, HS-SEC-002) y se pide confirmación al editarlo (HS-SEC-008).

## 10. Responsabilidades
| Quién | Responsabilidad |
|---|---|
| Persona (propietario de la instancia) | Instalarlo, mantener `check` rápido y revisar las sesiones que agotan los reintentos |
| Agente | Corregir lo que el hook le muestra, o explicar por qué no puede |
| Sistema (hook y CI) | El hook informa en local; la CI decide (ADR-016) |

## 11. Seguridad, permisos, límites y modos de fallo
- **Permisos:** no usa herramientas del agente ni red. Escribe un contador en el directorio temporal del sistema, nunca en el repositorio.
- **Entradas:** ejecuta `commands.check` del repositorio, el mismo código que ejecutaría la persona. Por eso no debe usarse en carpetas no confiables (en `-p` sin `--bare` los hooks del proyecto se ejecutan igualmente, R-14).
- **Modos de fallo:**
  - sin manifiesto o sin `check`: falla en abierto (exit 0 con aviso), porque la CI cubre el caso;
  - error persistente: tras 2 bloqueos (configurable) deja parar y pide escalar a la persona;
  - `HARNESS_STOP_MAX` no numérico: se usa el valor por defecto;
  - suspendido (`HARNESS_STOP_MAX=0`): no bloquea; si alguien lo deja fijo en su perfil, el hook deja de ayudar a esa persona, pero la CI sigue siendo la autoridad.
  - timeout: se trata como fallo.
- **No verificado:** el campo `stop_hook_active` del evento; el límite de reintentos no depende de él. Tampoco que un `export` en un comando Bash del agente llegue al entorno del hook (por arquitectura no debería: los hooks los lanza el proceso de Claude Code).

## 12. Estrategia de pruebas y verificación
- 10 pruebas unitarias (`pruebas`): verde y rojo, límite por defecto y configurable, suspensión, valor inválido, reinicio, sin manifiesto, comillas, tareas inválidas.
- Integración en F3.6 con una sesión real (E-015, con la versión 0.2.0: 3 bloqueos y después deja parar). Hallazgo H-1 (rojo intencionado en TDD) → versión 0.3.0.

## 13. Métricas de eficacia, calidad, coste y latencia
Ver `metricas` y `coste`. La línea base es el porcentaje de PR del piloto con `check` en rojo en el primer push. Umbral de retirada: sin mejora en 4 semanas.

## 14. Alternativas y compromisos
| Alternativa | Por qué no |
|---|---|
| Instrucción en AGENTS.md («ejecuta check antes de terminar») | Ya existe (L1) y no es verificable. El hook la hace determinista |
| Hook `PostToolUse` que ejecuta `check` tras cada edición | Más latencia y ruido; detecta estados intermedios rotos que son normales |
| Hook `prompt` o `agent` que «evalúa» si terminó | No determinista; no cuenta como control (ADR-009) |
| Solo la CI | Funciona, pero cada fallo cuesta un ciclo de PR |

## 15. Dependencias, madurez y portabilidad
- `experimental`.
- Solo `claude-code` (evento `Stop`, exit 2).
- Python 3 de la biblioteca estándar.
- La lógica es portable a otros agentes con un evento equivalente; el disparador no.

## 16. Criterios de aceptación para considerarlo implementado
1. Las pruebas unitarias pasan en la CI central.
2. `harness catalog validate` sin errores.
3. En F3.6, una sesión real no puede terminar con `check` en rojo, y el mensaje que ve el agente incluye el error.

## 17. Referencias y decisiones relacionadas
- ADR-009, ADR-015, ADR-016.
- `standard/adaptadores/claude-code.md` §6.
- code.claude.com/docs/en/hooks («Stop | Yes | Prevents Claude from stopping, continues the conversation»).
- E-011.
- R-14.
