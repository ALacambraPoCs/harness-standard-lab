---
documento: HS-00
titulo: Alcance, convenciones normativas y terminología
version_estandar: 0.1.0
estado: borrador
fecha: 2026-10-19
adr: [ADR-001, ADR-002]
---

# 00 · Alcance, convenciones normativas y terminología

## 1. Objeto

El Estándar de Harness define cómo debe estructurarse y operarse un repositorio de software para que personas y agentes de IA puedan:

- planificar, implementar, verificar, revisar, integrar y desplegar cambios de forma coordinada;
- verificar automáticamente las partes comprobables;
- auditar el resultado.

## 2. Alcance

**Dentro del alcance**

- Estructura de archivos y metadatos de un repositorio (la *instancia*).
- Contratos de los componentes reutilizables: skills, agentes, hooks, plugins, herramientas y workflows.
- Controles de verificación, integración y despliegue.
- Seguridad de la configuración de agentes.
- Concurrencia entre personas y agentes.
- Gestión del contexto y del coste.
- Gobierno del propio estándar.

**Fuera del alcance**

- La arquitectura interna de las aplicaciones. El estándar exige que los límites que declare un proyecto sean verificables, pero no dicta cuáles deben ser.
- La elección de lenguajes, frameworks o proveedores de modelos.
- La política de uso aceptable de la IA en la organización, salvo en lo que afecte a controles técnicos.

**Ámbito de la versión 1**

| Aspecto | Cubierto en v1 |
|---|---|
| Adaptador de agente | Claude Code |
| Plataforma | GitHub y GitHub Actions |
| Perfiles de repositorio | Greenfield y brownfield grande |
| Monorepo y multi-repo | Reglas mínimas. El tratamiento completo es trabajo futuro |

## 3. Convenciones normativas

### 3.1 Palabras clave

Las palabras clave se interpretan según RFC 2119 y RFC 8174, traducidas al español. Solo tienen valor normativo cuando aparecen en **MAYÚSCULAS**.

| Término | Equivale a | Significado |
|---|---|---|
| **DEBE** | MUST | Requisito absoluto para el nivel de conformidad al que aplica |
| **NO DEBE** | MUST NOT | Prohibición absoluta |
| **DEBERÍA** | SHOULD | Requisito por defecto. Incumplirlo exige un motivo documentado. Cada requisito DEBERÍA indica en qué circunstancias es aceptable no cumplirlo |
| **NO DEBERÍA** | SHOULD NOT | Prohibición por defecto, con las mismas condiciones |
| **PUEDE** | MAY | Opción permitida |

### 3.2 Requisitos

Un requisito es una obligación con un identificador estable `HS-<DOMINIO>-NNN`. Su fuente de verdad es `standard/requirements.yaml`, validado con `schemas/requirement.schema.json`.

El texto en prosa de los documentos `standard/*.md` explica los requisitos y DEBE citar su ID. Si la prosa y el registro discrepan, prevalece el registro, y la discrepancia se corrige como defecto editorial.

| Dominio | Prefijo | Dominio | Prefijo |
|---|---|---|---|
| Instrucciones | `INS` | Componentes | `CMP` |
| Arquitectura y segmentación | `ARC` | Integración y despliegue | `CI` |
| Estado y tareas | `STA` | Observabilidad y métricas | `OBS` |
| Verificación | `VER` | Gobierno y conformidad | `GOV` |
| Concurrencia | `CON` | Seguridad | `SEC` |
| Contexto y coste | `CTX` | | |

### 3.3 Atributos de un requisito

| Atributo | Valores | Significado |
|---|---|---|
| `nivel` | `DEBE`, `NO DEBE`, `DEBERÍA`, `NO DEBERÍA`, `PUEDE` | Fuerza normativa |
| `conformidad` | Subconjunto de `N0`–`N3` | Niveles en los que aplica (ver HS-02) |
| `naturaleza` | `guidance` / `enforcement` | *Guidance* orienta a personas o agentes. *Enforcement* DEBE estar respaldado por un control determinista de capa L4 o L5 (ver HS-01 §5) |
| `verificacion` | `automatica` / `semiautomatica` / `manual` | Cómo se comprueba. Los requisitos `automatica` DEBEN tener al menos una regla en la CLI |
| `exentable` | `true` / `false` | Si admite waiver de instancia |
| `fuentes` | IDs de fuentes o `decision-propia` | Fundamento. Una `decision-propia` DEBE citar un ADR |
| `estado` | `propuesto`, `aprobado`, `deprecado`, `retirado` | Ciclo de vida |
| `retirada` | Texto | Condición en la que el requisito deja de tener sentido |

