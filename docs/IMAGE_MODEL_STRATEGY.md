# Estrategia del modelo generador de IMAGE

**Objetivo vigente:** crear un generador local de imágenes que aprenda el patrón visual de la colección propia y produzca imágenes nuevas similares en estilo y aspecto, con recursos medidos y lo más bajos posible.

IMAGE es independiente de WordWaifu y CharacterWord.

## Las tres piezas del sistema

1. **Modelo base:** la red generativa completa. Aporta la capacidad general de entender descripciones y sintetizar imágenes.
2. **LoRA propia:** adaptación compacta entrenada con un subconjunto curado de nuestras imágenes para aproximarse al estilo visual buscado. No es un generador independiente; debe coincidir con una familia y versión compatibles del modelo base.
3. **Motor/creador de imagen:** aplicación local que carga el modelo base y la LoRA, ofrece descripción, semilla, dimensiones, intensidad de adaptación, generación de variantes, guardado y una futura comparación lado a lado.

La prioridad es adaptar un modelo generativo ya entrenado, no aprender toda la capacidad de generación desde pesos aleatorios. Las guías oficiales de Diffusers describen el entrenamiento LoRA como entrenamiento de un número reducido de pesos y muestran cómo aplicar después esos pesos a un modelo base. También advierten que puede haber sobreajuste:
- [Hugging Face Diffusers: LoRA training](https://huggingface.co/docs/diffusers/training/lora)
- [Hugging Face Diffusers: SDXL training and memory notes](https://huggingface.co/docs/diffusers/training/sdxl)

## Motor de inferencia inicial

La primera CLI reutilizable está en `ml/generate_diffusion.py`. Acepta una carpeta/identificador de un modelo Diffusers y una LoRA opcional, genera las salidas de forma secuencial para no disparar el consumo por lotes, y guarda los parámetros al lado de cada PNG. De manera predeterminada opera con archivos/cache local y requiere `--allow-download` para autorizar descargas.

Para instalar las dependencias opcionales, instala primero PyTorch adecuado al equipo y después usa `python -m pip install -r requirements-diffusion.txt`. La CLI aún no elige un checkpoint ni entrena la LoRA: esas decisiones dependen de recuperar los metadatos y revisar el hardware y los permisos.

## Primera decisión técnica: rastrear lo que ya generó las imágenes

El inventario actual registra 759 imágenes, de las que 728 tienen un nombre que empieza por `from-PixAI-`. El nombre se conserva, pero no prueba qué modelo, LoRA o configuración se utilizó.

Antes de escoger un checkpoint:
1. Ejecutar `python scripts/extract_generation_metadata.py --root .`.
2. Revisar `data/cache/generation-metadata.csv` localmente para identificar prompts, modelo/checkpoint, hashes, LoRAs, pesos, sampler y semilla cuando existan metadatos embebidos.
3. Cruzar lo extraído con `data/training-labels.csv`, conservando separados el modelo/LoRAs que produjeron la imagen y la LoRA destino.
4. Si hay varias familias de checkpoints, agrupar por compatibilidad/procedencia y comparar pilotos por grupo. No mezclar ciegamente imágenes de bases incompatibles para entrenar una sola LoRA.
5. Si no hay metadatos, dejar los campos vacíos y etiquetar manualmente solo lo que se pueda confirmar.

## Entrenador LoRA integrado (primer flujo local)

El nuevo ml/train_lora.py usa los scripts oficiales de texto-a-imagen de Diffusers v0.35.1 para las familias StableDiffusionPipeline (SD 1.x/2.x) y StableDiffusionXLPipeline. Los scripts se descargan solo tras ejecutar el comando explícito --fetch-official-trainers y se verifican contra sus Git blob SHA conocidos. La descarga de pesos base queda separada; la inferencia y el entrenamiento siguen siendo locales por defecto.

Pasos reproducibles:

1. Ejecutar el extractor de metadatos y luego scripts/summarize_generation_metadata.py. El resumen informa cobertura e identificadores de modelo/LoRA y omite deliberadamente los textos de prompt.
2. Crear la plantilla de captions con python ml/train_lora.py --make-caption-template; rellenar captions revisados y revisar visual_review, license_review y training_permission en el manifiesto.
3. Instalar PyTorch y torchvision compatibles como pareja para el equipo, y luego requirements-training-lora.txt.
4. Obtener los entrenadores fijados mediante python ml/train_lora.py --fetch-official-trainers.
5. Ejecutar la prevalidación con --check-only. Se exige confirmar la familia del dataset y el modelo local se identifica por el campo _class_name de model_index.json. Los identificadores de origen desconocidos o múltiples bloquean el entrenamiento hasta que se revisen o se autoricen explícitamente.
6. Quitar --check-only para iniciar el entrenamiento. Por defecto se utiliza batch size 1, acumulación de gradiente 4, gradient checkpointing, checkpoints locales y precisión elegida a partir de la disponibilidad CUDA. Sin CUDA se usa precisión completa y el proceso advierte que el entrenamiento en CPU puede ser muy lento.
7. Revisar el estado y el artefacto final en outputs/training-lora/. El lanzador no declara éxito por el código de salida solamente: requiere el archivo pytorch_lora_weights.safetensors y comprueba que se puede leer y contiene claves LoRA.

La preparación genera un ImageFolder temporal usando enlaces simbólicos o enlaces duros, con copia como último recurso. Los originales no se renombran ni alteran. El informe de entrenamiento conserva la lista de rutas seleccionadas y hashes de captions, mientras que los prompts y datos de trabajo permanecen locales. Los ejemplos de validación quedan excluidos del entrenamiento y registrados para una comparación posterior; no existe aún una puntuación automática de similitud ni una evaluación visual automática de ese conjunto.

## Piloto de estilo

- Auditar tamaños, transparencia, errores, duplicados exactos y cercanos, contenido y procedencia.
- Seleccionar un conjunto pequeño, representativo y permitido para entrenamiento. No entrenar automáticamente con las 759 imágenes.
- Separar ejemplos de validación que no participen en el entrenamiento.
- Escribir captions útiles: sujeto y rasgos visibles que deben variar, sin inventar información sobre el origen.
- Probar un token único para el estilo propio y evaluar si la LoRA aprende trazos, paleta, sombreado, proporciones y acabado sin memorizar cada imagen.
- Comparar antes/después con las mismas descripciones, semillas y configuración; revisar ejemplos conocidos y prompts no vistos.
- Guardar por experimento: modelo base y revisión/hash, versión del trainer, manifiesto del conjunto, configuración, semilla, logs, LoRA y ejemplos de validación.

## Recursos y honestidad sobre el hardware

- El ahorro principal proviene de adaptar una base preentrenada con LoRA, no de entrenar desde cero. Aun así, entrenar una LoRA y ejecutar inferencia son cargas diferentes: entrenar en CPU suele ser muchísimo más lento.
- No elegir SD 1.5, SDXL, Flux u otra familia por moda: primero recuperar metadatos del checkpoint original. Si no se puede confirmar la familia, SD 1.5 queda como candidato de prueba de bajo consumo, no como decisión de procedencia.
- La RAM reservada para una APU integrada no es una tarjeta de vídeo dedicada ni garantiza soporte del backend. En el motor Diffusers actual, la selección GPU implementada es CUDA/MPS; una Radeon integrada en Windows suele acabar en CPU, salvo que se configure un backend explícitamente compatible.
- No prometer 2 GB de memoria total. Medir por separado RAM de sistema, memoria compartida/UMA, tiempo por imagen, tamaño de modelo en disco y calidad visual.
- Mantener una generación a la vez, 512×512 como tamaño de prueba, 12 pasos como punto de partida, precisión automática y optimizaciones de memoria. Este perfil reduce el trabajo de la primera prueba; no garantiza que cualquier modelo quepa o sea rápido.
- Antes de entrenar en esta PC, terminar inventario, metadatos y permisos. No iniciar un entrenamiento con las 759 imágenes por defecto ni gastar recursos en una LoRA antes de probar que la base puede generar una imagen aceptable.
- Se evaluará como alternativa local `stable-diffusion.cpp`: sus fuentes oficiales documentan soporte de SD 1.x, LoRA, formatos SafeTensors/GGUF y backends CPU/Vulkan. Esto lo convierte en candidato para probar la Radeon integrada, no en un resultado ya validado para la APU concreta. Primero se debe obtener/compilar el binario explícitamente, identificar el modelo compatible y medir una salida 512×512 antes de integrarlo como backend.
- Fuentes técnicas:
  - [Diffusers: optimización de memoria](https://github.com/huggingface/diffusers/blob/main/docs/source/en/optimization/memory.md)
  - [stable-diffusion.cpp: README, modelos y backends](https://github.com/leejet/stable-diffusion.cpp)
  - [stable-diffusion.cpp: selección de backend y memoria](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/backend.md)
- No comprometer checkpoints ni derivados pesados en Git. Mantenerlos en directorios locales ignorados y registrar instrucciones y versiones.

## Perfil inicial para PCs con recursos limitados

1. **Primer objetivo: inferencia, no entrenamiento.** Probar una sola imagen a 512×512 y 12 pasos, modelo compatible local ya disponible, sin LoRA al principio. Registrar el tiempo y observar el uso máximo de RAM. No descargar pesos automáticamente.
2. **Motor Diffusers existente:** empezar con CPU y el perfil de bajo consumo de la interfaz; no activar FP16 manualmente en CPU sin comprobar compatibilidad. El modo automático de este motor no descubre Vulkan para AMD.
3. **Candidato para aceleración AMD:** probar `stable-diffusion.cpp` por separado con CPU y Vulkan, si el driver y el binario lo permiten. El test solo cuenta como exitoso si se guarda un PNG real y se registran tiempo, modelo, backend y parámetros. No asumir que Vulkan será más rápido ni estable hasta medirlo.
4. **Selección de base:** preferir la familia que demuestren los metadatos de la colección. Solo si no se recupera esa información, realizar un piloto comparativo con un checkpoint SD 1.5 ligero y con licencia compatible; no usar SDXL/Flux como primera prueba de bajo consumo sin una razón basada en datos.
5. **LoRA:** primero curar un subconjunto pequeño autorizado, con captions y validación. No correr entrenamiento completo en CPU como siguiente acción automática. Evaluar tiempo, memoria y calidad antes de decidir si entrenar localmente o preparar un entorno de entrenamiento distinto.
6. **Criterio de avance:** anotar RAM máxima, tiempo por imagen, tamaño en disco, calidad visual revisada y si hubo errores. Ninguna optimización queda aprobada por intuición o por CI.

## «Exacta» versus «similar»

- Para reproducir exactamente un archivo ya generado, conservar el archivo original y su huella, además de los parámetros si existen. La semilla por sí sola no garantiza identidad entre versiones o motores.
- Una LoRA estilística busca semejanza visual y capacidad de producir nuevas composiciones; no promete reconstruir píxeles exactos de imágenes arbitrarias.
- Más adelante puede añadirse img2img o referencia visual para acercar una salida a una imagen fuente, si el modelo elegido lo soporta y el hardware lo permite.

## Fases de implementación

| Fase | Resultado verificable | No se considera terminado hasta |
|---|---|---|
| A. Metadatos | CSV local con prompts, checkpoint, LoRA y semilla extraídos cuando existan | pruebas automáticas y revisión del informe local |
| B. Curación | subconjunto de entrenamiento/validación y captions | contenido y permisos revisados; duplicados tratados |
| C. Prueba de base | comparar el modelo compatible y un backend local CPU/Vulkan opcional | imagen real guardada, consumo/tiempo medidos y licencia revisada |
| D. LoRA piloto | adaptación de estilo entrenada y ejemplos antes/después | evaluación en imágenes retenidas y prompts nuevos |
| E. Motor local | interfaz con controles y guardado | generación repetible, manejo de errores y recursos medidos |
| F. Optimización | perfil de bajo consumo y backend seleccionado por medición | mediciones de RAM/VRAM/tiempo guardadas; sin cifras no probadas |

## Salvaguardas del conjunto

No borrar, renombrar ni sobrescribir imágenes originales automáticamente. No entrenar imágenes cuyo permiso siga sin revisar. Una imagen generada en una plataforma puede incluir personajes, diseños o materiales de terceros aunque la haya generado la cuenta del usuario. Registrar por separado procedencia, permisos y utilidad técnica de cada registro.
