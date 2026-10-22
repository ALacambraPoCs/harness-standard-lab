---
componente: verificador
---

# Verificación independiente de la tarea en curso (`subagente` · `verificador`)

## 1. Nombre y propósito
Subagente de Claude Code que verifica el trabajo en curso **con comandos** y devuelve un informe de formato fijo. Ver `proposito`.

## 2. Problema que resuelve
- El agente que implementa evalúa su propio trabajo con el contexto lleno de sus propias suposiciones; es el sesgo que motivó ADR-016.
- Además, ejecutar y leer salidas de pruebas consume contexto del agente principal.

## 3. Objetivo y beneficios esperados
- Una segunda comprobación con contexto limpio antes de pedir revisión.
- Menos contexto gastado en el agente principal.
- Medido por la coincidencia con la CI y el coste por invocación (`metricas`).

## 4. Principios y conceptos fundamentales
- Separación entre quien hace y quien verifica.
- Privilegio mínimo (`tools` explícito, HS-CMP-005).
- Contenido externo como dato (OWASP LLM01).
- La revisión de un agente es **informativa**, no autorización (encargo, «Colaboración y seguridad»).

## 5. Cuándo utilizarlo y cuándo no
- **Usar:** antes de abrir o actualizar un PR, o antes de aplicar la skill `cerrar-tarea`.
- **No usar:**
  - en cambios triviales (D-023), donde el coste supera el beneficio;
  - como sustituto de la CI;
  - cuando el hook `verificar-al-terminar` ya basta (cambios sin criterios de aceptación propios).

## 6. Arquitectura y funcionamiento
El agente principal delega en `verificador` (contexto aislado, herramientas `Read`, `Grep`, `Glob` y `Bash`). El subagente:
1. lee el manifiesto y la tarea;
2. ejecuta `check`, `test` y los criterios;
3. devuelve el informe;
4. no conserva estado.

## 7. Implementación paso a paso
1. Copiar `src/verificador.md` a `.claude/agents/verificador.md`.
2. `harness check` (HS-CMP-004 y 005).
3. Invocarlo: «usa el subagente verificador para T-NNNN».

## 8. Ejemplo concreto
```
VERIFICACIÓN · T-0003 · 2026-10-23 10:12
check: python3 -m py_compile src/app.py → código 0
test:  python3 -m unittest discover -s tests → código 1
AC1 total() rechaza precios negativos: python3 -m unittest tests.test_app.TotalTest.test_precio_negativo → código 1
RESULTADO: NO LISTO (AC1 y test fallan)
```

## 9. Integración con el resto del harness
- Lee el contrato de comandos y los archivos de tarea (`plans.dir`).
- Su informe es la evidencia que se pega en `harness:evidencia` del PR.
- Lo complementan el hook `verificar-al-terminar` y la skill `cerrar-tarea`.

## 10. Responsabilidades
| Quién | Responsabilidad |
|---|---|
| Persona | Decidir con el informe y la CI; nunca solo con el informe |
| Agente principal | Invocarlo y actuar sobre NO LISTO |
| Subagente | Ejecutar y reportar sin modificar nada |
| CI | Autoridad final (ADR-016) |

## 11. Seguridad, permisos, límites y modos de fallo
- **Bash:** es necesario para ejecutar las pruebas, pero permite escribir. La restricción a solo lectura es **instrucción (L1)**. Mitigación técnica parcial: las reglas `ask` y `deny` de `settings.json` siguen aplicando dentro del subagente. **No verificado:** si `tools` admite patrones de Bash para el subagente. Se revisará en F3.6.
- **Modos de fallo:** un informe erróneo (LISTO cuando no lo está) se descubre en la CI. Un comando colgado lo corta el tiempo máximo de Bash del agente.

## 12. Estrategia de pruebas y verificación
- **Unitarias:** frontmatter, ausencia de herramientas de escritura e instrucciones obligatorias.
- **Evaluación (F3.6):** un caso NO LISTO real.

## 13. Métricas de eficacia, calidad, coste y latencia
Ver `metricas` y `coste`. Umbral de retirada: coincidencia con la CI por debajo del 95 %.

## 14. Alternativas y compromisos
| Alternativa | Por qué no |
|---|---|
| Que el agente principal ejecute las pruebas | Es lo habitual; no aísla el contexto ni separa roles |
| Subagente con permiso de corrección | Mezcla verificar y hacer; pierde independencia |
| Solo el hook | El hook no lee criterios de aceptación ni produce informe |

## 15. Dependencias, madurez y portabilidad
- `experimental`, solo `claude-code`.
- El cuerpo del prompt es neutro y portable a otros agentes con subagentes.

## 16. Criterios de aceptación para considerarlo implementado
1. Pruebas unitarias en verde.
2. `harness catalog validate` sin errores.
3. En F3.6, el informe coincide con el resultado de la CI en un caso que pasa y en otro que falla.

## 17. Referencias y decisiones relacionadas
- ADR-016, ADR-009.
- HS-CMP-004, HS-CMP-005.
- code.claude.com/docs/en/sub-agents.
- S-OWASP-LLM01.
