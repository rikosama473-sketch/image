# IMAGE — generador de imágenes anime con estilo propio

Proyecto privado e independiente para crear un **motor local de generación de imágenes** que aprenda el patrón visual de la colección del usuario. La ruta prioritaria es utilizar un modelo base generativo compatible y entrenar una LoRA propia con ejemplos seleccionados, buscando imágenes nuevas de estilo similar con bajo consumo de recursos.

**No forma parte de WordWaifu ni de CharacterWord.**

## Objetivo vigente

1. Aprovechar las imágenes propias para descubrir qué estilo, prompts, checkpoints y LoRAs se usaron.
2. Curar un conjunto de entrenamiento consistente y revisar la procedencia/permisos.
3. Elegir un modelo base compatible con esas imágenes y el hardware disponible.
4. Entrenar una LoRA propia que aprenda rasgos visuales comunes sin limitarse a memorizar imágenes.
5. Crear una aplicación local para generar y guardar nuevas imágenes con controles reproducibles.
6. Medir memoria, velocidad y calidad; optimizar después de tener una línea base real.

## Decisión técnica

- **No entrenar desde cero como ruta principal.** Una arquitectura pequeña creada con pesos aleatorios no ofrece por sí sola la capacidad de un generador moderno de texto a imagen. La adaptación LoRA es la opción inicial que se debe probar.
- El modelo base y la LoRA deben ser de familias/versiones compatibles. Primero hay que leer los metadatos incrustados en las imágenes; no seleccionar SD 1.5, SDXL u otra familia por intuición.
- `lora_identifiers` y `lora_weights_or_settings` describen la LoRA y la configuración que generaron una imagen cuando se conocen. `lora_target_identifiers` es un campo separado para la LoRA que se quiera probar como destino.
- No se promete reproducción pixel a pixel mediante una LoRA. Para la salida exacta se conserva el archivo original y su hash; para imágenes nuevas, la meta es similitud estilística y control.
- El objetivo antiguo de 2 GB de RAM del sistema no está demostrado y no se debe tratar como garantía para difusión moderna. La memoria del sistema, la VRAM, el tiempo por imagen, el tamaño del modelo y la calidad se medirán por separado.

## Colección existente

El inventario de `main` registra **759 imágenes rasterizadas** (aprox. 706,4 MB): 728 nombres empiezan por `from-PixAI-` y 31 son nombres numéricos. `data/training-labels.csv` conserva las rutas/nombres originales y campos para modelo base, LoRA de origen, configuración y LoRA destino.

El nombre de un archivo es una pista humana, no prueba del checkpoint ni de la LoRA. Las imágenes todavía necesitan revisión visual, de procedencia, contenido y permisos. No se debe entrenar automáticamente con toda la carpeta.

## Primer paso: rescatar los metadatos

Con Python 3.10+ y las dependencias de `requirements.txt`:

~~~bash
python -m pip install -r requirements.txt
python scripts/extract_generation_metadata.py --root .
~~~

El informe se guarda localmente en `data/cache/generation-metadata.csv`, una ruta excluida de Git. Cuando existen metadatos compatibles, el script intenta extraer prompt, prompt negativo, modelo/checkpoint, hash, LoRA, sampler, pasos, CFG y semilla. Los campos que no se encuentren quedan vacíos; **no se adivina la LoRA a partir del nombre**. Revisar el CSV antes de usarlo para decidir el modelo base.

## Auditoría y curación

~~~bash
python scripts/audit_dataset.py --root . --output data/image-audit.csv
python scripts/sync_training_labels.py --root .
~~~

La auditoría reporta dimensiones, modo, transparencia, SHA-256 y un hash perceptual básico. No borra ni cambia originales. Completar las revisiones de contenido, procedencia y entrenamiento en `data/training-labels.csv`. Después:

- agrupar imágenes por checkpoint/LoRA compatible cuando esos datos puedan confirmarse;
- descartar/corregir duplicados y casos inadecuados;
- escribir captions coherentes y seleccionar ejemplos representativos;
- mantener una separación de validación no usada durante el entrenamiento;
- comparar un piloto pequeño con prompts/semillas de prueba antes de ampliar.

La guía detallada está en [docs/DATASET_GUIDE.md](docs/DATASET_GUIDE.md), y la arquitectura y hoja de ruta en [docs/IMAGE_MODEL_STRATEGY.md](docs/IMAGE_MODEL_STRATEGY.md).

## Creador visual de avatares anime

IMAGE Character Creator es un editor basado en ilustraciones PNG reales con navegación lateral, retrato grande, galería de miniaturas, capas activas y exportación. [Abrir el editor](tools/avatar-maker/index.html) · [Guía](tools/avatar-maker/README.md) · [Catálogo y procedencia](tools/avatar-maker/assets/catalog.json).

Incluye seis vistas base de Pibara (la original y cinco variantes completas generadas), composición de capas PNG/WebP, lienzo de 768×1280, fondo/transparencia, posición, escala, opacidad, orden, control de tono y exportación PNG/proyectos JSON. En Windows, ejecuta [start-avatar-maker.bat](tools/avatar-maker/start-avatar-maker.bat).

El catálogo separa **ilustraciones completas** de **máscaras candidatas**. Elegir una variante completa cambia el retrato entero; no se etiqueta como recorte de cabello. Las máscaras automáticas de cabello/cara/cuerpo/ropa siguen pendientes de revisión visual. La meta es ampliar el catálogo de piezas ilustradas alineadas y corregidas.

