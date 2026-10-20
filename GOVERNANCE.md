---
estado: borrador
version: 0.1.0
fecha: 2026-10-19
pendiente: Q-01 (composición nominal del grupo de gobierno)
---

# Gobierno del Estándar de Harness

## 1. Roles

| Rol | Responsabilidad | Composición propuesta (Q-01, pendiente) |
|---|---|---|
| **Grupo de gobierno** | Aprueba los cambios normativos (`standard/`, `schemas/`, `adr/`), las versiones MAJOR y MINOR del estándar y las excepciones a requisitos no exentables a nivel organización. | 1 persona de DevEx/plataforma (preside), 1 de seguridad y 2 tech leads de equipos piloto |
| **Mantenedores de la plantilla** | Mantienen la CLI, las reglas, el scaffold y los workflows. Publican versiones de B. | Equipo de plataforma/DevEx |
| **Propietario de instancia** | Responde de la conformidad de su repositorio, declara su nivel y aprueba los waivers locales dentro de los límites del estándar. | Tech lead del repositorio |
| **Contribuidor** | Propone cambios mediante PR o RFC. | Cualquier ingeniero |

Hasta que se resuelva Q-01, los equipos de GitHub de referencia son `@org/harness-owners`, `@org/platform` y `@org/security`. Son nombres genéricos que cada organización sustituye por los suyos.

## 2. Tipos de cambio y proceso

| Tipo | Ejemplos | Proceso | Aprobación |
|---|---|---|---|
| **Editorial** | Erratas, aclaraciones que no cambian ninguna obligación | PR | 1 mantenedor |
| **Normativo menor** | Nuevo requisito DEBERÍA o PUEDE, nuevo rol opcional, nueva regla para un requisito existente | PR con requisito, regla y fixtures | Grupo de gobierno (2 aprobaciones) |
| **Normativo mayor** | Nuevo DEBE, cambio de nivel de un requisito, retirada de un rol, cambio incompatible de esquema | RFC (`docs/rfc/NNNN-*.md`) con un periodo de comentarios de 10 días hábiles, ADR y plan de migración | Grupo de gobierno (mayoría, con seguridad incluida si afecta a SEC o CI) |
| **Plantilla o CLI** | Correcciones, nuevas salidas, rendimiento | PR con tests | 1 mantenedor (2 si cambia el comportamiento de una regla) |

Ninguna decisión de este documento ni de los ADR se considera aprobada sin un registro explícito: estado `aprobado` en el ADR y una entrada en `docs/REGISTRO.md`.

## 3. Versionado

- **Estándar (A):** SemVer en `standard/VERSION`.
  - **MAJOR:** algún repositorio conforme deja de serlo sin cambiar nada, o cambia un esquema de forma incompatible.
  - **MINOR:** nuevos requisitos DEBERÍA o PUEDE, nuevos roles opcionales, o nuevos requisitos DEBE solo en niveles superiores al nivel más alto que declara cualquier instancia afectada.
  - **PATCH:** cambios editoriales.
- **Plantilla y CLI (B):** SemVer propio en `pyproject.toml`. Declara el rango de versiones de A que soporta (`SUPPORTED_STANDARD` en la CLI).
- Las versiones se publican con tags `standard-vX.Y.Z` y `cli-vX.Y.Z`. Mientras el estándar sea `0.x`, cualquier MINOR puede contener cambios incompatibles.

## 4. Deprecación y retirada

- Un requisito o rol pasa por los estados `propuesto` → `aprobado` → `deprecado` → `retirado`.
- Un elemento deprecado se mantiene al menos una versión MINOR, con un aviso de la CLI, antes de retirarse en la siguiente MAJOR.
- Cada requisito declara su condición de retirada (ADR-002). La revisión semestral comprueba si se cumple (ADR-015, pendiente).

## 5. Waivers

- **A nivel de instancia:** los aprueba el propietario de instancia. Se declaran en el manifiesto con aprobador, fecha de aprobación y caducidad, con un máximo de 90 días renovables (ADR-007).
- **Requisitos con `exentable: false`:** solo el grupo de gobierno puede autorizar una excepción, mediante un ADR específico.

## 6. Revisión periódica

- **Trimestral:** se reverifican las capacidades de los adaptadores contra la documentación oficial y se actualizan las fechas de verificación (riesgo R-01).
- **Semestral:** revisión por ablación de requisitos y componentes (ADR-015) y del presupuesto de requisitos por dominio.
