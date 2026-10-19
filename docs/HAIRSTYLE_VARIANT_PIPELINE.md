# Flujo IMAGE: referencias de peinados desde GitHub

## Objetivo

Partir de una imagen frontal elegida del propio repositorio y generar seis variantes donde el peinado sea la variable principal. La automatización conserva cada prompt utilizado, registra la imagen de origen y su hash, crea una lámina de contacto y propone los resultados mediante un Pull Request. No sobrescribe ni elimina originales.

El flujo usa la API de edición de imágenes de OpenAI (modelo gpt-image-2.5-sunburst) con la URL pública de la imagen ya guardada en GitHub. La imagen no se adjunta al chat; el servicio de generación sí debe acceder a la referencia para editarla.

## Requisitos previos, una sola vez

1. Después de integrar este cambio en main, abrir **Settings → Secrets and variables → Actions → New repository secret** y crear OPENAI_API_KEY con una clave de API válida. No escribir la clave en código, YAML, commits, prompts ni logs. La generación por API puede tener costes.
2. Ir a **Actions → Generate hairstyle reference variants → Run workflow**.
3. Elegir una imagen que exista en el repositorio. Preferir un retrato frontal vertical, con la cabeza completa, ojos visibles, cabello sin tapar y fondo sencillo. Para este flujo se exige una referencia apropiada, completamente vestida y no explícita. Las primeras imágenes numéricas del repositorio no deben asumirse como aptas; revisar la imagen seleccionada antes de iniciar.
4. Elegir el personaje (Pibara, Chie, Sunna o uno de los dos espacios sin identificar) y el paquete de seis estilos.
5. Al terminar, abrir el Pull Request que genera la automatización y comprobar visualmente la identidad. El resultado no se integra en main automáticamente.

## Qué crea cada ejecución

Dentro de generated/hairstyles/<personaje>/run-<id>/:
- seis imágenes WebP individuales;
- contact-sheet.jpg con las seis variantes;
- PROMPTS.md con el prompt exacto de cada generación y, solo si existía, el prompt recuperado de los metadatos de la referencia;
- manifest.json con ruta, commit y SHA-256 de la referencia, dimensiones, modelo, descripciones y nombres de archivo.

No se infiere la LoRA o el prompt de origen por el nombre de archivo. Si los metadatos no contienen un prompt, el documento dice que no se encontró en lugar de inventarlo.

## Paquetes de variaciones

- core-6: bob recto, largo liso, coleta alta, dos coletas, trenza lateral y ondas en capas.
- short-cuts: pixie, bob a la barbilla, bob asimétrico, shag, wolf cut y pageboy.
- updos: moño alto/bajo, semirecogido, dos moños, coleta y corona trenzada.
- bangs: flequillo recto, lateral, cortina, ligero, raya al medio y raya lateral profunda.
- waves-braids: ondas sueltas, rizos definidos, trenza lateral, espiga, dos trenzas y ondas en capas.

## Límites de calidad y coste

Los prompts insisten en conservar rostro, ojos, gafas, expresión, color de pelo, accesorios, ropa, pose, encuadre y estilo de dibujo. Aun así, un editor generativo puede cambiar algo fuera del pelo. **No se debe considerar una variante válida solo porque sea bonita:** rechazar las que alteren la identidad o la ropa. La siguiente mejora, si las pruebas lo requieren, es aplicar una máscara específica del pelo y comparar los píxeles fuera de esa región antes de aceptar los resultados.

Cada ejecución solicita seis imágenes a la API y puede generar costes. Empieza con una referencia y un solo paquete; no lances cientos de generaciones en lote.

## Separación de personajes y prompts

Pibara, Chie y Sunna son grupos separados. El nombre del grupo no prueba que una imagen corresponda a ese personaje: hay que confirmarlo con la referencia y los metadatos. Los espacios personaje-4 y personaje-5 quedan sin asignar hasta identificar dos identidades adicionales. El registro canónico se debe completar con fuentes reales, quitando del prompt base los rasgos variables (peinado, longitud, raya y recogidos) y manteniéndolos en las variantes individuales.

## Referencias técnicas

- OpenAI, edición de imágenes: https://developers.openai.com/api/reference/resources/images/methods/edit
- OpenAI, guía de generación y edición: https://developers.openai.com/api/docs/guides/image-generation
- GitHub, secretos de Actions: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- GitHub, artefactos de Actions: https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts
