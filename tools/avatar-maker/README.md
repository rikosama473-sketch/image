# KIRA — creador fácil de personajes

KIRA es un creador 2D sencillo, de un solo archivo HTML, para construir un avatar mediante opciones visuales. La ilustración vectorial se dibuja por capas y se actualiza al instante; no requiere IA, GPU, paquetes ni conexión a Internet para usar las opciones incorporadas.

## Abrirlo

- Abre `tools/avatar-maker/index.html` en Chrome, Edge o Firefox.
- Elegí un peinado y una ropa; cambiá los ojos, colores, accesorios y fondo en las pestañas.
- Pulsá **Sorpréndeme** para una combinación aleatoria.
- Descargá el resultado como PNG de alta resolución o como SVG.
- Guardá el diseño en JSON para seguir editándolo más adelante.

## Usar piezas de tu biblioteca

El repositorio contiene muchas ilustraciones completas, pero eso no significa que cada archivo sea una pieza aislada y alineada. KIRA no las convierte automáticamente en cabello o ropa: así se evita cortar píxeles incorrectos sin avisar.

Para incorporar piezas propias, primero extraé cabello, ropa o accesorios como PNG/WebP con fondo transparente usando el editor manual en `tools/manual-character-editor/`. En KIRA elegí **Cargar pieza PNG**. Después seleccioná el orden de la capa (cabello trasero, sobre ropa, sobre cabello o por encima de todo), y movela con el mouse o ajustá X/Y, tamaño y opacidad.

Los diseños exportados conservan los archivos importados dentro de su JSON de proyecto. Las ilustraciones originales del repositorio no se modifican. Los archivos elegidos en tu computadora se procesan localmente en el navegador.

## Qué incluye

- 9 peinados, 5 flequillos, 6 formas de ojos, 5 bocas, 8 vestimentas y 9 accesorios.
- Controles visuales para color de cabello, piel, ojos, ropa y fondo.
- Estilos visuales Anime, Chibi, Manga y Pastel.
- Fondo decorado o transparente.
- Piezas PNG/WebP propias, movibles y con control de capa, escala y opacidad.
- Descarga PNG/SVG y guardar/abrir proyectos JSON.

## Límites conocidos

Esta primera versión usa una ilustración vectorial modular original como base; no intenta afirmar que las 759 imágenes de referencia ya sean piezas separadas. Los estilos cambian rasgos y acabado de la misma base vectorial, no transforman automáticamente cualquier imagen subida a un estilo nuevo. El resultado está diseñado para ser fácil de usar y ampliable con assets compatibles, no sustituye un editor de ilustración completo.
