# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Hay dos líneas de versión: **standard** (A) y **cli** (B).

## [cli 0.1.1] — 2026-10-20

### Cambiado
- Acciones de GitHub fijadas por SHA a versiones con runtime Node 24: `actions/checkout` v7.0.1, `actions/setup-python` v7.0.0 y `actions/upload-artifact` v7.0.2. Elimina el aviso de deprecación de Node 20 que apareció en la primera ejecución de la CI.
- Runner fijado a `ubuntu-24.04`, porque `ubuntu-latest` migra a Ubuntu 26 desde el 2026-10-19.
- El workflow reutilizable usa por defecto `cli-ref: cli-v0.1.1`.

### Añadido
- La CI del repositorio central rechaza rutas no portables a Windows (`:`, `<>"|?*\`, espacio o punto final). Así se detecta el incidente de los metadatos ADS del 2026-10-20.

## [standard 0.1.0] [cli 0.1.0] — 2026-10-20 — Fase 1

### Cambiado (2026-10-20)
- Los 23 requisitos N0 pasan a estado `aprobado` (D-015).
- El workflow reutilizable recibe `standard-repository` explícito; plantilla y fixtures lo pasan.
- Ejemplo `examples/greenfield` (instancia real del laboratorio) y comprobación en la CI central.
- `.github/CODEOWNERS` del repositorio central.
- Runbook de publicación `docs/fase-1/PUBLICACION.md`.

### Primera entrega (2026-10-19)

### Añadido
- Estructura del repositorio central (ADR-001).
- `standard/00-alcance-terminologia.md`, `01-modelo-conceptual.md` y `02-niveles-de-conformidad.md`.
- `standard/requirements.yaml` con los requisitos del nivel N0.
- `standard/roles.yaml` con los roles de archivo (ADR-004).
- Esquemas `manifest`, `requirement` y `roles` (JSON Schema 2020-12).
- CLI `harness` en Python con los comandos `check`, `matrix` y `explain`, las reglas del nivel N0, la salida en texto y en JSON, y la gestión de waivers.
- Fixtures conformes y no conformes, y autotests con pytest.
- Workflows `ci.yml` (CI de este repositorio) y `harness-conformance.yml` (reutilizable, `workflow_call`).
- ADR-001 a ADR-015 como archivos individuales en `adr/`.

### Corregido respecto a F0-02
- Los workflows reutilizables se ubican en `.github/workflows/` y no en `ci/`, porque GitHub solo permite llamar a workflows reutilizables desde esa ruta.
