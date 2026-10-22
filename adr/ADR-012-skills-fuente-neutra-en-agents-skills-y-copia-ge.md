---
id: ADR-012
titulo: "Skills: fuente canónica en `.claude/skills/` con perfil portable; `.agents/skills/` generado solo cuando un adaptador lo necesite"
estado: aprobado
fecha: 2026-10-22
revision: 2
origen: docs/fase-0/03-decisiones-propuestas.md (rev. 1, 2026-10-19); revisado en F3.1 con docs/fase-3/01-verificacion-fuentes.md
---

## ADR-012 · Ubicación y formato de las skills (revisión 2)

> El nombre del archivo se conserva para no romper enlaces. La revisión 1 proponía lo contrario: fuente neutra en `.agents/skills/` y copia generada en `.claude/skills/`.

**Problema.** Las skills son el mecanismo de conocimiento procedimental de menor coste de contexto (unos 100 tokens por skill al inicio, según S-SKILLS). Cada herramienta las busca en directorios distintos. Hay que fijar dónde está la fuente de verdad, qué campos se permiten y cómo se mantiene la portabilidad sin duplicar archivos a mano.

**Hechos (verificados el 2026-10-22, `fase-3/01-verificacion-fuentes.md`)**

| Herramienta | `.claude/skills/` | `.agents/skills/` |
|---|---|---|
| Claude Code | ✅ | ❌ ("anything under a `.agents/` directory" no se lee) |
| GitHub Copilot | ✅ | ✅ |
| Cursor | ✅ (compatibilidad) | ✅ |
| Codex | ❌ | ✅ |
| Gemini CLI | ❌ | ✅ (alias de `.gemini/skills`) |

- Claude Code **ignora sin error** los campos de frontmatter que no reconoce (H3). Lo que hacen las demás herramientas con campos extra **no está verificado**.
- `skills-ref`, el validador de referencia, es una demostración y no está pensado para producción (H4).

**Recomendación**

1. **Fuente canónica:** `.claude/skills/<nombre>/SKILL.md` (más `scripts/`, `references/` y `assets/` opcionales, según S-SKILLS). Una sola copia versionada. La leen Claude Code, Copilot y Cursor.
2. **Dos perfiles de skill**, declarados en su entrada de catálogo (`compatibilidad`):
   - `portable`: solo los campos de Agent Skills (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Es el perfil por defecto.
   - `claude-code`: puede usar además las extensiones de Claude Code (`disable-model-invocation`, `paths`, `context`, `hooks`, `allowed-tools`, etc.). Hay que justificarlo en la ficha. No se copia a otros adaptadores.
3. **`.agents/skills/` no existe en la v1.** Cuando se añada un adaptador que lo necesite (Codex o Gemini CLI), `harness sync` generará copias (no symlinks, por Windows, R-11) **solo de las skills portables**, y la CI fallará si hay deriva.
4. **Validación propia en la CLI** (F3.3) de la especificación de Agent Skills:
   - `name` de 1–64 caracteres, `a-z0-9-`, sin `--`, sin guion inicial ni final, e igual al directorio;
   - `description` de 1–1024 caracteres;
   - `compatibility` de 500 caracteres como máximo;
   - `metadata` de cadena a cadena;
   - perfil coherente con los campos usados;
   - aviso si SKILL.md supera 500 líneas.
5. Las skills son **configuración de agentes**: ya están en `patrones_sensibles` y bajo CODEOWNERS (ADR-013).

**Alternativas descartadas**

| Alternativa | Por qué no |
|---|---|
| Rev. 1: fuente en `.agents/skills/` y copia generada en `.claude/skills/` | Duplica archivos en todas las instancias desde el primer día para beneficiar a Codex y Gemini, que no están en el alcance de la v1. Claude solo vería la copia, y el autor editaría un archivo que su herramienta no lee |
| Symlink `.agents/skills → .claude/skills` | En Windows los symlinks exigen permisos o modo desarrollador, y Git los convierte en archivos de texto si `core.symlinks` es false (inferencia común a R-11). Rompe el clonado en el entorno del usuario |
| Mantener ambos directorios a mano | Deriva garantizada |
| Usar `skills-ref` como validador en CI | Es solo una demostración (H4). Puede usarse en local como comprobación cruzada, no como control |

**Riesgos y supuestos**
- **Supuesto:** Copilot y Cursor toleran las extensiones de Claude Code o no cargan esas skills. No está verificado. Por eso el perfil `portable` es el predeterminado y el perfil `claude-code` se justifica en cada caso.
- **Riesgo (R-01):** Claude Code podría empezar a leer `.agents/skills/`. Se reevalúa en cada revisión trimestral del adaptador.
- **Coste de migración** al añadir Codex o Gemini: bajo, porque basta con generar copias de las skills portables.

**Condición de retirada.** Si Claude Code lee `.agents/skills/` de forma nativa, se mueve la fuente canónica allí y `.claude/skills/` deja de usarse. Lo decide un ADR nuevo.

**Evidencia.** H1–H4 en `fase-3/01-verificacion-fuentes.md`, con URL de la documentación oficial de cada herramienta.

**Validación**
- F3.3: fixtures de skills válidas e inválidas por cada regla de la especificación y por perfil.
- F3.6: la skill semilla `cerrar-tarea` se carga desde `.claude/skills/` en una sesión real de Claude Code del laboratorio.
