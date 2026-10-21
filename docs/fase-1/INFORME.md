---
documento: F1-INFORME
titulo: Informe de cierre de la Fase 1 — Fundamentos normativos
estado: CERRADA (2026-10-20)
fecha: 2026-10-19
---

# Fase 1 · Fundamentos normativos — informe

## 1. Qué se ha entregado

| Entregable (F0-04 §3) | Ubicación | Estado |
|---|---|---|
| Esqueleto del repositorio central | raíz de `harness-standard/` | ✅ |
| README, GOVERNANCE (borrador) y CHANGELOG | `README.md`, `GOVERNANCE.md`, `CHANGELOG.md` | ✅ (Q-01 abierta) |
| ADR como archivos individuales | `adr/ADR-001…015` + índice | ✅ |
| Terminología y convenciones normativas | `standard/00-alcance-terminologia.md` | ✅ borrador |
| Modelo conceptual | `standard/01-modelo-conceptual.md` | ✅ borrador |
| Niveles de conformidad y waivers | `standard/02-niveles-de-conformidad.md` | ✅ borrador |
| Registro de requisitos N0 | `standard/requirements.yaml` (23 requisitos, todos `propuesto`) | ✅ **pendiente de aprobación** |
| Registro de roles | `standard/roles.yaml` | ✅ |
| Esquemas | `schemas/{manifest,requirement,roles}.schema.json` | ✅ |
| CLI `harness` (Python) | `tools/harness-cli/` · `check`, `explain`, `matrix` · 20 reglas | ✅ |
| Fixtures y autotests | `tests/fixtures/` (2 conformes, 31 no conformes) · `tests/*.py` (44 tests) | ✅ |
| Matriz de trazabilidad | `docs/MATRIZ.md` (generada) | ✅ |
| CI del repositorio central y workflow reutilizable | `.github/workflows/ci.yml`, `harness-conformance.yml` | ✅ validados con actionlint; **sin ejecutar en GitHub** (R-09) |
| Plantilla mínima N0 (provisional) | `template/` | ✅ supera su propio validador |

## 2. Criterios de aceptación de la fase

| Criterio | Resultado | Evidencia |
|---|---|---|
| El repositorio central existe con su CI | Parcial | Estructura y workflows listos y validados con actionlint. Falta publicarlo en GitHub (Q-10). |
| `harness check` pasa sobre el fixture conforme y falla con un mensaje de remedio sobre el no conforme | ✅ | 2 casos conformes y 31 no conformes. Cada hallazgo sigue el formato QUÉ / POR QUÉ / CÓMO. |
| Cada requisito N0 tiene ID, naturaleza, verificabilidad y fuente | ✅ | Lo garantiza el esquema `requirement.schema.json`, que se valida al cargar el estándar. |
| La matriz se genera sin requisitos automatizables sin regla | ✅ | `harness matrix --strict` → código de salida 0. Única incidencia no bloqueante: HS-SEC-004 es *enforcement* con verificación manual, pendiente de la Fase 5. |
| La plantilla supera su propio validador | ✅ | `tests/test_template.py` |
| El paquete se instala y funciona fuera del repositorio | ✅ | `pip install .` en un venv limpio; la CLI usa la copia empaquetada del estándar. |

Comandos para reproducirlo:

```bash
python -m pip install ".[test]"
python -m pytest -q                       # 44 passed
harness matrix --strict --output docs/MATRIZ.md
harness check --path tests/fixtures/conforming/n0-basico --run-commands
```

## 3. Decisiones de diseño tomadas durante la implementación

Son decisiones menores que no requerían ADR y se pueden revertir.

