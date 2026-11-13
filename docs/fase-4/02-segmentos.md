---
documento: F4-02
titulo: F4.2 · Mapa de segmentos — análisis del brownfield y propuesta de ADR-014 rev. 2
estado: propuesta (decisión 2 pendiente de aprobación)
fecha: 2026-11-13
depende_de: [D-081, D-082]
---

# F4.2 · Mapa de segmentos

## 1. Análisis del brownfield (E-045)

Análisis hecho por Claude el 2026-11-13 sobre `ALacambraPoCs/harness-example-brownfield` (`aa056dc`), en una copia local y en solo lectura. Las cifras se pueden reproducir con `git ls-files`, con `git log --since=2025-11-12` y con un análisis AST de los imports `keep.*`.

### Tamaño y cambio

| Directorio | Archivos | Commits del último año que lo tocan |
|---|---|---|
| `keep-ui/` (Next.js) | 1.043 | unos 130 (features 33, app 26, shared 23…) |
| `keep/providers/` | 354 | 57 |
| `keep/api/` (models 136, core 32, routes 30…) | 237 | 42 |
| `docs/` | 659 | 63 |
| `tests/` (plano, sin estructura por módulo) | 150 | 88 |
| Resto de `keep/` (workflows, identidad, secretos…) | unos 78 | unos 15 |
| Infraestructura (`docker*`, `keycloak/`, `elk/`, `grafana/`, `prometheus/`, `proxy/`, `otel-shared/`) | unos 45 | pocos |

En total, 164 commits en el último año.

### Dependencias reales entre los segmentos provisionales

Son imports estáticos de Python; la cifra es el número de imports.

| De → a | api | modelo-datos | motor | providers | identidad |
|---|---|---|---|---|---|
| **api** | — | 168 | 26 | 18 | 65 |
| **modelo-datos** | 11 | — | 2 | 2 | — |
| **motor** | 31 | 17 | — | 5 | 3 |
| **providers** | 21 | 66 | 204 | — | 2 |
| **identidad** | 29 | 8 | 10 | — | — |

**Hallazgo principal:** hay **8 pares de segmentos con dependencia mutua**. A nivel de paquete hay 21. Keep no tiene capas: todo depende de todo en algún punto.

Cualquier regla de dependencias «ideal» fallaría desde el primer día. El mapa tiene que **describir la realidad** y **evitar que empeore**, sin exigir una arquitectura que el código no tiene. Es lo que pasará en cualquier brownfield de Nirvana.

### Puntos calientes por naturaleza (no por cambio)

- **`keep/api/models/db/migrations/versions/`**: 93 migraciones de Alembic en una **cadena lineal**. Dos tareas que añadan una migración cada una no chocan como texto (son archivos distintos), pero dejan **dos `head`**. Es un conflicto semántico que git no ve. Es el candidato natural para el conflicto provocado de la F4.6.
- `keep-ui/package-lock.json` y `poetry.lock`: conflictos textuales seguros si dos tareas tocan dependencias.
- `tests/` es plano. Asignar cada prueba a un segmento por ruta no funciona, solo por nombre o por import.

## 2. Propuesta: ADR-014 rev. 2

La recomendación original se mantiene: un `.harness/segments.yaml` del que se derivan o validan CODEOWNERS, los `AGENTS.md` de segmento, las reglas de dependencias y la detección de solapamientos. El análisis obliga a concretar cinco puntos.

| # | Punto | Recomendación | Alternativas descartadas |
|---|---|---|---|
| 2a | **Quién lo escribe** | `harness segments propose` genera una propuesta (inventario, grafo, *hotspots*, propietarios de CODEOWNERS) que **no escribe** el mapa. Una persona la ajusta y la versiona en un PR. `.harness/segments.yaml` queda bajo CODEOWNERS de plataforma (ADR-013) | La CLI lo genera y se acepta tal cual: una agrupación automática no conoce el propósito ni la propiedad |
| 2b | **Derivados** | Se **validan** (`segments check`), no se regeneran: CODEOWNERS cubre cada segmento con su propietario, y cada segmento con `AGENTS.md` lo tiene en su raíz con los comandos del mapa | Regenerarlos: se pisarían ajustes locales y se crearía deriva en sentido contrario |
| 2c | **Dependencias** | **Línea base con trinquete**. `depende_de` declara las dependencias aceptadas. Las dependencias reales no aceptadas que ya existen van a `deuda`, con motivo y caducidad: generan un aviso, y un error al caducar. **Una dependencia nueva entre segmentos que no esté declarada es un error.** Para Keep: 8 pares mutuos en `deuda` y 0 errores al empezar | Arquitectura ideal (unos 21 errores desde el primer día; inusable). Sin reglas (el mapa deja de ser verificable y diverge) |
| 2d | **Granularidad** | Un segmento es una **unidad de propiedad y de paralelización**, no un paquete. Orientación: 5–12 por repositorio. Dentro de un segmento, `puntos_calientes` declara rutas con política propia (las migraciones, `serializada`) | Un segmento por paquete (más de 20 en Keep: mucho mantenimiento y nadie lo revisa) |
| 2e | **Lenguajes** | La cobertura de rutas sirve para cualquier lenguaje. La verificación de imports, **solo Python** en la F4.3 (AST, sin ejecutar). TypeScript se declara «no verificado» en el informe, no se finge | Analizar TS con heurísticas de texto (falsos positivos con alias de `tsconfig`) |