Se registran bibliotecas CC0 declaradas por sus páginas originales de OpenGameArt. La guía documenta cómo obtener archivos PSD con capas y exportarlos conservando las coordenadas del lienzo. Los recursos externos quedan en caché local mientras se revisan licencia, contenido y compatibilidad.
## Motor de generación local y creador visual

IMAGE ya incluye una primera CLI de inferencia en `ml/generate_diffusion.py` y una pequeña interfaz web local en `tools/image-creator/`. La interfaz permite configurar el modelo base, una LoRA opcional, descripción, prompt negativo, resolución, pasos, semilla, escala y perfil de memoria; muestra los resultados y conserva los parámetros junto a los PNG.

### Ejecutar el creador

Instala PyTorch usando el selector oficial según tu sistema/GPU y después las dependencias opcionales:

~~~bash
python -m pip install -r requirements-diffusion.txt
~~~

Inicia el servidor local:

~~~bash
python ml/local_server.py
~~~

Abre `http://127.0.0.1:8765` en el navegador. En “Modelo base”, indica la carpeta local de un modelo compatible con Diffusers. En “LoRA de estilo”, puedes dejar el campo vacío o indicar una LoRA del mismo tipo de modelo.

El sistema no elige pesos al azar: todavía falta identificar el checkpoint más compatible con tu colección y entrenar nuestra propia LoRA. La casilla de descargas remotas está desactivada por defecto; actívala solo si autorizas al motor a bajar el modelo/LoRA indicado. La generación se ejecuta localmente y la interfaz escucha únicamente en loopback.

Los PNG y archivos JSON asociados se guardan en `outputs/generated/`, ignorados por Git. Este es el primer motor funcional para probar modelos y LoRAs compatibles, no una afirmación de que nuestra adaptación propia ya esté entrenada. CPU puede ser lenta y la meta antigua de 2 GB no está validada.


## Investigación de recursos y licencias

`docs/RESOURCE_HUNT.md` conserva la búsqueda de recursos gráficos y motores de composición como vía complementaria. Los assets descargables no forman parte de nuestro dataset de entrenamiento por defecto: la licencia para usarlos en la aplicación, redistribuirlos y entrenar IA se revisa por separado.

## Principios de seguridad del proyecto

- Mantener las imágenes y los pesos originales sin sobrescritura automática.
- No ejecutar entrenamiento si `training_permission` continúa sin revisar.
- No cargar ni enviar imágenes a un servicio remoto silenciosamente.
- No guardar checkpoints pesados en Git; usar carpetas locales ignoradas.
- No afirmar que una medida de memoria o una calidad se cumplen hasta medirlas.
- Mantener el proyecto separado de WordWaifu y CharacterWord.

## Generación automática de assets sin OpenAI API key

El workflow [Generate character assets without an API key](.github/workflows/generate-character-assets-free.yml) llama la API pública de Gradio del [editor Krea 2 Identity Edit](https://huggingface.co/spaces/conradlocke/krea2-identity-edit). No requiere `OPENAI_API_KEY`. La ejecución programada diaria selecciona el primer paquete incompleto de cada referencia confirmada, guarda el avance aunque el servicio agote su cuota gratuita y continúa en una ejecución posterior. Los límites del servicio público siguen aplicándose; no hay garantía de completar un paquete en una sola ejecución.

Los paquetes actuales cubren cinco peinados, cinco expresiones, cuatro variantes de ojos, cuatro accesorios y cuatro detalles faciales. La ejecución manual acepta una ruta de referencia existente en el repositorio. El único enlace de origen confirmado actualmente es Pibara: `from-PixAI-2034984086876227343-0.png`. El generador rechaza reutilizar ese archivo para Chie o Sunna. La auditoría automática de prompts/metadatos no encontró referencias con sus nombres, así que sus imágenes de origen deben identificarse correctamente antes de ponerlas en cola.

Los assets quedan en `generated/character-assets/<personaje>/...`:

- `base/*-character-cutout.png` y `base/*-alpha-mask.png`: recorte automático del personaje original, sin generación nueva.
- `renders/*.png`: variantes generadas de la ilustración completa.
- `transparent/*.png`: recortes del personaje completo con fondo transparente, no capas aisladas de solo cabello, ojos o accesorios.
- `manifest.json`, `PROMPTS.md` y `contact-sheet.jpg`: procedencia, prompts, parámetros y vista conjunta de las variantes.

Las salidas transparentes aún requieren revisión visual de identidad y bordes. Para un diseñador de personajes verdaderamente por capas todavía hay que aislar y comprobar las regiones individuales (cabello, ojos, accesorios y expresiones); el recorte completo no debe confundirse con una capa independiente de cabello. El flujo anterior de [referencias de peinados](docs/HAIRSTYLE_VARIANT_PIPELINE.md), basado en OpenAI API, permanece como una ruta alternativa opcional y sí requiere `OPENAI_API_KEY`.


## Split source sheets into layered assets

For existing spritesheets, use `scripts/split_sprite_sheet.py` to export individual grid cells or exact pixel-coordinate crops as uniform RGBA PNGs. It writes a contact sheet and a manifest with the source SHA-256, optional license/credit, crop coordinates, output hashes, and alpha statistics. Background removal is optional and only removes a key color connected to the crop border.

The splitter is deterministic: it does not generate alternate hairstyles and cannot separate pixels that overlap in the source. Use boxes that genuinely isolate each hair, eye, expression, or accessory; a full-character cutout is not a semantic layer. See [docs/SPRITE_LAYER_FACTORY.md](docs/SPRITE_LAYER_FACTORY.md) for examples and the optional PyGithub publisher for reviewed output on a feature branch.
