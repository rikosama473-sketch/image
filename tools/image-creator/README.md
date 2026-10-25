# IMAGE — generador anime local

## Uso rápido en Windows

1. Instala Python 3.11 o 3.12 si todavía no está instalado.
2. Ejecuta `setup-image-creator.bat`. Instala PyTorch CPU, Diffusers y el recortador anime local. No instala CUDA.
3. Ejecuta `start-image-creator.bat`.
4. Escribe una descripción y pulsa **Generar imágenes**.

La interfaz preconfigura `Ojimi/anime-kawai-diffusion` como candidato anime de arranque basado en Stable Diffusion 1.x. Sus pesos no se incluyen en Git porque son grandes. La primera generación los descarga a la caché local cuando se permite esa descarga; el segmentador `isnet-anime` también descarga sus pesos locales en su primer uso.

## Perfil seguro inicial

- CPU por defecto, apropiado para comenzar con Ryzen 5 5600G e iGPU AMD; la ruta CUDA de PyTorch no acelera esa iGPU.
- Resolución inicial 512 × 768; perfil limitado a 786.432 píxeles por imagen.
- 16 pasos, una imagen por solicitud, procesamiento secuencial, cuatro hilos CPU por defecto (ajustable entre 1 y 6).
- Una sola generación activa; no se apilan trabajos de difusión concurrentes.
- El modo **Un personaje anime** añade términos positivos de sujeto único y negativos base para anatomía, dedos, personajes múltiples, fondos, auras, partículas, emojis, textos, logos y marcas de agua.
- **PNG con fondo transparente** genera sobre blanco y después usa `rembg/isnet-anime` localmente. La salida solo se guarda como transparente si se detectan píxeles no opacos en el canal alfa.

## Privacidad y limitaciones

Los prompts, imágenes y resultados no se envían a una API remota de inferencia. Los pesos del modelo y del segmentador se descargan a la PC durante su primer uso si la descarga está autorizada. Si elegís un modelo detectado localmente, el selector desactiva la descarga remota.

Los negativos son una guía, no una garantía matemática: pueden quedar manos, caras o poses defectuosas. La segmentación puede recortar mal mechones finos; revisa el resultado y corrige los bordes en el editor. Conservá los originales.

El modelo es un candidato inicial preconfigurado, no un checkpoint incluido con el programa ni una prueba de rendimiento en tu máquina. La generación CPU-only puede tardar bastante. La medición de tiempo y RAM, así como la calidad del recorte, siguen pendientes en el Ryzen real.
