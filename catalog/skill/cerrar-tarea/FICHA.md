---
componente: cerrar-tarea
---

# Cerrar una tarea en el PR que la completa (`skill` · `cerrar-tarea`)

## 1. Nombre y propósito
Skill portable (Agent Skills) con el procedimiento de ADR-016 para cerrar una tarea. Ver `proposito`.

## 2. Problema que resuelve
Fricción observada en F2.6:
- `done_pr` exige conocer el número del PR antes de escribirlo;
- el índice debe regenerarse;
- la issue necesita `Closes #n`.

Cada olvido es un ciclo de CI fallido (`tasks.done-pr`, `tasks.index`, `pr.issue`) por un problema de forma, no de fondo.

## 3. Objetivo y beneficios esperados
Cero fallos de forma en los PR de cierre y un solo push hasta tener la CI de tareas en verde (`metricas`).

## 4. Principios y conceptos fundamentales
- Divulgación progresiva: solo la descripción ocupa contexto hasta que se usa (S-SKILLS).
- ADR-016: el `done` lo decide la CI.
- La skill no relaja nada: prohíbe tocar criterios e inventar aprobadores.

## 5. Cuándo utilizarlo y cuándo no
- **Usar:** al terminar una tarea con archivo `T-NNNN`.
- **No usar:**
  - en PR triviales (D-023), que no tienen tarea;
  - si algún criterio falla: primero hay que corregirlo;
  - para cancelar una tarea, que es otra transición (`cancelled`).

## 6. Arquitectura y funcionamiento
El agente carga la skill por su descripción cuando la tarea está lista. La skill le guía en 8 pasos y se apoya en la CLI (`harness tasks index`, `tasks validate`, `pr check`) y en el subagente `verificador` si existe.

## 7. Implementación paso a paso
1. Copiar `src/SKILL.md` a `.claude/skills/cerrar-tarea/SKILL.md` (ADR-012).
2. `harness check` (HS-CMP-001 y 002).
3. Instalar la CLI `harness` en local (cli-v0.3.0 o posterior) y `gh`.

## 8. Ejemplo concreto
«La tarea T-0003 ya está; ciérrala». El agente:
1. abre el PR en borrador, que resulta ser el #9;
2. mueve el archivo y escribe `done_pr: 9` y el resultado;
3. ejecuta `harness tasks index --write` y `harness tasks validate --base origin/main --pr-number 9 --run-acceptance`;
4. sube y marca el PR como listo.

## 9. Integración con el resto del harness
- Ficha `plans.dir`, ADR-016.
- HS-STA-002…006, HS-CI-002.
- X-01 (`Closes #n`).
- Componentes `verificador` (dependencia) y `verificar-al-terminar`.
- Las reglas `ask` de `git push` (HS-SEC-008) siguen pidiendo confirmación.

## 10. Responsabilidades
| Quién | Responsabilidad |
|---|---|
| Persona | Confirmar el push, aprobar el PR (y ser `verified_by` de los criterios manuales) y fusionar |
| Agente | Seguir los pasos y no cambiar criterios ni inventar aprobadores |
| CI | Volver a ejecutar los criterios y decidir (ADR-016) |

## 11. Seguridad, permisos, límites y modos de fallo
- **Permisos:**
  - escribe en `docs/plans/`;
  - hace `git push`, con confirmación por la regla `ask`;
  - usa `gh` contra api.github.com;
  - no usa secretos más allá de la sesión de `gh` de la persona.
- **Riesgos:**
  - **debilitar criterios**: prohibido en la skill; regla candidata para F5 (avisar si un PR cambia `acceptance` de una tarea que pasa a `done`);
  - **inventar `verified_by`**: la CI lo comprueba contra los aprobadores reales.
- **Fallo:** si falta `gh` o red, el agente se detiene en el paso 1 y avisa.

## 12. Estrategia de pruebas y verificación
- **Unitarias:**
  - especificación y perfil;
  - **cada comando `harness` citado lo acepta la CLI real**, opciones incluidas, con una prueba que confirma que una opción inventada se rechaza;
  - presencia de los errores frecuentes.
- **Evaluación:** F3.6.

## 13. Métricas de eficacia, calidad, coste y latencia
Ver `metricas` y `coste`.

## 14. Alternativas y compromisos
| Alternativa | Por qué no |
|---|---|
| Instrucciones en AGENTS.md | Ocuparían contexto en todas las sesiones; la skill solo cuando se usa |
| Automatizar en la CLI (`harness tasks close`) | Mejor a medio plazo (condición de retirada); requiere la API de GitHub y una decisión de diseño (F5/F7) |
| Bot que escribe `done` tras el merge | Descartado en ADR-016 |

## 15. Dependencias, madurez y portabilidad
- `experimental`.
- Perfil `portable`: la leen Claude Code, Copilot y Cursor (ADR-012).
- Depende de git, `gh` y la CLI `harness`.

## 16. Criterios de aceptación para considerarlo implementado
1. Pruebas unitarias en verde.
2. `harness catalog validate` sin errores.
3. En F3.6, el PR de cierre de T-0003 pasa `harness tasks` en el primer push del cierre.

## 17. Referencias y decisiones relacionadas
- ADR-016, ADR-012.
- E-011…E-013 (fricción observada).
- S-SKILLS.
- Ficha `plans.dir`.