## 4. Terminología

| Término | Definición |
|---|---|
| **Harness** | Todo lo que rodea al modelo y condiciona su trabajo en un repositorio: instrucciones, herramientas, entorno, estado y retroalimentación. Incluye los controles de CI y de plataforma. |
| **Agente** | Proceso que usa un modelo de lenguaje para decidir y ejecutar acciones con herramientas, por ejemplo Claude Code en local o en CI. |
| **Persona responsable** | Ser humano a cuyo nombre trabaja un agente y que responde de su resultado. Todo trabajo de un agente DEBE tener una persona responsable. |
| **Instancia** | El harness concreto de un repositorio, identificado por `.harness/manifest.yaml`. |
| **Manifiesto** | Archivo `.harness/manifest.yaml`. Declara la versión del estándar, el nivel de conformidad, los adaptadores, los comandos, los roles reubicados y los waivers. |
| **Rol (de archivo)** | Función que cumple un archivo o directorio en la instancia, por ejemplo `instructions.root`. El estándar asigna a cada rol una ruta por defecto. Si el rol es `reubicable`, el manifiesto puede declarar otra. Registro: `standard/roles.yaml`. |
| **Núcleo** | Parte de la instancia expresada en formatos abiertos o propios del estándar, sin dependencia de proveedor. |
| **Adaptador** | Traducción del núcleo a los archivos que exige una herramienta concreta (agente o plataforma). Un adaptador nunca es fuente de una norma. |
| **Adaptador fino** | Archivo de adaptador escrito a mano que solo referencia el núcleo y añade lo exclusivo de la herramienta, por ejemplo `CLAUDE.md` con `@AGENTS.md`. |
| **Artefacto generado** | Archivo producido por la CLI a partir del núcleo. No se edita a mano. La CI comprueba que no haya divergido de su fuente. |
| **Contrato de comandos** | Correspondencia entre roles de comando (`setup`, `check`, `test`…) y su invocación real en el repositorio (ADR-006). |
| **Segmento** | Parte de la codebase con propósito, propietario, dependencias y contratos explícitos, declarada en el mapa de segmentos (ADR-014, Fase 4). |
| **Tarea** | Unidad de trabajo con alcance, criterios de aceptación, propietario y estado, representada por un archivo (ADR-005). |
| **Evidencia** | Prueba verificable de que se cumplió un criterio de aceptación: run de CI, commit o artefacto enlazado. La afirmación del agente no es evidencia. |
| **Nivel de conformidad** | N0–N3. Conjunto acumulativo de requisitos que una instancia declara cumplir (HS-02). |
| **Waiver** | Excepción temporal a un requisito exentable. Lleva motivo, aprobador, fecha de aprobación y caducidad. |
| **Control** | Mecanismo que impide o detecta un incumplimiento. Es **determinista** si su resultado no depende de un modelo de lenguaje. |
| **Guidance / Enforcement** | Orientación probabilística frente a imposición determinista (HS-01 §5). |
| **Entrada no confiable** | Todo contenido que no ha sido revisado por una persona autorizada: issues, comentarios, salidas de herramientas, descripciones de herramientas MCP, documentos externos, la rama de un PR no fusionado. |
| **Clase de riesgo** | Clasificación de un cambio que determina la verificación y la aprobación exigidas (Fase 5). |

## 5. Referencias normativas

| ID | Referencia | Uso |
|---|---|---|
| RFC2119 / RFC8174 | IETF, palabras clave de requisitos | §3.1 |
| S-AGENTSMD | https://agents.md/ (verificado 2026-10-19) | Formato de instrucciones del núcleo |
| S-SKILLS | https://agentskills.io/specification (verificado 2026-10-19) | Formato de skills del núcleo |
| JSON Schema 2020-12 | https://json-schema.org/draft/2020-12 | Esquemas del estándar |
| SemVer 2.0.0 | https://semver.org/ | Versionado |

Las referencias informativas (fuentes T2–T4) se catalogan en `docs/fase-0/01-inventario-y-analisis.md`.
