---
rol: decisions.dir
titulo: Registro de decisiones del proyecto (ADR)
estado: propuesta
version: 0.1.0
consumidores: [personas, agentes]
dependencias: [architecture.map, instructions.root]
propietario: Tech lead del repositorio (aprueba los ADR del proyecto)
requisitos: [HS-ARC-002, "pendiente:F2.5"]
reglas: [core.decisions.exists]
ejemplo_canonico: template/core/docs/decisions/_plantilla.md
fuentes: [S-NYGARD-ADR, S-LHE#L05, S-OAI-HE#p6]
evolucion: >-
  MAJOR si cambia el formato obligatorio (frontmatter o estados); MINOR si se añade un campo opcional; PATCH editorial.
---

# Registro de decisiones del proyecto (ADR)

> Ruta (reubicable), obligatoriedad y nivel: `standard/roles.yaml#decisions.dir`.

## Propósito

Guardar **por qué** se tomó cada decisión significativa, para que ninguna persona ni agente la deshaga sin conocer sus motivos.

Responde a un fallo documentado: la compactación de contexto conserva el "qué" pero pierde el "por qué" (S-LHE L05). Sigue el formato de *Architecture Decision Record* (S-NYGARD-ADR).

**Qué es una decisión significativa:** la que afecta a la estructura, las dependencias, las interfaces, la seguridad o los atributos de calidad, o la que es cara de revertir.

## Contenido requerido

**El directorio:**

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|
| `README.md` índice con una tabla: número, título, estado | `<!-- harness:indice -->` | HS-ARC-002 (existencia); índice pendiente:F2.5 | Automática |
| Al menos un ADR. En la adopción, el ADR de "adoptar el estándar" | — | HS-ARC-002 | Automática |

**Cada ADR** (`NNNN-<slug>.md`) con frontmatter:

| Campo | Valores | Obligatorio |
|---|---|---|
| `id` | `ADR-NNNN`, igual al número del archivo | Sí |
| `titulo` | Texto | Sí |
| `estado` | `propuesta`, `aceptada`, `rechazada`, `reemplazada`, `deprecada` | Sí |
| `fecha` | `AAAA-MM-DD` | Sí |
| `decisores` | Lista de personas o equipos | Sí |
| `reemplaza` / `reemplazada_por` | `ADR-NNNN` | Si aplica |

Secciones del cuerpo: **Contexto**, **Decisión**, **Consecuencias** y **Alternativas consideradas**. Opcional: **Validación**.

## Contenido recomendado y opcional

- Enlazar en la tarea (`plans.active`) los ADR que motiva o que respeta.
- **Un agente PUEDE redactar un ADR en estado `propuesta`.** Solo una persona de `decisores` lo pasa a `aceptada`, y siempre mediante PR.

## Contenido excluido

| No incluir | Va en |
|---|---|
| Decisiones triviales (nombres de variables, formato) | Linters y convenciones |
| Ediciones de un ADR aceptado que cambien su decisión | Un ADR nuevo que lo reemplaza. El aceptado no se reescribe |
| Planes de ejecución o progreso | `plans.active` |
| Normas del estándar corporativo | Repositorio central (`adr/` del estándar), no la instancia |

## Formato y convenciones

- Markdown con frontmatter YAML. Nombre `NNNN-<slug>.md`, con numeración correlativa sin huecos reutilizados.
- `_plantilla.md` (con guion bajo inicial) está exento de la numeración y no cuenta como ADR.
- Inmutables una vez `aceptada`. Solo se permiten correcciones editoriales y el cambio de `estado` a `reemplazada` o `deprecada`.
- Idioma libre (D-020). Claves y estados, fijos.

## Ejemplo canónico

Plantilla: `template/core/docs/decisions/_plantilla.md`. Ejemplo de adopción: `template/core/docs/decisions/0001-adoptar-estandar-de-harness.md`.

## Validaciones

| Validación | Capa | Estado |
|---|---|---|
| Existe el directorio con al menos un `.md` | L4 (`core.decisions.exists`) | Vigente |
| `README.md` índice con ancla; índice coherente con los archivos | L4 | Pendiente F2.5 |
| Frontmatter válido (esquema `adr`), `id` igual al número de archivo | L4 | Pendiente F2.5 |
| Un ADR `aceptada` no cambia de contenido salvo `estado` | L4 (diff en PR) | Pendiente F2.5 (DEBERÍA) |
| La aceptación la hace una persona | L5 (revisión del PR, CODEOWNERS) | Vigente si CODEOWNERS asigna el directorio |

## Criterios de aceptación

1. Cada cambio de arquitectura de los últimos 6 meses se puede rastrear hasta un ADR.
2. Ningún ADR `aceptada` se ha editado para cambiar su decisión.

## Ciclo de vida y evolución

- **Creación:** el ADR 0001 se escribe en la adopción.
- **Actualización:** un ADR por decisión, en el PR que la introduce o antes.
- **Revisión:** al revisar el mapa de arquitectura (semestral), se marcan como `deprecada` las decisiones que ya no aplican.
- **Retirada:** no aplica.
