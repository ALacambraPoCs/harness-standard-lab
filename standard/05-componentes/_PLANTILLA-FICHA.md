---
# Ficha de componente (17 puntos, encargo del proyecto). Copia como catalog/<tipo>/<id>/FICHA.md.
# La entrada de catálogo (componente.yaml) es la fuente de verdad de los datos estructurados;
# la ficha los explica y no los duplica: cita el campo en vez de copiarlo.
componente: <id>
---

# <Título> (`<tipo>` · `<id>`)

## 1. Nombre y propósito
Qué hace, en una o dos frases. → `proposito`

## 2. Problema que resuelve
Qué falla hoy sin el componente, con evidencia (incidente, métrica o PR).

## 3. Objetivo y beneficios esperados
Beneficio medible y cómo se medirá. Debe enlazar con `metricas`.

## 4. Principios y conceptos fundamentales
Principios del estándar en que se apoya (P1…, ADR-…).

## 5. Cuándo utilizarlo y cuándo no
- Usar cuando: …
- No usar cuando: … (incluye la alternativa más simple que lo hace innecesario)

## 6. Arquitectura y funcionamiento
Evento o disparador, flujo y salidas. Un diagrama si aclara.

## 7. Implementación paso a paso
Cómo se instala en una instancia (archivos → `archivos`) y cómo se configura.

## 8. Ejemplo concreto
Configuración o invocación real, ejecutable.

## 9. Integración con el resto del harness
Con qué roles, requisitos, workflows y componentes interactúa (`dependencias`).

## 10. Responsabilidades
| Quién | Responsabilidad |
|---|---|
| Persona (propietario) | … |
| Agente | … |
| Sistema automatizado (CI/hook) | … |

## 11. Seguridad, permisos, límites y modos de fallo
Permisos (→ `permisos`), entradas no confiables, qué pasa si falla (¿abierto o cerrado?) y cómo se nota.

## 12. Estrategia de pruebas y verificación
→ `pruebas`. Qué se prueba de forma automática y qué no.

## 13. Métricas de eficacia, calidad, coste y latencia
→ `metricas`, `coste`. Valor de referencia y umbral de retirada.

## 14. Alternativas y compromisos
| Alternativa | Por qué no |
|---|---|

## 15. Dependencias, madurez y portabilidad
→ `compatibilidad`, `estado`. Qué cambia con otros adaptadores.

## 16. Criterios de aceptación para considerarlo implementado
1. …

## 17. Referencias y decisiones relacionadas
ADR, requisitos, fuentes (con URL o ID del inventario).
