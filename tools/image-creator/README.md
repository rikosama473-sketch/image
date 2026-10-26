# IMAGE — generador anime local

## Uso rápido en Windows

1. Instala Python 3.11 o 3.12 si todavía no está instalado.
2. Ejecuta `setup-image-creator.bat`. Instala PyTorch CPU, Diffusers y el recortador anime local. No instala CUDA.
3. Ejecuta `start-image-creator.bat`.
4. Escribe una descripción y pulsa **Generar imágenes**.

La interfaz preconfigura `hakurei/waifu-diffusion` desde la revisión `main` con `variant=fp16`: Diffusers busca los archivos `.fp16.safetensors` sin cambiar a la rama separada `fp16`, que publica pesos `.bin`. Así se mantiene la carga de `safetensors` segura y se selecciona el conjunto FP16 más pequeño; los pesos se convierten a precisión FP32 al cargarlos para inferencia CPU. Los pesos no se incluyen en Git. La primera generación los descarga a la caché local si autorizás la descarga; el segmentador `isnet-anime` también guarda sus pesos localmente.

## Perfil seguro inicial

- CPU por defecto, apropiado para comenzar con Ryzen 5 5600G e iGPU AMD; la ruta CUDA de PyTorch no acelera esa iGPU.
- Resolución inicial 512 × 768; perfil limitado a 786.432 píxeles por imagen.
- 16 pasos, una imagen por solicitud, procesamiento secuencial, cuatro hilos CPU por defecto (ajustable entre 1 y 6).
- Una sola generación activa; no se apilan trabajos de difusión concurrentes.
- El modo **Un personaje anime** añade términos positivos de sujeto único y negativos base para anatomía, dedos, personajes múltiples, fondos, auras, partículas, emojis, textos, logos y marcas de agua.
- Los prompts positivos y negativos se ajustan al límite del tokenizador del modelo (ventana CLIP); el usuario recibe un aviso si fue necesario recortar texto y los metadatos conservan tanto la descripción original como el prompt efectivo.
- **PNG con fondo transparente** genera sobre blanco y después usa `rembg/isnet-anime` localmente. La salida solo se guarda como transparente si se detectan píxeles no opacos en el canal alfa.

## Privacidad y limitaciones

Los prompts, imágenes y resultados no se envían a una API remota de inferencia. Los pesos del modelo y del segmentador se descargan a la PC durante su primer uso si la descarga está autorizada. La casilla de descarga controla tanto los pesos del modelo base como los pesos faltantes del segmentador; podés dejarla desactivada para limitar el uso a cachés locales, y IMAGE avisará si falta algún archivo.

Los negativos son una guía, no una garantía matemática: pueden quedar manos, caras o poses defectuosas. La segmentación puede recortar mal mechones finos; revisa el resultado y corrige los bordes en el editor. Conservá los originales.

El modelo es un candidato inicial preconfigurado, no un checkpoint incluido con el programa ni una prueba de rendimiento en tu máquina. La generación CPU-only puede tardar bastante. La medición de tiempo y RAM, así como la calidad del recorte, siguen pendientes en el Ryzen real.
