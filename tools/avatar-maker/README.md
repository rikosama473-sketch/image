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

El contador de combinaciones es teórico: incluye fondos, retratos base, filtros, opciones de capa y los 361 estados del control de tono (0–360°) en cuatro grupos de capa. Las capas importadas agregan opciones adicionales. No mide cuántas salidas visuales distintas serán buenas; no significa que una máscara beta esté aprobada.


## Edición profesional asistida por IA

La pestaña **IA Studio** permite describir una edición en español, elegir un modelo de imagen y calidad, indicar la dirección artística, adjuntar una imagen de referencia opcional y revisar la salida antes de aplicarla. Incluye un **pincel de máscara** para pintar en rosa la región editable (por ejemplo, solo el pelo); los píxeles fuera de la máscara se protegen según las capacidades del modelo. La máscara se conserva en el proyecto JSON. El resultado entra como una capa PNG sobre el diseño anterior: se puede ocultar, mover, reducir su opacidad o eliminar sin destruir la composición que ya tenías. Guardar el proyecto JSON conserva la imagen generada como dato de capa.

### Requisitos y arranque en Windows

1. Instala Python 3.10 o superior.
2. Crea una clave API en tu cuenta del proveedor si todavía no tienes una; el uso de la API puede generar cargos. ChatGPT Plus/Free no incluye automáticamente saldo para la API.
3. Abre PowerShell desde la carpeta raíz del repositorio y configura la clave solo para esa sesión:

~~~powershell
$env:OPENAI_API_KEY = "TU_CLAVE_API"
.\tools\avatar-maker\start-avatar-maker.bat
~~~

Si no quieres habilitar IA, inicia el lanzador sin configurar esa variable: el creador manual, las capas y la exportación local siguen disponibles. No escribas la clave en HTML, JavaScript, JSON, GitHub, ni en una captura de pantalla. Para quitarla de la sesión actual, ejecuta:

~~~powershell
Remove-Item Env:OPENAI_API_KEY
~~~

El puente se vincula únicamente a 127.0.0.1, lee la clave desde el entorno del proceso y la envía desde Python al endpoint oficial de edición de imágenes. El navegador nunca recibe la clave. Se permiten modelos GPT Image conocidos por la integración y se valida tipo/tamaño de las imágenes antes de enviarlas. La imagen del lienzo y la referencia opcional se envían al proveedor externo elegido; no las envíes si no deseas procesarlas en dicho servicio.

La salida del modelo es una **candidata de edición, no una máscara de cabello garantizada**. La IA puede alterar otros detalles o no recuperar partes ocultas por una imagen aplanada. Revisa cada resultado antes de usarlo y conserva los proyectos JSON originales. La opción de transparencia depende de las capacidades/modelo de imagen disponible.

### Solución de problemas

- **“Falta OPENAI_API_KEY”**: inicia el archivo BAT desde la misma sesión de PowerShell donde configuraste la variable.
- **“Puente de IA no detectado”**: usa el lanzador local, no la vista previa web estática.
- **401/403 del proveedor**: revisa el estado de la clave, permisos, disponibilidad del modelo y cuota de API.
- **Tiempo de espera**: prueba calidad media o baja, y comprueba la conexión.
- **Exportación PNG bloqueada**: usa el lanzador local; las imágenes que el navegador no pueda leer por CORS pueden contaminar el lienzo e impedir la exportación.

Referencia de la integración: [guía oficial de edición de imágenes de OpenAI](https://developers.openai.com/api/reference/resources/images/methods/edit).


## Biblioteca visual del repositorio

La pestaña **Biblioteca** carga \`assets/image-library.json\`, un índice inicial de **759 imágenes rasterizadas preexistentes**; las nuevas generaciones se agregan automáticamente al catálogo. Permite buscar por nombre/ruta, paginar resultados y filtrar por los campos de procedencia, licencia y permiso de entrenamiento. Al elegir una imagen se utiliza como retrato base completo, nunca como cabello u otra capa semántica por defecto.

**Límite de procedencia:** el índice no es una enciclopedia de todo el anime ni prueba que cada imagen esté licenciada. Gran parte de las imágenes tiene procedencia/licencia/permiso sin revisar. Un nombre PixAI o numérico es solo una pista. Antes de publicar, redistribuir o usar para entrenar, revisa el origen real y sus condiciones. Los nuevos packs deben incorporarse con fuente, autor, licencia, hash, estado de revisión y categoría; prioriza bibliotecas con permiso claro y referencias propias.

## Taller anatómico y separación de piezas

La pestaña **Anatomía** tiene dos flujos:

1. **Generar guía anatómica.** Usa la ilustración que está en el lienzo como referencia y solicita una ficha de cuerpo entero en pose A, con proporciones y articulaciones legibles. Hay una variante tipo maniquí de estudio. La salida se revisa en IA Studio y se agrega como capa separada; no sustituye la ilustración original. Requiere la clave API local y puede generar cargos.
2. **Separar regiones manualmente.** Activa el pincel rosa, pinta dentro de la región que quieras extraer y pulsa **Crear capa separada**. El programa recorta mediante una máscara alfa y conserva el lienzo completo de 768×1280, incluido el origen superior izquierdo. Selecciona la nueva capa y pulsa **Exportar capa seleccionada** para guardar su PNG transparente alineado.

Para sacar piezas del arte original, oculta primero la guía anatómica y cualquier otra capa superpuesta. Pinta dentro de la silueta con un pincel pequeño en los bordes. Este es un flujo de selección manual asistida; no es un segmentador semántico automático. Si el fondo del retrato es opaco, los píxeles incluidos en la zona pintada también se conservan: revisa el PNG exportado y elimina los restos antes de aprobar la pieza.

La exportación individual conserva coordenadas, por lo que las piezas pueden recomponerse en el editor. No existe todavía garantía de segmentación perfecta de cabello/ojos/ropa en el inventario ni en las nuevas imágenes; cada pieza extraída queda pendiente de revisión.

## Modelos y controles API

Los nombres GPT Image 2.5 Sunburst y Flare, GPT Image 2 y GPT Image 1.5 se mantienen en el selector. La llamada utiliza el endpoint oficial de edición, una entrada por imagen base y una imagen de referencia opcional. La máscara transparente solo se envía cuando hay trazos. Consulta la documentación oficial de [edición de imágenes](https://developers.openai.com/api/reference/resources/images/methods/edit) para disponibilidad, límites y compatibilidad de los modelos.


### Resultado anatómico generado en el repositorio

La primera ejecución automatizada para Pibara completó el paquete \`anatomy-guide-1\` en GitHub Actions. Consulta los archivos en la carpeta [run-39496066089](../../generated/character-assets/pibara/2026-10-20/run-39496066089/):

- \`renders/01-full-body-anatomy-a-pose.png\` — render de referencia.
- \`transparent/01-full-body-anatomy-a-pose.png\` — versión con fondo quitado para el editor.
- \`manifest.json\` — prompt, modelo público, dimensiones, hashes y estado de revisión.

El manifiesto marca la guía como pendiente de revisión visual. La máscara alfa se generó correctamente por métricas, pero revisa contorno, rostro, manos, pies y proporciones antes de usarla como referencia definitiva.
