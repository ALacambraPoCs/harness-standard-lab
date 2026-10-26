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
| Estado intermedio | Job `sync-issues` de `harness-tasks-lifecycle.yml` (push a la rama por defecto): `harness tasks issue-sync --base <before>` refleja `status` como etiqueta `status:<valor>` (sustituye la anterior) y el `owner` como asignado; en `done` comenta el enlace al run. Solo actúa sobre tareas cambiadas en el push. El titular del `lease` no se usa como asignado: puede ser un agente, que no es usuario de GitHub. |
| Permisos | Job separado con solo `issues: write`, sin credenciales del modelo (ADR-013). |
| Divergencia | Prevalece el archivo; la CI sobrescribe la issue. |
| Regla CLI | Si existe `issue:`, debe ser un entero positivo (esquema). `pr.issue`: un PR que lleva a `done` una tarea con `issue` debe incluir `Closes #<n>`. La existencia de la issue se comprueba al sincronizar (error de API visible en el run). `--dry-run` muestra las operaciones sin llamar a la API. |
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

## Registro de medición

| Fecha | Tareas con `issue` | Sincronizaciones | Desincronizaciones sin resolver | Duración del job | Notas |
|---|---|---|---|---|---|
| 2026-10-22 | 1 (T-0002 → #4) | 3 (PR #5, #6 y #7) | 0 | Pendiente de leer en Actions | Inicio en `harness-example-greenfield` (E-013). Fricción observada: hay que predecir `issue` y `done_pr` |
| 2026-10-23 | 2 (T-0002 → #4, T-0004 → #8) | 6 (PR #5, #6, #7, #9, #10 y #11) | 0 | Pendiente de leer en Actions | E-019. La skill `cerrar-tarea` elimina la predicción de `done_pr` (se escribe tras abrir el PR); `issue` sigue creándose a mano antes del archivo. Fricción nueva: dependencia de `gh` (H-10) |
| 2026-10-24 | 3 (T-0002 → #4, T-0004 → #8, T-0006 → #12) | 9 (+ PR #13, #14 y #15) | 0 | Pendiente de leer en Actions | E-022/E-023. Sin fricción nueva en la sincronización; la fricción está en `gh pr edit` (H-13), no en X-01 |
