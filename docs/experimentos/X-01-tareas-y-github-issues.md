---
id: X-01
titulo: Enlace de archivos de tarea con GitHub Issues
estado: aprobado (en preparación; se ejecuta en el piloto)
aprobado: 2026-10-21 (D-022)
relacionado: [ADR-005, ADR-013, D-021, Q-04]
---

# X-01 · Enlace de archivos de tarea con GitHub Issues

## Hipótesis
Enlazar cada archivo de tarea con una issue mejora la visibilidad del trabajo en curso para las personas
sin coste de sincronización apreciable y sin crear una segunda fuente de verdad.

## Diseño
| Aspecto | Regla |
|---|---|
| Fuente de verdad | El archivo de tarea (ADR-005). La issue es un espejo para personas. |
| Enlace | Campo opcional `issue: <número>` en el frontmatter durante el experimento. |
| Dirección | Solo archivo → issue. Nunca al revés. |
| Cierre | El PR que completa la tarea incluye `Closes #<n>`; GitHub cierra la issue al fusionar. |
| Estado intermedio | Job de CI posterior al merge: refleja `status` como etiqueta `status:<valor>` y el titular del `lease` como asignado. |
| Permisos | Job separado con solo `issues: write`, sin credenciales del modelo (ADR-013). |
| Divergencia | Prevalece el archivo; la CI sobrescribe la issue. |
| Regla CLI | Si existe `issue:`, debe ser un entero positivo; la existencia en el mismo repositorio se comprueba en CI con la API. |
| Seguridad | Una issue es entrada no confiable (PR-7): un agente no toma instrucciones de una issue sin que una persona responsable la convierta en archivo de tarea. |

## Métricas (≥ 4 semanas o ≥ 20 tareas en el piloto)
| Métrica | Fuente |
|---|---|
| Desincronizaciones no resueltas tras la CI | Script de comparación archivo ↔ issue |
| Coste añadido por merge | Duración del job y minutos de Actions |
| Fricción | Tareas sin `issue:` o PR sin `Closes` |
| Valor percibido | Encuesta breve: ¿consultas las issues para saber qué hay en curso? |

## Criterio de decisión
- **Adoptar** (requisito N1 DEBERÍA) si: 0 desincronizaciones no resueltas, < 1 min añadido por merge y > 50 % del equipo las consulta.
- **Retirar** el campo `issue:` y el job en caso contrario, sin migración.
