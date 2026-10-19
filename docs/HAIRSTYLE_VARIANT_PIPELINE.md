# Flujo IMAGE: referencias de peinados desde GitHub

## Objetivo

Partir de una imagen del propio repositorio y generar cinco o seis variantes (según el paquete elegido) donde el peinado sea la variable principal. La automatización recorta la zona superior de la cabeza, registra de qué archivo sale y su hash, conserva los prompts, crea una lámina de contacto y propone los resultados mediante un Pull Request. No sobrescribe ni elimina originales.

**El editor no recibe la imagen original completa.** El runner de GitHub recorta una franja superior de la imagen y la coloca en un lienzo neutro cuadrado; la referencia recortada se guarda como reference-head-crop.png para poder revisarla. El recorte funciona mejor con ilustraciones verticales de un solo personaje, de frente o casi de frente, con la cabeza cerca del borde superior. Si el recorte no conserva toda la cara o incluye partes no deseadas, elige otra imagen antes de generar.

El flujo primero intenta recuperar el prompt original de los metadatos con el extractor ya existente en IMAGE. Después usa GPT-6 Luna para inferir un prompt estable a partir del recorte (rostro, ojos, accesorios, color de pelo y patrón de arte, excluyendo largo y forma del peinado). Esa descripción es una reconstrucción visual, **no** el prompt original, y se guarda como candidata pendiente de revisión. Luego usa la API de edición de imágenes GPT-Image-2.5 Sunburst para crear las variantes. Ambas llamadas reciben únicamente la referencia recortada como data URL; la imagen original completa no se envía a esos endpoints.

## Requisitos previos, una sola vez

1. Después de integrar este cambio en main, abrir **Settings → Secrets and variables → Actions → New repository secret** y crear OPENAI_API_KEY con una clave de API válida. No escribir la clave en código, YAML, commits, prompts ni logs. La generación por API puede tener costes.
2. Ir a **Actions → Generate hairstyle reference variants → Run workflow**.
3. Elegir la ruta exacta de una imagen existente. Preferir una imagen vertical de un solo personaje, con la cara y el cabello completos. Seleccionar **mode = preview** primero: no llama a las API de IA ni genera cargos; crea un recorte cuadrado y un manifiesto descargables como artefacto de la ejecución.
4. Revisar visualmente que el recorte contenga el rostro completo y la parte de cabello necesaria. Si corta la barbilla, el flequillo o las puntas, repetir el preview con otra altura o seleccionar otra imagen.
5. Solo después, repetir con **mode = generate**, elegir el personaje (Pibara, Chie, Sunna o uno de los dos espacios sin identificar) y el paquete de cinco estilos (`core-5`) o cualquiera de los paquetes de seis estilos. Es necesario el secreto OPENAI_API_KEY.
6. Al terminar, abrir el Pull Request que genera la automatización y comprobar visualmente la identidad. El resultado no se integra en main automáticamente.

## Qué crea cada ejecución

Dentro de generated/hairstyles/<personaje>/run-<id>/:
- reference-head-crop.png: recorte que realmente se envía al editor, sobre un lienzo blanco 1024×1024;
- cinco imágenes WebP individuales para `core-5`, o seis para los demás paquetes actuales;
- `contact-sheet.jpg` con todas las variantes del paquete seleccionado;
- PROMPTS.md con el prompt exacto de cada generación, el prompt original recuperado si existe y un prompt visual estable inferido (claramente etiquetado como reconstrucción);
- manifest.json con ruta, commit y SHA-256 de la imagen original y del recorte, coordenadas del recorte, dimensiones, modelo y prompts.

No se infiere la LoRA o el prompt de origen por el nombre de archivo. Si los metadatos no contienen un prompt original, el documento lo marca como no encontrado; la reconstrucción visual se guarda aparte como candidata revisable, nunca se presenta como prompt original. Cada ejecución agrega una referencia única al historial del personaje en data/character-prompt-registry.json, dejando canonical_prompt vacío hasta que se revise.

## Cómo se prepara la referencia

El script aplica orientación EXIF, toma el 96% central del ancho y recorta desde arriba una altura seleccionable de 0,60, 0,70 u 0,80 veces el ancho, con un límite del 75% de la altura original. La región se adapta a un lienzo blanco de 1024×1024. El límite anterior de 28% de la altura podía cortar la barbilla en retratos verticales; por eso el preview es ahora el primer paso y permite revisar el encuadre antes de generar.

## Paquetes de variaciones

- core-5: bob recto, largo liso, coleta alta, dos coletas y trenza lateral (cinco estilos, pensado para la primera tanda de Pibara).
- core-6: bob recto, largo liso, coleta alta, dos coletas, trenza lateral y ondas en capas.
- short-cuts: pixie, bob a la barbilla, bob asimétrico, shag, wolf cut y pageboy.
- updos: moño alto/bajo, semirecogido, dos moños, coleta y corona trenzada.
- bangs: flequillo recto, lateral, cortina, ligero, raya al medio y raya lateral profunda.
- waves-braids: ondas sueltas, rizos definidos, trenza lateral, espiga, dos trenzas y ondas en capas.

## Límites de calidad y coste

Los prompts insisten en conservar rostro, ojos, gafas, expresión, color de pelo, accesorios y estilo de dibujo. Aun así, un editor generativo puede cambiar algo fuera del pelo. **No se debe considerar una variante válida solo porque sea bonita:** rechazar las que alteren la identidad. Una mejora posterior sería aplicar una máscara específica del pelo y comparar píxeles fuera de esa región.

Una ejecución en modo preview no llama a modelos ni genera cargos por inferencia. Una ejecución en modo generate solicita una interpretación visual y las imágenes del paquete elegido a las API, así que puede generar costes. Empieza con una referencia y un solo paquete; `core-5` genera cinco imágenes. No lances cientos de generaciones en lote.

## Separación de personajes y prompts

Pibara, Chie y Sunna son grupos separados. El nombre del grupo no prueba que una imagen corresponda a ese personaje: hay que confirmarlo con la referencia y los metadatos. Los espacios personaje-4 y personaje-5 quedan sin asignar hasta identificar dos identidades adicionales. El registro canónico se debe completar con fuentes reales, quitando del prompt base los rasgos variables (peinado, longitud, raya y recogidos) y manteniéndolos en las variantes individuales.

## Referencias técnicas

- OpenAI, edición de imágenes: https://developers.openai.com/api/reference/resources/images/methods/edit
- OpenAI, guía de generación y edición: https://developers.openai.com/api/docs/guides/image-generation
- GitHub, secretos de Actions: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- GitHub, artefactos de Actions: https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts
