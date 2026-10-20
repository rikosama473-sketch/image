# IMAGE Character Creator

Editor visual guiado por la referencia compartida: navegación lateral, ilustración grande, galería de miniaturas, capas activas y exportación. La base usa PNG anime reales del repositorio; no dibuja una cara mediante SVG ni figuras geométricas.

## Abrir

- Windows: ejecutá \`start-avatar-maker.bat\` para servir el repositorio localmente y abrir \`http://127.0.0.1:8766/tools/avatar-maker/index.html\`.
- También podés servir la raíz del repositorio con Python y abrir \`tools/avatar-maker/index.html\`.
- [Catálogo de imágenes, fuentes y licencias](assets/catalog.json).

## Implementado

- Seis vistas ilustradas de Pibara: imagen original y cinco variantes completas generadas.
- Galería de nueve máscaras candidatas del repositorio.
- Lienzo de 768×1280, capas PNG/WebP importadas, mover/centrar, escala, opacidad, orden, visibilidad y tono.
- Fondo colorido o transparente, cuatro filtros visuales de previsualización, exportación PNG y proyectos JSON guardables.
- Un diálogo advierte antes de agregar máscaras automáticas. Los estados pendientes de revisión se conservan también en el catálogo.

**Diferencia importante:** seleccionar un retrato de la galería cambia el personaje completo; eso mantiene su aspecto dibujado, pero no es un cambio de cabello aislado. Los recortes semánticos del repositorio aún no fueron aprobados visualmente para anime. Se pueden probar y ajustar, pero no se describen como piezas finales.

## Recursos artísticos de la web

El catálogo registra dos paquetes OpenGameArt cuya página original declara CC0:

- [Anime Girl and Boy Portraits — stevenburrow](https://opengameart.org/content/anime-girl-and-boy-portraits): componentes de retrato, ojos, boca y cabello en una fuente por capas.
- [Visual Novel Style Characters — madameberry](https://opengameart.org/node/54368): imágenes de novela visual, archivos PSD por capas y exportaciones PNG.

La descarga se mantiene fuera del repositorio en \`data/asset-cache/\` hasta revisar las capas. El extractor propuesto conserva el tamaño del lienzo PSD y la ubicación de cada capa para que puedan ensamblarse sin desplazamientos. Los assets de distintos personajes todavía deben compararse visualmente antes de mezclarlos.

## Separación fiable

Para exactitud geométrica, usá la fuente con capas PSD/XCF y exportá cada pieza en un lienzo del tamaño original manteniendo su offset. Cuando solo existe una imagen aplanada, segmentación automática no recupera píxeles ocultos detrás del pelo/ropa ni garantiza bordes impecables. Las máscaras del proyecto siguen marcadas \`pending_visual_review\`; abrí el [editor manual de recortes](../manual-character-editor/index.html) para corregir el borde y reconstruir lo que falta.

El contador de combinaciones es teórico y aumenta con cada opción y pieza independiente cargada. No significa que una máscara beta sea ya una pieza aprobada.