1. **`niveles_definidos` en `requirements.yaml`.** Si una instancia declara un nivel sin requisitos definidos (N1 a N3 en la v0.1), la CLI lo trata como error (HS-GOV-002). Así nadie puede declarar N2 y cumplirlo trivialmente.
2. **Fechas del manifiesto como texto.** El YAML se carga sin convertir las fechas a objetos, para que el esquema las valide con `format: date`.
3. **Semántica de CODEOWNERS.** Se implementa la de GitHub: gana el último patrón que coincide, y `docs/*` no cubre subdirectorios. Las rutas sensibles se comprueban con rutas de ejemplo (`roles.yaml#rutas_sensibles`).
4. **Detección de `@imports`.** Solo cuenta como import un token con extensión de archivo. Así se ignoran las menciones `@org/equipo` y los correos.
5. **Workflows reutilizables en `.github/workflows/`.** Se corrige así F0-02 §3, que los situaba en `ci/`; GitHub solo admite reutilizables en esa ruta.
6. **Ejecución de comandos solo con `--run-commands`.** Está activada por defecto en el workflow reutilizable, que no tiene secretos ni permisos de escritura (ADR-013).

## 4. Limitaciones conocidas

- **Sin ejecución real en GitHub.** El workflow reutilizable (checkout del estándar, instalación, informe en el resumen del job) solo se ha validado de forma estática.
- **Requisitos L5 verificados a mano.** La CLI no consulta los rulesets de GitHub, por lo que no comprueba que el check sea requerido ni que la revisión de code owner sea obligatoria. Esos requisitos (HS-GOV-004, HS-SEC-002) se verifican a mano hasta la Fase 5.
- **Secretos.** HS-SEC-004 no tiene regla automática. El estándar remite al secret scanning y a la push protection de GitHub.
- **Presupuesto de contexto.** Se mide en líneas por archivo, no en el total cargado en el arranque.
- **`harness init` no existe todavía.** La plantilla se copia a mano.

## 5. Qué necesito de ti

1. **Revisar los 23 requisitos N0** (resumen en `standard/02-niveles-de-conformidad.md` §3). Para cada uno: aprobarlo, ajustarlo o rechazarlo. Puedo presentártelos por bloques: gobierno, instrucciones, arquitectura y seguridad, comandos.
2. **Q-01:** composición del grupo de gobierno.
3. **Q-10:** organización de GitHub donde publicar `harness-standard` y nombres de los equipos, para ejecutar la CI y el workflow reutilizable de verdad.

## 6. Cierre de la fase (2026-10-20)

| Criterio | Estado | Evidencia |
|---|---|---|
| Requisitos N0 aprobados | ✅ | D-015 (23 requisitos) |
| Repositorio central publicado con CI en verde | ✅ | E-001, E-002 (cli 0.1.1, sin avisos) |
| El push directo a `main` lo bloquea la plataforma | ✅ | E-003 (`GH013`) |
| Una instancia separada usa el workflow reutilizable y detecta incumplimientos | ✅ | E-004 (HS-INS-002 detectado) |
| Un check no requerido no basta: hace falta L5 | ✅ (lección) | E-005 (merge con check rojo antes del ruleset) |
| El check requerido bloquea el merge | ✅ | E-006 |
| La corrección desbloquea el merge | ✅ | E-007 |

Lecciones incorporadas:

1. **Las copias Windows→WSL añaden metadatos ADS** que rompen el clonado en Windows. La CI central rechaza ya rutas no portables (R-11, cli 0.1.1).
2. **En una organización Free, los repos privados no aplican los rulesets.** El laboratorio usa repos públicos (D-018).
3. **El orden importa:** sin el ruleset activo, un check rojo no impide fusionar (E-005). El runbook de adopción debe exigir crear el ruleset **antes** del primer PR. Esto se lleva a la Fase 9.

## 7. Propuesta de alcance de la Fase 2

1. Estructura canónica N0–N1 (`standard/03-estructura-canonica.md`).
2. Fichas de archivo (`standard/04-archivos/`): AGENTS.md raíz y local, CLAUDE.md, mapa de arquitectura, ADR del proyecto, política de seguridad, contrato de comandos, CODEOWNERS y plantilla de PR.
3. **Esquema de tarea y plan** (ADR-005): estados, transiciones, evidencia y su verificación por CI. Base de N1.
4. Requisitos **N1** con reglas y fixtures, incluido el de rutas portables en instancias.
5. Decisiones que tomar: Q-02 (idioma de los archivos de instancia), umbral de "tarea trivial" sin archivo, y si el estado de las tareas se enlaza con GitHub Issues (Q-04).
