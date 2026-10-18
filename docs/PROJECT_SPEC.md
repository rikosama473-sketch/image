# Especificación de IMAGE

## Producto
Generador local de imágenes anime que aprende el patrón visual de la colección propia. Debe permitir escribir descripciones, ajustar el estilo aprendido, producir variantes y guardar PNG y parámetros. Es independiente de WordWaifu y CharacterWord.

## Arquitectura prioritaria
- **Modelo base generativo compatible:** aporta la capacidad general de generar imágenes. Escoger después de leer metadatos, comprobar compatibilidad, licencia y uso de recursos.
- **LoRA de estilo propia:** entrenada con un conjunto pequeño, curado y autorizado. Aprende rasgos comunes del estilo; no es un modelo independiente ni asegura copia pixel a pixel.
- **Motor local de inferencia:** carga el modelo base y una o más adaptaciones compatibles; gestiona prompt, prompt negativo, semilla, dimensiones, pesos/escala, generación de variaciones, guardado y errores.
- **Interfaz sencilla:** prompt, controles principales, vista previa, historial/galería y parámetros reproducibles. No requiere una aplicación gigante ni un formulario de metadatos.

## Objetivo visual
- Aprender similitudes de línea, paleta, sombreado, proporción, rostro, cabello y acabado presentes en las imágenes aprobadas.
- Generar personajes nuevos con variaciones controlables. Los controles anatómicos independientes solo se prometerán si se implementan y evalúan mediante entrenamiento/captions, máscaras, referencias o un subsistema compositor.
- Para reproducir exactamente una imagen previa, guardar el original y su hash; no atribuir esa garantía a una LoRA.

## Entrenamiento y datos
- Ruta principal: adaptar un modelo generativo preentrenado mediante LoRA, no entrenar todo desde inicialización aleatoria.
- No fijar previamente SD 1.5, SDXL o cualquier otra familia. Primero extraer metadatos de las imágenes; las LoRAs son dependientes de un modelo base compatible.
- Agrupar por familia de checkpoint si existen fuentes incompatibles. No mezclar sin revisión imágenes de estilos/modelos distintos en una única LoRA.
- Usar solo imágenes que hayan pasado revisión visual y de permiso de entrenamiento. No entrenar automáticamente con las 759 imágenes.
- Separar validación. Mantener captions/prompts y metadatos verificables; nunca adivinar el modelo o la LoRA a partir del nombre del archivo.
- Registrar dataset/manifest, procedencia, permisos, base exacta y hash/revisión, versión del trainer, configuración, semilla, checkpoints, logs y comparativas.

## Recursos y perfiles
- La meta es **bajo consumo medido**, no una cifra publicitaria. El objetivo anterior de ≤ 2 GB de RAM del sistema no se considera factible ni cumplido para un pipeline moderno de difusión hasta que una prueba reproducible lo demuestre.
- Medir RAM de sistema y VRAM por separado, pico de memoria, tiempo de generación, descarga/disco, tamaño de la LoRA y calidad.
- Comparar familias compatibles de modelo base con una prueba breve y resolución inicial moderada; escoger por calidad/estilo, licencia y recursos reales.
- Evaluar CPU-only, GPU local y/o ejecución remota como perfiles separados. No subir imágenes a servicios externos sin acción y consentimiento explícitos.
- Pesos grandes y resultados de prueba se guardan en directorios locales ignorados por Git.

## Calidad y pruebas de aceptación
1. El extractor funciona con imágenes con y sin metadatos y no altera originales.
2. Se conocen modelo base y origen de la mayor proporción posible de la colección; lo que no se pueda confirmar queda marcado como desconocido.
3. La LoRA piloto produce mejoras consistentes en un conjunto de validación, no solo en las imágenes memorizadas.
4. Las comparativas utilizan prompts, semillas y parámetros registrados.
5. La interfaz puede cargar un modelo y la adaptación compatible, generar una salida y guardarla con sus parámetros.
6. Las mediciones de recursos y las limitaciones están documentadas sin prometer un presupuesto no medido.
7. Todos los originales, anotaciones y decisiones de permiso permanecen recuperables.

## Referencias técnicas
- [Diffusers: LoRA training](https://huggingface.co/docs/diffusers/training/lora): adaptación de una cantidad menor de parámetros y carga posterior sobre un modelo base.
- [Diffusers: SDXL training](https://huggingface.co/docs/diffusers/training/sdxl): técnicas de gestión de memoria y advertencias por complejidad/sobreajuste.
- [rhedak/anime-character-creator](https://github.com/rhedak/anime-character-creator): referencia complementaria para composición procedural SVG, no reemplaza la meta de un generador basado en modelo aprendido.

## Fuera del primer hito
- Entrenar un modelo base completo desde cero.
- Crear un catálogo obligatorio de assets gráficos externos.
- Garantizar 2 GB de RAM sin una prueba en hardware real.
- Garantizar reproducción pixel a pixel de una imagen con una LoRA.
- Controles anatómicos exactos que todavía no estén respaldados por datos y pruebas.
