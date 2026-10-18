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
