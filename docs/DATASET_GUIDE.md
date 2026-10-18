# Preparación del dataset para la LoRA de estilo de IMAGE

## Estado conocido de la colección
El inventario de main registra 759 imágenes (706.409.784 bytes, aprox. 706,4 MB): 728 nombres empiezan por `from-PixAI-` y 31 son numéricos. El manifiesto conserva sus rutas/nombres originales y las columnas para modelo base, LoRAs de origen, configuración y LoRA destino. Esas cantidades describen el inventario; no significan que las imágenes estén aprobadas ni listas para entrenamiento.

## Paso 1: rescatar la información embebida

Ejecutar desde la raíz del repositorio:

~~~bash
python -m pip install -r requirements.txt
python scripts/extract_generation_metadata.py --root .
~~~

Se genera `data/cache/generation-metadata.csv` en una carpeta local excluida de Git. El extractor lee metadatos comunes en PNG/JPEG/WebP/TIFF y busca prompts, prompts negativos, identificadores/hash de modelo, datos de LoRA, sampler, pasos, CFG y semilla. También intenta leer bloques de parámetros habituales. Los formatos de cada aplicación difieren: por tanto, el CSV es un informe heurístico que debe revisarse y no una fuente infalible.

- Si una imagen no tiene metadatos, el informe la marca como desconocida; el script no inventa un modelo ni una LoRA a partir del nombre.
- No modifica el archivo de imagen.
- Un hash de metadatos ayuda a comparar registros, pero no prueba autoría, procedencia ni derechos.
- Cruzar los resultados con el manifiesto de etiquetas de manera revisada. Mantener separados los ajustes de origen y la LoRA que se quiere utilizar después.

## Paso 2: auditoría visual/técnica

~~~bash
python scripts/audit_dataset.py --root . --output data/image-audit.csv
python scripts/sync_training_labels.py --root .
~~~

El informe de auditoría reporta dimensiones, modo de color, transparencia, SHA-256 y un hash perceptual básico. No elimina duplicados ni cambia originales. Una persona debe confirmar si las imágenes muestran el tipo de arte y contenido que se desea aprender.

## Paso 3: decidir qué se aprende

La ruta principal es una LoRA entrenada encima de un modelo base generativo compatible, no una red pequeña aleatoria desde cero. Antes de escoger la base:

1. Agrupar imágenes por el checkpoint o familia confirmada en metadatos.
2. Comparar el estilo visual dentro de cada grupo.
3. Verificar que el checkpoint se pueda obtener legalmente, sea compatible con la LoRA prevista y permita el uso deseado.
4. Si hay muchas familias distintas, probar por separado pequeños subconjuntos en vez de mezclarlos automáticamente.
5. Si faltan metadatos, escoger con inspección visual y dejar el origen marcado como incierto.

El número de imágenes útil no equivale necesariamente al tamaño total de la carpeta. La diversidad, calidad, coherencia del estilo, captions, duplicados y permiso de entrenamiento afectan el resultado.

## Paso 4: preparar el piloto

- No elegir simplemente las primeras 100 por nombre.
- Quitar/revisar duplicados exactos y casi duplicados para evitar sobreponderar una misma composición.
- Elegir ejemplos variados pero coherentes con el estilo que se pretende aprender.
- Crear captions honestos que describan lo visible (personaje, encuadre, cabello, ropa, paleta, acabado) sin inventar rasgos invisibles ni atribuir modelos no confirmados.
- Separar imágenes de validación que nunca entran al entrenamiento.
- Mantener anotaciones de permiso por imagen; no pasar a entrenamiento si el permiso sigue pendiente.
- Comenzar con una prueba pequeña y guardar el conjunto exacto usado, parámetros y ejemplos de salida.

## Paso 5: evaluar sin engañarnos

Comparar una selección de prompts con y sin LoRA, usando el mismo modelo base, semillas y configuración. Incluir:
- prompts que describen imágenes similares a las del entrenamiento;
- prompts nuevos con peinados, ropa, encuadres y colores que no aparezcan juntos en una sola imagen;
- ejemplos retenidos de validación;
- defectos recurrentes, fugas de conceptos no deseados y señales de memorización.

Una LoRA de estilo no garantiza una copia exacta de cualquier ejemplo. Para reproducir un resultado anterior se debe conservar el archivo original y, cuando estén disponibles, el modelo base exacto, las LoRAs y sus pesos, prompt, seed, sampler, pasos y versión del motor.

## Interfaz de revisión

Usa [tools/dataset-reviewer](../tools/dataset-reviewer/README.md) para filtrar y editar etiquetas en el navegador local. No sube las imágenes. Después de editar, exporta y revisa el CSV antes de reemplazar manualmente el manifiesto oficial.
