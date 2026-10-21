# Auditoría de arquitectura — IMAGE Character Creator (octubre de 2026)

## Esquema actual

- **Interfaz:** `tools/avatar-maker/index.html` concentra HTML, CSS y JavaScript; canvas raster de 768×1280, selector de imágenes, capas, edición manual, guardado/carga JSON, exportación PNG, biblioteca y generador IA.
- **Catálogos:** `assets/catalog.json` mantiene ilustraciones de referencia y capas candidatas con estados de revisión; `assets/image-library.json` indexa los archivos raster del repositorio.
- **Servicios locales:** `ai_edit_server.py` entrega la UI y mantiene las llamadas al modelo de edición de imágenes detrás de una API local `127.0.0.1`; la clave del proveedor solo se lee de `OPENAI_API_KEY`.
- **Generación por lotes:** `generate-hairstyle-variants.yml` ofrece previsualización de recorte sin llamada generativa y paquetes de estilos que producen una rama/PR revisable.

## Hallazgos y cambios aplicados

1. **Piezas raster vs. retratos completos.** El inventario tiene 764 entradas indexadas y 759 marcadas como `full_illustration`. Estas sirven como referencias/base, pero no son 759 peinados ni componentes recortados. La galería ahora las recorre en páginas de 24 y las etiqueta explícitamente como retratos completos con licencia pendiente.
2. **Separación de operaciones de imagen.** La extracción semántica mediante modelo generativo puede reconstruir píxeles ocultos, alterar detalles o mover contornos; por eso sigue siendo un candidato revisable. Se agregó `POST /api/remove-background` con `rembg` local y el modelo `isnet-anime` (alternativa `birefnet-portrait`) para segmentar el personaje sin regenerarlo y sin una llamada generativa. Conserva las dimensiones/posiciones, pero la decontaminación opcional puede ajustar el color RGB de los bordes para reducir halos. La salida debe conservar el tamaño, tener alfa real y quedar pendiente de revisión.
3. **Uso repetido del modelo.** Se cachean sesiones de segmentación por modelo en vez de inicializar la red en cada petición. La inicialización es bajo demanda: instalar el extra es opcional y la primera ejecución puede descargar los pesos.
4. **Seguridad y tolerancia a errores.** El endpoint local restringe host/origen, valida formato y tamaño, limita los píxeles de entrada y no modifica la imagen original. La ausencia del extra devuelve un error controlado con instrucciones.
5. **Regresión.** El validador comprueba sintaxis JavaScript con Node, identificadores HTML, rutas y esquema de catálogos, y ahora verifica la integración del motor y el mínimo de ilustraciones completas. Las pruebas de servicio cubren la salida alfa, dimensiones conservadas, modelo no permitido y la ruta existente de edición API.
6. **Composición no destructiva.** La base se puede ocultar independientemente; su estado persiste en JSON. Al aplicar el recorte de fondo, se oculta automáticamente la base opaca para que no vuelva a cubrir la salida alfa; se puede restaurar en cualquier momento.
7. **Revisión de capas.** Ninguna salida de segmentación se aprueba automáticamente. Deben revisarse el canal alfa, cabello fino, halos, bordes, identidad y alineación. Mantener este estado de candidato protege contra errores de capas y composiciones que se desincronizan.

## Comprobación con inferencia real

La primera inferencia real sobre `from-PixAI-2034984086876227343-0.png` terminó correctamente con `isnet-anime`, conservó 768×1280 y devolvió un canal alfa verificable. La revisión visual encontró un borde claro tenue en algunos mechones sobre fondos muy contrastados, así que el resultado sigue pendiente de aprobación. La matriz de alfa, el análisis visual y el artefacto descargable están documentados en [REAL_CUTOUT_REVIEW_2026-10.md](REAL_CUTOUT_REVIEW_2026-10.md). El flujo mejorado ahora genera previsualizaciones sobre tablero, negro, blanco y magenta y reporta bandas de alfa más útiles.

## Referencias técnicas contrastadas

- [rembg — repositorio upstream](https://github.com/danielgatis/rembg): modelos `isnet-anime` / `birefnet-portrait`, sesiones reutilizables y segmentación local. La licencia de la biblioteca no certifica por sí sola los derechos de cada peso del modelo ni de las imágenes de entrada.
- [Krita 5.3.2.1 — corrección del layer docker](https://planet.kde.org/krita-news-2026-06-02-krita-5-3-2-1-released/): un fallo de capas causaba desincronización y cierres; la lección aplicada aquí es validar cambios de estado y persistencia en lugar de confiar solo en la vista.
- [anime-character-creator — arquitectura](https://github.com/rhedak/anime-character-creator): usa anclajes relativos y orden de capas para mantener consistencia, pero genera dibujos vectoriales. IMAGE mantiene su objetivo raster/anime y no sustituye arte de referencia por geometría genérica.

## Límites actuales

- El recorte local elimina el fondo del personaje completo; **no** separa por sí solo pelo, ojos, ropa y accesorios. Esas operaciones semánticas siguen usando edición generativa y requieren `OPENAI_API_KEY`, pueden costar dinero y requieren comprobación visual.
- El catálogo contiene retratos completos, no una biblioteca masiva validada de piezas intercambiables. Procedencia, licencias y permisos de redistribución/entrenamiento siguen necesitando auditoría individual.
- Los tests automatizados usan una salida de segmentación simulada para comprobar contrato, seguridad y alfa; no certifican la calidad visual real de cada modelo o ilustración.
- La rama de trabajo y PR #19 no quedan integrados en `main` por esta auditoría.
