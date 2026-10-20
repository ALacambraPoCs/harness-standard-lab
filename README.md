# harness-standard

> Laboratorio publicado en [`ALacambraPoCs/harness-standard-lab`](https://github.com/ALacambraPoCs/harness-standard-lab). Instancia de ejemplo: `ALacambraPoCs/harness-example-greenfield` (ver `docs/fase-1/PUBLICACION.md`).

Repositorio central del **Estándar de Harness** para el desarrollo de software con agentes de IA. Contiene dos productos (ADR-001):

| Producto | Qué es | Dónde está | Versión actual |
|---|---|---|---|
| **A · Estándar** | Normas: requisitos identificados (`HS-<DOMINIO>-NNN`), especificaciones de archivos y componentes, niveles de conformidad y procedimientos | `standard/`, `schemas/`, `adr/` | `0.1.0` (N0 aprobado; ver `standard/VERSION`) |
| **B · Plantilla ejecutable** | CLI de conformidad, reglas, scaffold, workflows reutilizables, ejemplos y fixtures | `tools/harness-cli/`, `template/`, `.github/workflows/`, `examples/`, `tests/` | `0.1.1` (ver `pyproject.toml`) |

El tercer producto, **C · Instancia**, vive en cada repositorio de proyecto. Se identifica por su archivo `.harness/manifest.yaml`.

> **Precedencia:** si el estándar (A) y la plantilla (B) discrepan, prevalece A. La discrepancia se registra como un defecto de B.

## Estado

**Fase 1 (fundamentos normativos) completada en borrador.** Incluye:

- terminología;
- modelo conceptual;
- niveles de conformidad N0–N3;
- requisitos del nivel N0;
- esquemas del manifiesto y de los requisitos;
- CLI `harness` con las reglas del nivel N0.

Los niveles N1–N3 y las especificaciones detalladas de cada archivo llegarán en las fases 2 a 6 (`docs/fase-0/04-metodo-y-plan.md`).

## Estructura

```
standard/            normas (producto A)
  VERSION
  00-alcance-terminologia.md
  01-modelo-conceptual.md
  02-niveles-de-conformidad.md
  requirements.yaml  registro máquina de requisitos
  roles.yaml         registro de roles de archivo (ADR-004)
  04-archivos/       fichas de archivo (Fase 2)
  05-componentes/    contratos de componentes (Fase 3)
  adaptadores/       claude-code, github (Fases 3 y 5)
schemas/             JSON Schemas versionados
adr/                 decisiones de arquitectura del estándar
tools/harness-cli/   CLI de conformidad (Python ≥ 3.11)
template/            scaffold núcleo + adaptadores (Fase 2+)
examples/            instancias de ejemplo (greenfield, brownfield)
tests/fixtures/      instancias conformes y no conformes para autotest
.github/workflows/   CI del repositorio y workflow reutilizable de conformidad
docs/                documentos de trabajo por fase y REGISTRO
```

## Uso rápido de la CLI

```bash
pip install "git+https://github.com/ALacambraPoCs/harness-standard-lab@cli-v0.1.1"
harness check                   # valida el repositorio actual
harness check --format json     # salida para CI
harness check --path ../otro-repo
harness matrix                  # (en este repo) matriz requisito → regla → fixture
```

En un repositorio de proyecto, el check de conformidad se añade llamando al workflow reutilizable:

```yaml
# .github/workflows/harness.yml
name: harness
on: [pull_request, merge_group]
permissions:
  contents: read
jobs:
  conformance:
    uses: ALacambraPoCs/harness-standard-lab/.github/workflows/harness-conformance.yml@cli-v0.1.1
    with:
      standard-repository: ALacambraPoCs/harness-standard-lab
      cli-ref: cli-v0.1.1
```

## Contribuir

Todo cambio en `standard/` sigue el proceso de `GOVERNANCE.md`. Cada requisito automatizable entra en el mismo PR que su regla y que sus fixtures (conforme y no conforme). La CI lo comprueba con `harness matrix --strict`.
