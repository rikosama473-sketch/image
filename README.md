# IMAGE — estudio modular de creación de personajes e ilustración anime

> **AVISO: el proyecto principal ahora es [KIRA Atelier — Anime Character Studio](https://github.com/rikosama473-sketch/KIRA-Atelier).**
>
> La edición actual, el Atlas visual, el taller de peinados, la preparación de capas y los módulos auxiliares se centralizan en **KIRA Atelier**. Este repositorio se conserva temporalmente como **archivo de origen y respaldo**, no como destino principal de nuevas funciones. Los originales aquí guardados no se borraron; cualquier trabajo nuevo debe comenzar en KIRA Atelier y cualquier transferencia adicional debe verificarse antes de retirar este respaldo.


IMAGE es un estudio local y modular para **buscar referencias, componer personajes anime, separar y editar capas, guardar proyectos, crear variantes y, de forma opcional, generar o editar imágenes mediante IA**. La biblioteca, el constructor, el editor 2D y el motor de generación son módulos relacionados de un mismo producto; ninguno sustituye a los demás.

La identidad del proyecto no es la de un simple generador ni la de un archivador. Las funciones manuales deben seguir disponibles aunque no haya modelos de IA instalados, conexión remota o GPU dedicada.

## Objetivo y hardware

El equipo objetivo de desarrollo es AMD Ryzen 5 5600G, 16 GB de RAM y gráficos Radeon integrados, sin GPU dedicada. El constructor y los editores 2D no dependen de difusión. El motor de IA local es opcional y su rendimiento no se considera validado en ese hardware hasta medir tiempo, memoria y estabilidad con un modelo concreto.

IMAGE preserva los originales y distingue entre una ilustración completa, una máscara candidata, un recorte transparente y una capa semántica realmente aislada. Que una imagen tenga una etiqueta no garantiza que exista el recurso como PNG, que el recorte sea limpio ni que haya permiso para redistribuirlo o entrenarlo.

## Módulos del estudio

- **Constructor de personajes:** `tools/avatar-maker/index.html`. Combina ilustraciones y capas, ofrece transformaciones y ajustes visuales, administra variantes y proyectos JSON, y puede enviar una petición de edición IA solo cuando se ejecuta esa acción y está configurado el proveedor.
- **Biblioteca visual:** `tools/visual-reference-library/index.html`. Reúne imágenes locales y referencias enlazadas, permite buscar/clasificar, anotar procedencia y revisión, guardar recetas visuales y exportar anotaciones. Una receta es una especificación, no una imagen nueva.
- **Taller manual de peinados:** `tools/hairstyle-workbench/index.html`. Compone piezas PNG existentes, permite manejar variantes y exportar composiciones; no inventa los píxeles que estaban ocultos por otra capa.
- **Editor manual de capas:** `tools/manual-character-editor/index.html`. Ofrece selecciones, máscara manual, recorte, borrado/restauración, extracción de regiones y exportación PNG sin subir imágenes a un servicio remoto. Importa JSON del Constructor (si registra la imagen base) y del Taller de peinados; rasteriza la geometría en capas editables y guarda la procedencia. Se rechazan URL externas y rutas inseguras.
- **Generador local de imágenes:** `tools/image-creator/index.html`, servido por `python ml/local_server.py` en `http://127.0.0.1:8765`. Usa un modelo compatible que el usuario proporciona/configura; no presupone que exista uno instalado ni que la IA local sea viable con rapidez aceptable.

## Puesta en marcha

En Windows, inicia `tools/avatar-maker/start-avatar-maker.bat`. El servidor local de herramientas escucha en `127.0.0.1:8766` y permite abrir el constructor, la biblioteca, el taller de peinados y el editor manual desde una navegación compartida. Si abres el editor manual con su lanzador independiente, los enlaces de otros módulos también resuelven desde la raíz del repositorio, en un puerto local temporal.

El generador de difusión es un servidor aparte: ejecuta `python ml/local_server.py` tras instalar las dependencias opcionales apropiadas. No requiere una GPU dedicada para abrir el resto de IMAGE. Para la edición generativa mediante proveedor externo, la clave se lee desde el entorno y no debe guardarse en el HTML ni en un proyecto. No se envían imágenes a un servicio remoto en segundo plano.

## Estado honesto de las funciones

El repositorio contiene varias herramientas operativas, pero IMAGE no debe declararse consolidado solo porque existan pantallas o porque un botón esté presente. La apertura/guardado, exportación PNG, persistencia de capas, respuesta de cada motor y compatibilidad con el hardware deben validarse con pruebas y recorridos reales. Las capas generadas o segmentadas permanecen candidatas hasta revisar visualmente sus bordes, identidad y alineación.

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

Incluye seis vistas base de Pibara (la original y cinco variantes completas generadas), composición de capas PNG/WebP, lienzo de 768×1280, fondo/transparencia, posición, escala, opacidad, orden, control de tono y exportación PNG/proyectos JSON. La pestaña IA Studio añade edición por instrucciones, referencias opcionales y resultados revisables como capas, mediante un puente local que mantiene la clave API en una variable de entorno. En Windows, ejecuta [start-avatar-maker.bat](tools/avatar-maker/start-avatar-maker.bat) y consulta la [guía de edición IA](tools/avatar-maker/README.md#edición-profesional-asistida-por-ia).

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


## IMAGE Character Creator: anatomy and image library

The avatar maker now includes an **Anatomía** workspace for generating a full-body anime anatomy guide from the selected canvas reference, manually painting regions, creating transparent full-canvas PNG layers, and exporting each selected layer while preserving its original coordinates. The **Biblioteca** workspace starts from the 759-image repository inventory and appends generated outputs to the searchable catalog, with provenance/license/training-review status kept separate.
The workflow now offers **`anatomy-sheet-4`**, one repository run for four separate full-body references: front A-pose, side profile, back view, and joint landmarks. Each generated output is stored separately with a manifest and transparent cutout where the service succeeds.

The index is a local repository inventory, **not every anime character worldwide and not blanket permission to reuse those images**. Many image sources and rights are still unreviewed. Check provenance before sharing or training on assets. A generated anatomy sheet is a reference layer, not a guaranteed segmentation of the original artwork. See [the avatar maker setup and anatomy guide](tools/avatar-maker/README.md).


### Primera guía anatómica generada dentro del repositorio

La ejecución gratuita de GitHub Actions **39496066089** terminó correctamente para Pibara. Los enlaces siguientes fueron verificados contra archivos existentes en un commit inmutable; no dependen de cómo GitHub resuelva el nombre de una rama.

- [Ver PNG generado (fondo original)](https://github.com/rikosama473-sketch/image/blob/0efede21e292909395d617df0bf6acb861e2cdb8/generated/character-assets/pibara/2026-10-20/run-39496066089/renders/01-full-body-anatomy-a-pose.png)
- [Ver PNG transparente para el editor](https://github.com/rikosama473-sketch/image/blob/0efede21e292909395d617df0bf6acb861e2cdb8/generated/character-assets/pibara/2026-10-20/run-39496066089/transparent/01-full-body-anatomy-a-pose.png)
- [Ver hoja de contacto](https://github.com/rikosama473-sketch/image/blob/0efede21e292909395d617df0bf6acb861e2cdb8/generated/character-assets/pibara/2026-10-20/run-39496066089/contact-sheet.jpg)
- [Manifiesto, dimensiones, hashes y procedencia](https://github.com/rikosama473-sketch/image/blob/0efede21e292909395d617df0bf6acb861e2cdb8/generated/character-assets/pibara/2026-10-20/run-39496066089/manifest.json)
- [Prompts usados](https://github.com/rikosama473-sketch/image/blob/0efede21e292909395d617df0bf6acb861e2cdb8/generated/character-assets/pibara/2026-10-20/run-39496066089/PROMPTS.md)
- [Ver ejecución de GitHub Actions](https://github.com/rikosama473-sketch/image/actions/runs/39496066089)

Ambos PNG conservan el lienzo de **768×1280**. La salida transparente registra aproximadamente un 67 % de píxeles transparentes y no tiene advertencia automática de calidad del recorte. Eso valida las métricas alfa, no la fidelidad anatómica ni el parecido. La identidad sigue marcada como pendiente de revisión visual.


### Lote anatómico de cuatro vistas — ejecución parcial

El paquete \`anatomy-sheet-4\` guardó tres vistas en el repositorio antes de que el servicio público agotara la cuota. Cada enlace siguiente apunta a un archivo verificado en el commit inmutable \`745404b7e5d5\`, por lo que no depende de la rama actual:

- [Abrir galería con las tres vistas y PNG transparentes](https://github.com/rikosama473-sketch/image/blob/daac2bf07e295bb7aac1484618b277312e25861f/generated/character-assets/pibara/2026-10-20/run-39500149462/ANATOMY-GALLERY.md)
- [Vista frontal generada (borrador recortado)](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/renders/01-batch-front-a-pose.png)
- [Vista frontal PNG transparente](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/transparent/01-batch-front-a-pose.png)
- [Vista lateral de cuerpo entero](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/renders/02-batch-side-profile.png)
- [Vista lateral PNG transparente](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/transparent/02-batch-side-profile.png)
- [Vista trasera de cuerpo entero](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/renders/03-batch-back-view.png)
- [Vista trasera PNG transparente](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/transparent/03-batch-back-view.png)
- [Hoja de contacto con las tres vistas](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/contact-sheet.jpg)
- [Manifiesto: 3/4 vistas, cuota y revisión](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/manifest.json)
- [Prompts usados](https://github.com/rikosama473-sketch/image/blob/745404b7e5d516434ef9c5782cc1ba893631a828/generated/character-assets/pibara/2026-10-20/run-39500149462/PROMPTS.md)
- [Ejecución de GitHub Actions](https://github.com/rikosama473-sketch/image/actions/runs/39500149462)

La vista frontal **no cumple la pose A solicitada**: las piernas están recortadas y un brazo está levantado. Perfil y espalda son de cuerpo entero, pero las tres vistas se apartan de la identidad visual de Pibara (cabello, ojos o vestuario). El manifiesto y la biblioteca lo registran. Son borradores anatómicos, no modelos canónicos aprobados.


### Reanudar la vista anatómica que falta

El paquete \`anatomy-sheet-4\` produjo tres vistas y preservó los archivos cuando el Space público agotó la cuota. La cola diaria se ha ajustado para priorizar primero los paquetes anatómicos pendientes y la conexión opcional admite \`HF_TOKEN\` como secreto de GitHub Actions.

Para dar más cuota al generador público sin poner credenciales en el código:
1. Crea un token de Hugging Face con los permisos mínimos que requiera el Space.
2. En GitHub abre **Settings → Secrets and variables → Actions → New repository secret**.
3. Usa exactamente el nombre \`HF_TOKEN\` y guarda el valor directamente en GitHub. **No lo escribas en el código, en el JSON de cola ni en este chat.**
4. Después de guardar el secreto, lanza la acción desde la rama \`work/easy-avatar-maker-2026-10\` con \`asset_pack=anatomy-sheet-4\`. El selector de la cola reconoce los tres archivos ya creados y solo debe intentar generar el cuarto que falta, si el servicio acepta la cuota.

La autenticación opcional ya está cableada; no puedo afirmar que está activa hasta que el secreto exista en la configuración del repositorio. El flujo de generación parcial actual se puede consultar en [Actions #39500149462](https://github.com/rikosama473-sketch/image/actions/runs/39500149462).
