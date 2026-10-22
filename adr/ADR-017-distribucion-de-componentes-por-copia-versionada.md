---
id: ADR-017
titulo: "Distribución de componentes: copia versionada en la instancia con lockfile y control de deriva"
estado: propuesto
fecha: 2026-10-22
origen: F3.5 (docs/fase-3/PLAN.md)
---

## ADR-017 · Distribución de componentes del catálogo a las instancias

**Problema.** El catálogo central tiene componentes revisados y versionados. Una instancia necesita:
- instalarlos;
- saber qué versión tiene;
- actualizarlos;
- detectar si alguien los ha modificado.

Además, debe poder hacerlo sin perder lo que exigen ADR-013 (la configuración de agentes es código revisado) y ADR-012 (portabilidad de las skills).

**Opciones**

| Criterio | A · Copia versionada (`harness components`) | B · Plugin de Claude Code + marketplace interno |
|---|---|---|
| Revisión en el PR de la instancia | ✅ Los archivos están en el diff y bajo CODEOWNERS | ❌ Solo cambia `enabledPlugins`; el código se descarga fuera del repositorio |
| Funciona con `-p --bare` y en CI | ✅ Son archivos del repositorio | ❌ `--bare` no carga plugins (verificado) |
| Funciona sin confiar en la carpeta | ✅ (las reglas `ask` y `deny` aplican; los hooks también) | ❌ `extraKnownMarketplaces` espera a la confianza; un plugin habilitado solo en el proyecto no se descarga salvo que su fuente sea una ruta relativa (verificado) |
| Portabilidad (Copilot y Cursor leen `.claude/skills/`) | ✅ | ❌ Formato exclusivo de Claude Code |
| Restricciones en subagentes | — | ❌ Los subagentes de plugin ignoran `hooks`, `mcpServers` y `permissionMode` (verificado) |
| Actualización | Manual, por PR (`harness components sync`) | Automática al cambiar la versión del plugin (inmediata y sin revisión en la instancia) |
| Duplicación | Cada instancia tiene su copia | Ninguna |
| Esfuerzo | CLI propia (prototipo en F3.5) | Empaquetar y operar un marketplace |

Fuentes: `fase-3/01-verificacion-fuentes.md` (plugins, headless, settings).

**Recomendación: A, copia versionada.**
1. `harness components add <id>` copia los archivos de la entrada del catálogo (`archivos`) a sus destinos y añade las dependencias (`dependencias`).
   - Fusiona en `.claude/settings.json` el fragmento declarado en `configuracion.claude_settings` (por ejemplo, el bloque del hook `Stop`).
   - Nunca sobrescribe un archivo que no gestiona.
2. `.harness/components.lock` (JSON) registra id, versión, origen (versión del estándar y de la CLI), el SHA-256 de cada archivo y el fragmento de configuración. Está en `.harness/`, una ruta sensible bajo CODEOWNERS.
3. **El catálogo viaja dentro del paquete de la CLI.** Fijar la versión de la CLI (`cli-v…`) fija la del catálogo. Sin red ni token.
4. `harness components sync` actualiza a la versión del catálogo de la CLI instalada **solo si los archivos no se han modificado en local**. Si lo han sido, se detiene: hay deriva.
5. `harness components remove <id>` retira los archivos (si no se han modificado) y el fragmento de configuración.
6. La regla **HS-CMP-009** (en `harness check`) avisa si hay deriva: archivos de componentes modificados o ausentes, o fragmentos de configuración retirados a mano. Cerrar la deriva tiene dos salidas: devolver el componente a su versión o convertirlo en un componente propio, con otro `id` y su ficha.

**Por qué**
- Los componentes son configuración de agentes. Para ADR-013 lo importante es que **cada cambio pase por revisión en el repositorio que los ejecuta**, y B lo saca del repositorio.
- B tampoco funciona en los dos escenarios que el estándar ya exige: CI con `--bare` y carpetas no confiables.
- A cuesta duplicación y actualizaciones manuales. Un PR de `sync` es justo el punto de control deseado.

**Alternativas pendientes**
- B queda como **canal opcional para uso personal** (`~/.claude`) de componentes que no afectan a la conformidad. Se reevaluará si Claude Code permite fijar plugins de proyecto sin confianza ni red.
- Un bot que abra PR de `sync` cuando sale una versión nueva (estilo Dependabot) queda para F7. Dependabot no gestiona este lockfile.

**Riesgos y supuestos**
- Las instancias se quedan en versiones antiguas. Mitigación: `harness components list` muestra lo desactualizado; en F6 se mide la antigüedad.
- La fusión de `settings.json` puede chocar con reglas manuales. Mitigación: la fusión solo **añade** entradas que falten, sin duplicar, y se revisa en el PR.
- Copiar el catálogo en el paquete de la CLI aumenta su tamaño (pocos KB).

**Condición de retirada.** Si un mecanismo nativo de Claude Code (u otro adaptador) permite componentes versionados, revisados en el repositorio y cargados en `--bare` y sin confianza.

**Validación**
- Pruebas automáticas: instalar, comprobar, deriva, sync con y sin modificaciones, remove, dependencias y fusión idempotente de `settings.json`.
- F3.6: el ejemplo greenfield instala los 3 componentes con `harness components add` y la CI comprueba que no hay deriva.
