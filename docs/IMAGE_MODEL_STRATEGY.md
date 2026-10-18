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

## Piloto de estilo

- Auditar tamaños, transparencia, errores, duplicados exactos y cercanos, contenido y procedencia.
- Seleccionar un conjunto pequeño, representativo y permitido para entrenamiento. No entrenar automáticamente con las 759 imágenes.
- Separar ejemplos de validación que no participen en el entrenamiento.
- Escribir captions útiles: sujeto y rasgos visibles que deben variar, sin inventar información sobre el origen.
- Probar un token único para el estilo propio y evaluar si la LoRA aprende trazos, paleta, sombreado, proporciones y acabado sin memorizar cada imagen.
- Comparar antes/después con las mismas descripciones, semillas y configuración; revisar ejemplos conocidos y prompts no vistos.
- Guardar por experimento: modelo base y revisión/hash, versión del trainer, manifiesto del conjunto, configuración, semilla, logs, LoRA y ejemplos de validación.

## Recursos y honestidad sobre el hardware

- El ahorro principal proviene de entrenar una LoRA, no un modelo base entero. Aun así, el modelo base sigue ocupando memoria y el coste cambia mucho según familia, resolución, precisión, optimizador, GPU/VRAM y uso de CPU offload.
- No elegir SD 1.5, SDXL, Flux u otra familia por moda: primero buscar el checkpoint original en los metadatos y evaluar compatibilidad, calidad, licencia y memoria. Si no se puede recuperar o no encaja, comparar candidatos ligeros mediante pruebas.
- El objetivo antiguo de 2 GB de RAM del sistema no es una garantía realista para un pipeline moderno de difusión. Medir por separado RAM, VRAM máxima, tiempo por imagen, tamaño descargado en disco y calidad. Hasta medirlo, el requisito es **perfil de bajo consumo medido**, sin promesa fija de 2 GB.
- CPU-only, GPU local y ejecución remota son perfiles distintos. La app debe mostrar qué motor usa y no ocultar cargas o envíos a un servicio externo.
- No comprometer checkpoints ni derivados pesados en Git. Mantenerlos en directorios locales ignorados y registrar instrucciones y versiones.

## «Exacta» versus «similar»

- Para reproducir exactamente un archivo ya generado, conservar el archivo original y su huella, además de los parámetros si existen. La semilla por sí sola no garantiza identidad entre versiones o motores.
- Una LoRA estilística busca semejanza visual y capacidad de producir nuevas composiciones; no promete reconstruir píxeles exactos de imágenes arbitrarias.
- Más adelante puede añadirse img2img o referencia visual para acercar una salida a una imagen fuente, si el modelo elegido lo soporta y el hardware lo permite.

## Fases de implementación

| Fase | Resultado verificable | No se considera terminado hasta |
|---|---|---|
| A. Metadatos | CSV local con prompts, checkpoint, LoRA y semilla extraídos cuando existan | pruebas automáticas y revisión del informe local |
| B. Curación | subconjunto de entrenamiento/validación y captions | contenido y permisos revisados; duplicados tratados |
| C. Prueba de base | comparación de checkpoints compatibles y consumo | modelo elegido por evidencia y licencia |
| D. LoRA piloto | adaptación de estilo entrenada y ejemplos antes/después | evaluación en imágenes retenidas y prompts nuevos |
| E. Motor local | interfaz con controles y guardado | generación repetible, manejo de errores y recursos medidos |
| F. Optimización | preset para el hardware disponible | mediciones de RAM/VRAM/tiempo guardadas; sin cifras no probadas |

## Salvaguardas del conjunto

No borrar, renombrar ni sobrescribir imágenes originales automáticamente. No entrenar imágenes cuyo permiso siga sin revisar. Una imagen generada en una plataforma puede incluir personajes, diseños o materiales de terceros aunque la haya generado la cuenta del usuario. Registrar por separado procedencia, permisos y utilidad técnica de cada registro.
