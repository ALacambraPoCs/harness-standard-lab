# harness CLI

CLI de conformidad del Estándar de Harness (producto B). Python ≥ 3.11; dependencias: `pyyaml` y `jsonschema`.

## Comandos

| Comando | Qué hace |
|---|---|
| `harness check [--path DIR] [--run-commands] [--strict] [--format text\|json] [--json-out FILE]` | Valida una instancia contra los requisitos aplicables a su nivel y adaptadores. Código de salida 1 si hay errores (o avisos con `--strict`). |
| `harness explain <HS-…\|regla>` | Muestra un requisito o una regla. |
| `harness matrix [--strict] [--output FILE]` | (Solo en el repo central) Genera la matriz requisito → regla → fixture. Con `--strict` ejecuta los fixtures y falla ante huecos de trazabilidad. |

## Arquitectura

```
manifest + árbol ─► Context (roles → rutas) ─► reglas aplicables ─► Findings ─► waivers ─► informe (texto/JSON)
                     standard.py (requirements.yaml, roles.yaml, schemas/)
```

- `standard.py`: carga y valida los datos normativos (producto A). Busca `HARNESS_STANDARD_ROOT`, después el repo central y, por último, la copia empaquetada.
- `rules/`: una función por regla, registrada con `@rule(id, [requisitos])`. Ficheros: `core.py` (núcleo), `claude.py` (adaptador claude-code) y `github.py` (plataforma).
- `checker.py`: selección de reglas por nivel y adaptador, severidad derivada del nivel del requisito, waivers y nivel efectivo.
- `selftest.py` y `matrix.py`: autotest con `tests/fixtures/cases.yaml` y trazabilidad.

## Añadir una regla

1. Añade o actualiza el requisito en `standard/requirements.yaml`, con `reglas: [<id>]`.
2. Implementa la función con `@rule("<id>", ["HS-…"])` y una docstring. Cada `Finding` debe incluir el QUÉ y el CÓMO arreglarlo.
3. Añade al menos un caso no conforme en `tests/fixtures/cases.yaml`.
4. Ejecuta `python -m pytest` y `harness matrix --strict --output docs/MATRIZ.md`.
