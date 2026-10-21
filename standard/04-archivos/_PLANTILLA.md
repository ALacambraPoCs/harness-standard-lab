---
# Plantilla de ficha de archivo. Copiar como standard/04-archivos/<rol>.md.
# Validado por schemas/ficha.schema.json. Ruta, tipo, obligatoriedad, nivel y capa
# se leen de standard/roles.yaml (no se repiten aquí: fuente única).
rol: <rol>
titulo: <Nombre legible del archivo>
estado: borrador
version: 0.1.0
consumidores: [agentes, personas, ci, cli]
dependencias: []           # roles referenciados
propietario: <rol organizativo en la instancia, p. ej. "tech lead del repositorio">
requisitos: []             # HS-… que lo regulan (o "pendiente:F2.5")
reglas: []                 # reglas de la CLI que lo validan
ejemplo_canonico: template/core/<ruta>
fuentes: []                # IDs de fuentes (F0-01) o decision-propia + ADR
evolucion: >-
  MAJOR si cambia el rol, la ruta por defecto o un elemento obligatorio; MINOR si se añade un
  elemento opcional; PATCH si es editorial.
---

# <Nombre del archivo>

> Ruta, obligatoriedad, nivel y capa: ver `standard/roles.yaml#<rol>` (vista resumida en
> `03-estructura-canonica.md`).

## Propósito
Una o dos frases: qué problema resuelve y para quién.

## Contenido requerido
Elementos obligatorios, cada uno con su **ancla verificable** (clave de frontmatter, encabezado
marcado con `<!-- harness:<ancla> -->` o campo de esquema) y el requisito que lo exige.

| Elemento | Ancla | Requisito | Verificación |
|---|---|---|---|

## Contenido recomendado y opcional

## Contenido excluido
Qué NO debe contener y dónde debe ir en su lugar.

| No incluir | Va en |
|---|---|

## Formato y convenciones
Formato, tamaño o presupuesto, idioma (libre, D-020), enlaces y estilo.

## Ejemplo canónico
Ejemplo mínimo completo (o enlace a `ejemplo_canonico`).

## Validaciones
Reglas automáticas, comprobaciones manuales y en qué capa (L1–L5) se imponen.

## Criterios de aceptación
Lista verificable para considerar el archivo conforme en una instancia.

## Ciclo de vida y evolución
Creación, quién lo actualiza y cuándo, revisión periódica y condición de retirada.
