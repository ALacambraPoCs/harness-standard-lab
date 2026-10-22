# Catálogo de componentes del harness

Modelo, tipos, contrato y ciclo de vida: [`standard/05-componentes/00-modelo.md`](../standard/05-componentes/00-modelo.md).
Esquema de entrada: [`schemas/catalog-entry.schema.json`](../schemas/catalog-entry.schema.json).
Plantilla de ficha: [`standard/05-componentes/_PLANTILLA-FICHA.md`](../standard/05-componentes/_PLANTILLA-FICHA.md).

Estructura: `catalog/<tipo>/<id>/{componente.yaml, FICHA.md, src/, tests/}`.

<!-- harness:indice -->
<!-- generado:catalogo:inicio (harness catalog index --write) -->
| Id | Tipo | Estado | Versión | Control | Título |
|---|---|---|---|---|---|
| [verificar-al-terminar](hook/verificar-al-terminar/FICHA.md) | hook | experimental | 0.2.0 | no | No dar el trabajo por terminado si check o las tareas fallan |
| [cerrar-tarea](skill/cerrar-tarea/FICHA.md) | skill | experimental | 0.1.0 | no | Cerrar una tarea en el PR que la completa (ADR-016) |
| [verificador](subagente/verificador/FICHA.md) | subagente | experimental | 0.1.0 | no | Verificación independiente de la tarea en curso |
<!-- generado:catalogo:fin -->

Los componentes nuevos entran como `experimental` (ADR-015); el paso a `estable` exige evidencia de uso (`standard/05-componentes/00-modelo.md` §5).