**Nivel.** El mapa es **DEBE en N2** y **PUEDE en N0 y N1**. Si existe en N0 o N1, se valida igual. El manifiesto ya reserva `segments` para N2 (`standard/04-archivos/manifest.md`).

### Formato propuesto (`.harness/segments.yaml`, versión 1)

```yaml
version: 1
segmentos:
  - id: modelo-datos
    proposito: Modelos SQLModel y migraciones Alembic.
    rutas: ["keep/api/models/**"]
    propietario: "@AlbertoLacambra"
    lenguaje: python
    paquetes: ["keep.api.models"]          # para atribuir imports (2e)
    depende_de: []
    contrato: ["keep/api/models/*.py"]     # interfaz pública que usan otros segmentos
    comandos: { test: "pytest tests/test_alert_dto.py" }
    riesgo: medio                          # mínimo para un PR que lo toque (pr risk)
    paralelizacion: contrato               # libre | contrato | serializada
    puntos_calientes:
      - rutas: ["keep/api/models/db/migrations/versions/**"]
        paralelizacion: serializada
        motivo: Cadena lineal de Alembic; dos migraciones a la vez dejan dos heads.
  - id: providers
    proposito: Integraciones con sistemas externos (un subdirectorio por proveedor).
    rutas: ["keep/providers/**"]
    propietario: "@AlbertoLacambra"
    lenguaje: python
    paquetes: ["keep.providers"]
    depende_de: [motor, modelo-datos]
    paralelizacion: libre                  # proveedores independientes entre sí
excluidos:                                 # cobertura explícita (criterio 1 del plan)
  - rutas: ["docs/**", "examples/**", "assets/**"]
    motivo: Documentación y ejemplos; sin código de la aplicación.
deuda:
  - de: providers
    a: api
    motivo: Importaciones heredadas de keep.api.core desde proveedores.
    caduca: 2027-06-30
```

### Segmentación provisional de Keep

Es la entrada de `segments propose`, que hay que ajustar a mano.

| Segmento | Rutas | Riesgo | Paralelización |
|---|---|---|---|
| `api` | `keep/api/**` salvo `models`; `keep/searchengine`, `keep/topologies`, `keep/event_subscriber` | medio | contrato |
| `modelo-datos` | `keep/api/models/**` (migraciones: serializada) | medio | contrato |
| `motor` | `keep/{workflowmanager,step,parser,conditions,functions,iohandler,contextmanager,actions,throttles,rulesengine,validation,exceptions}` | medio | contrato |
| `providers` | `keep/providers/**` | bajo | libre |
| `identidad` | `keep/{identitymanager,secretmanager}` | **alto** | serializada |
| `ui` | `keep-ui/**` (`package-lock.json`: serializada) | bajo | libre |
| `pruebas` | `tests/**` | bajo | libre |
| `infra` | `docker*`, `keycloak/`, `elk/`, `grafana/`, `prometheus/`, `proxy/`, `otel-shared/`, `start.sh`, `render.yaml` | alto | serializada |
| *excluidos* | `docs/`, `examples/`, `assets/`, `scripts/`, `templates/` | — | — |

## 3. Qué se implementa en la F4.2 si se aprueba

1. **Esquema** `schemas/segments.schema.json` y ficha `standard/04-archivos/segments.map.md` (rol ya referenciado por otras fichas).
2. **`harness segments propose [--path] [--since 12.months]`**, en solo lectura:
   - inventario por directorio, churn de git y grafo de imports de Python;
   - agrupación inicial por directorios de primer y segundo nivel;
   - sale YAML comentado o Markdown;
   - no escribe nada en el repositorio.
3. **`harness segments graph`**: la matriz de dependencias reales entre los segmentos de un mapa. Sirve para rellenar `deuda`.
4. **Pruebas**:
   - fixtures pequeños: un repo con un ciclo, una ruta sin cubrir y un `puntos_calientes`;
   - una prueba de que `propose` no escribe en el repositorio.
5. **Primer `segments.yaml` de Keep:** propuesta generada y ajustada por ti en un PR del ejemplo, que tendrá **Actions activado solo para los workflows del harness**. Eso se decide en ese PR.

`segments check` (cobertura, CODEOWNERS, `AGENTS.md`, trinquete de dependencias) es la **F4.3**.

## 4. Criterios de validación de la decisión

- El mapa de Keep cubre o excluye el **100 %** de las rutas versionadas.
- Con la línea base, `segments check` da **0 errores** sobre `base-f4`.
- Un import nuevo de `providers` hacia `identidad` no declarado (ni en `depende_de` ni en `deuda`), introducido a propósito, da **1 error**.
- Dos tareas con una migración cada una sobre `modelo-datos` se **serializan** (F4.4) o se detectan antes de fusionar (F4.6).
