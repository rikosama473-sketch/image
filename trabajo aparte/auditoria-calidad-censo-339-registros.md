# Auditoría de calidad del censo visual — IMAGE
**Fecha de corte:** 22 de octubre de 2026  
**Rama:** `work/interactive-hairstyle-atlas-2026-10`

## Estado cuantitativo confirmado

| Medida | Recuento |
|---|---:|
| Registros / URL canónicas exactas en JSON | 339 |
| Identificadores internos de ficha únicos (tras corrección) | 339 |
| URLs de vista previa registradas | 315 |
| Registros sin URL de vista previa | 24 |
| Registros con título | 339 |
| Registros con autor identificado (no necesariamente verificado contra la fuente) | 339 |
| Registros con `target_traits` | 330 |
| Registros con elementos extra/rojos descritos | 339 |
| Registros con estado de licencia presente | 294 |
| Registros cuya licencia/precio figura como incierto o pendiente | 96 |
| Registros con estado monocromo informado | 335 |
| Placas cuadradas monocromas con permiso de reutilización confirmado | 0 |
| Páginas fuente PixAI registradas según la estadística global | 58 |
| URLs exactas duplicadas en el índice | 0 |
| IDs internos reutilizados que se corrigieron durante QA | 5 |

**Importante:** las vistas previas son URL registradas, no imágenes que se hayan cargado y revisado una por una en el navegador final. El censo visual tiene un fallback de carga; no hubo una prueba real individual de todas las miniaturas. La deduplicación exacta por URL da cero duplicados, pero aún puede haber obras iguales en diferentes plataformas, variaciones del mismo dibujo o varias vistas de una hoja. No se ejecutó hash/perceptual matching de los ficheros originales.

## Cobertura aproximada por grupo de búsqueda

Estas cifras se solapan: un mismo registro puede servir para varias categorías. Se calcularon aplicando las expresiones de búsqueda de la interfaz a categoría, título, características, plataforma y tipo de recurso:

| Componente/familia | Registros que coinciden |
|---|---:|
| Cabello / partes de pelo | 127 |
| Ojos / iris / pestañas | 50 |
| Accesorios | 157 |
| Ropa / vestuario | 152 |
| Tutoriales / guías | 63 |
| Packs / productos descargables | 73 |

No son recuentos de imágenes únicas ni assets recortados. Los hubs de etiquetas, las colecciones editoriales y los productos también pueden coincidir; estas métricas sirven para descubrir material, no como una validación semántica final.

## Problemas de calidad pendientes

1. **24 fichas sin miniatura registrada.** Revisar las de mayor utilidad y no inventar ni asociar miniaturas de otra obra.
2. **96 fichas con licencia/precio incierto o pendiente.** Verificar el texto de la página original. “Libre para ver” y “uso comercial permitido” no significan que se pueda redistribuir el PSD/PNG en IMAGE.
3. **Cero placas 1:1 monocromas reutilizables confirmadas.** Algunas fuentes ofrecen tutoriales en blanco y negro o productos en capas, pero no se confirmó que cumplan simultáneamente aislamiento, proporción cuadrada, fondo limpio, legibilidad y permiso.
4. **Deduplicación visual sin resolver.** URL únicas exactas no prueban ilustraciones distintas; falta comparar miniaturas y hashes perceptuales sobre copias obtenidas legalmente.
5. **Tipos de fuente mezclados.** El censo contiene obras, páginas de tags, tutoriales, colecciones editoriales y anuncios de productos. Una página de colección no equivale a una pieza individual.
6. **Riesgo de fan art.** Las obras de franquicias sirven para estudiar el diseño, pero no son assets originales libres de derechos para comercializar o redistribuir.
7. **Compatibilidad heterogénea.** PSD/PNG en capas, sprites, MMD/VRoid, imágenes de referencia y tutoriales no son intercambiables. Se debe verificar formato y licencia antes de importar a un editor 2D.

## Documentos principales

- **Censo visual interactivo:** [censo-visual-interactivo.html](./censo-visual-interactivo.html)
- **Censo profundo de base:** [censo-exhaustivo-fuentes-waifu-2026-10-21.md](./censo-exhaustivo-fuentes-waifu-2026-10-21.md)
- **Censo de 153 URLs maestras:** [censo-exhaustivo-153-fuentes.md](./censo-exhaustivo-153-fuentes.md)
- **Auditoría específica de accesorios:** [auditoria-accesorios-44-fuentes.md](./auditoria-accesorios-44-fuentes.md)
- **Índice JSON:** [indice-visual-componentes.json](./indice-visual-componentes.json)

## Regla de cierre por ficha

Se considerará lista para producción solo cuando tenga: (a) URL original/autor identificables; (b) miniatura que coincida al abrir el origen; (c) componente objetivo claro; (d) extras ajenos marcados en rojo; (e) licencia acorde con el uso concreto de IMAGE; (f) placa cuadrada monocroma y permiso de uso confirmados cuando se requiera; y (g) deduplicación registrada. El censo actual es una base extensa de investigación; no es todavía una biblioteca terminada de assets reutilizables.

## Corrección de identidad de fichas — 22 de octubre de 2026

Una inspección adicional encontró cinco IDs de la combinación de lotes que se habían reutilizado para páginas distintas. Se cambiaron a identificadores únicos con sufijo `-ALT1`; el JSON conserva `legacy_merged_id` para trazabilidad y el HTML interactivo se sincronizó por URL de origen. Ahora hay **339 registros y 339 IDs internos únicos**, con 0 duplicados exactos de URL. Esto no sustituye la deduplicación visual: páginas distintas todavía pueden mostrar la misma obra o variaciones de una misma hoja.
