---
documento: HS-05
titulo: Modelo de componentes del harness y catálogo
version_estandar: 0.3.0-borrador
estado: propuesta (F3.1)
fecha: 2026-10-22
adr: [ADR-009, ADR-012, ADR-013, ADR-015]
fuente_de_verdad: schemas/catalog-entry.schema.json
---

# 05 · Modelo de componentes y catálogo

## 1. Qué es un componente

Un **componente** es una pieza reutilizable que cambia lo que un agente sabe, puede hacer o tiene prohibido hacer, o que automatiza una verificación. Tiene identidad (`id`), versión, propietario y ciclo de vida, y se describe en el catálogo con una **entrada** (`componente.yaml`, validada por `schemas/catalog-entry.schema.json`) y una **ficha** de 17 puntos (`FICHA.md`).

No son componentes los archivos de instrucciones (`AGENTS.md`, `CLAUDE.md`) ni los documentos núcleo. Esos tienen su ficha en `04-archivos/`.

**Regla de entrada (ADR-015).** Un componente solo entra en el catálogo si su ficha demuestra un beneficio medible frente a no tenerlo, o frente a resolverlo con un mecanismo más simple, por este orden de preferencia: instrucción → skill → CI/hook → subagente → MCP. Nada entra «por si acaso».

## 2. Tipos

El núcleo define seis tipos con un contrato neutro. El adaptador traduce cada tipo a archivos reales: §4 y `adaptadores/claude-code.md` (F3.2).

| Tipo | Propósito neutro | ¿Puede ser control? (ADR-009) | Coste de contexto (S-VILA, S-SKILLS) |
|---|---|---|---|
| `skill` | Procedimiento o conocimiento que se carga bajo demanda | **No.** Es guía (L1) | Bajo: ~100 tokens en el arranque y el cuerpo al activarse |
| `subagente` | Rol con contexto aislado, herramientas limitadas y salida estructurada | **No.** Su salida es informativa y no autoriza nada | Alto en ejecución (contexto propio) y nulo en el principal salvo el resultado |
| `hook` | Acción en un evento del ciclo del agente (antes o después de usar una herramienta, al terminar…) | **Sí, solo si es determinista** (tipo `command` o `http`) y bloquea mediante el mecanismo documentado. Los hooks `prompt` y `agent` **nunca** cuentan como control | Prácticamente nulo |
| `mcp` | Servidor que expone herramientas o datos externos | No | Alto: las descripciones de herramientas ocupan contexto (P12) |
| `workflow` | Automatización en CI (workflow reutilizable) | **Sí** (L4), si es un check requerido (L5) | Nulo en el agente |
| `plugin` | Paquete que distribuye otros componentes | Hereda lo de sus componentes | El de sus componentes |

## 3. Contrato común

Todo componente declara en su entrada de catálogo:

| Bloque | Contenido | Para qué |
|---|---|---|
| Identidad | `id`, `tipo`, `version` (SemVer), `estado`, `titulo`, `proposito`, `propietario` | Trazabilidad y responsabilidad |
| Compatibilidad | Adaptadores, versión mínima del agente, niveles y (en skills) perfil `portable` o `claude-code` (ADR-012) | Saber dónde funciona |
| Contrato | `entradas`, `salidas` y `efectos` (qué modifica, en lenguaje llano) | Componer y revisar sin leer el código |
| Permisos | Herramientas que usa, escritura (patrones de ruta), red (dominios o ninguna), acceso a secretos (`false` por defecto) | Privilegio mínimo (OWASP LLM01) y revisión de seguridad |
| Control | `es_control`, `capa` (L1–L5) y `determinista` | Impedir que una guía se presente como control (ADR-009) |
| Archivos | Origen en el catálogo → destino en la instancia | Distribución (F3.5) y comprobación de deriva |
| Calidad | `pruebas` (≥ 1), `metricas` (≥ 1), `coste`, `riesgos` (≥ 1) | Verificación y medición |
| Retirada | `condicion` y `procedimiento` | ADR-015 |
| Ficha | Ruta a `FICHA.md` (17 puntos) | Documentación completa |

## 4. Entradas no confiables y seguridad

1. **Todo componente es configuración de agentes** (ADR-013). Vive en rutas de `patrones_sensibles` dentro de la instancia y bajo CODEOWNERS, tanto en el catálogo como en la instancia.
2. **Privilegio mínimo.** Un `subagente` de revisión o verificación DEBERÍA declarar solo herramientas de lectura y ejecución de los comandos del contrato. Un componente con `secretos: true` o red abierta requiere aprobación de seguridad en su paso a `estable`.
3. **Datos frente a instrucciones.** Los componentes que leen contenido externo (issues, web, salidas de MCP) lo tratan como dato: no siguen instrucciones que aparezcan en él (S-MCP: las descripciones de herramientas no son confiables).
4. **MCP:**
   - transporte `stdio` para servidores locales;
   - sin *token passthrough*;
   - el comando completo se muestra en la ficha;
   - nunca se aprueba de forma automática desde el repositorio (verificado: un repositorio no puede aprobar sus propios servidores en sesión interactiva).
5. **CI** (R-14): un componente pensado para ejecutarse con el agente en CI declara que se usa con `--bare` y con configuración que no proviene del PR.

## 5. Ciclo de vida

```
experimental ──► estable ──► deprecado ──► retirado
      └──────────────────────────────────────▲  (retirada directa si el experimento no demuestra valor)
```

| Estado | Significado | Condición para entrar |
|---|---|---|
| `experimental` | Disponible para pilotos; puede cambiar sin aviso | Entrada válida, ficha completa y pruebas que pasan |
| `estable` | Recomendado; cambios con SemVer | Evidencia de uso (`evidencia` ≥ 1: enlace a ejecución o PR), métricas medidas, revisión del propietario y de plataforma; si tiene permisos elevados, también de seguridad |
| `deprecado` | No usar en adopciones nuevas | `deprecacion.motivo` y, si existe, `deprecacion.reemplazo`; fecha de retirada prevista |
| `retirado` | Fuera del catálogo distribuible; la entrada se conserva para la trazabilidad | Ninguna instancia lo usa o venció el plazo de deprecación |

Los cambios de estado se hacen por PR en el repositorio central. La CLI validará las transiciones (F3.3), igual que con las tareas.

## 6. Estructura del catálogo (repositorio central)

```
catalog/
├── README.md                      # índice generado (F3.3)
└── <tipo>/<id>/
    ├── componente.yaml            # entrada (schemas/catalog-entry.schema.json)
    ├── FICHA.md                   # 17 puntos (standard/05-componentes/_PLANTILLA-FICHA.md)
    ├── src/…                      # archivos que se instalan (SKILL.md, agente .md, script de hook…)
    └── tests/…                    # pruebas del componente
```

`<id>` sigue las reglas de nombre de Agent Skills (1–64 caracteres, `a-z0-9-`, sin `--`), para que una skill pueda conservar su `id` como `name`.

## 7. Distribución a las instancias (ADR-017)

Los componentes llegan a una instancia **por copia versionada**. El catálogo viaja dentro del paquete de la CLI, así que fijar `cli-v…` fija también el catálogo.

```bash
harness components list                 # catálogo y estado de lo instalado
harness components add cerrar-tarea     # instala (y añade dependencias: verificador)
harness components sync                 # actualiza a la versión del catálogo de la CLI, si no hay cambios locales
harness components remove cerrar-tarea  # retira archivos y configuración (si no se han modificado)
```

- `.harness/components.lock` registra la versión, el origen, el SHA-256 de cada archivo (con los finales de línea normalizados) y el fragmento de `settings.json` aportado.
- `harness check` avisa de la deriva (HS-CMP-009).
- Cada operación se sube en un PR, porque toca rutas sensibles (ADR-013).
