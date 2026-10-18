# Auditoría de las imágenes del repositorio

## Estado de entrada
El árbol actual contiene 759 imágenes (706,409,784 bytes, unos 706,4 MB): 728 rutas cuyos nombres empiezan por `from-PixAI-` y 31 nombres numéricos. El manifiesto fue actualizado de 546 a 759 filas; se incorporaron 213 rutas nuevas preservando las anotaciones existentes y dejando los permisos como pendientes. El nombre/código se conserva porque el usuario lo usa como pista para identificar el modelo/LoRA asociado; aun así, no se deben adivinar esos identificadores si no están confirmados.

## Ejecutar auditoría
```bash
python -m pip install -r requirements.txt
python scripts/audit_dataset.py --root . --output data/image-audit.csv
```

El CSV reporta ruta, dimensiones, modo de color, alfa, hash SHA-256 y un hash perceptual básico. No modifica imágenes ni decide automáticamente si dos imágenes son duplicadas.

## Etiquetado
Rellena `data/training-labels.csv`:
- `visual_review=approved` solo después de abrir la imagen y comprobar el contenido.
- `license_review=approved` y `training_permission=approved` solo cuando la procedencia/condiciones permiten ese uso.
- `hair`, `clothing`, `legs`, `pose` y `background` deben tener categorías consistentes para el control condicional.
- Una imagen sin rótulos suficientes o sin autorización no pasa al entrenamiento.

## Selección del piloto de 100
No escoger solo las primeras 100 por nombre. Elegir variedad de poses, cuerpos, ropa, peinados y fondos; quitar duplicados; separar validación de entrenamiento; preferir imágenes de un mismo estilo y con cuerpo completo. Si todas pertenecen a una sola pose, el modelo no aprenderá poses nuevas por magia.


## Interfaz local de revisión

Para revisar las imágenes con miniaturas, filtros y etiquetas, usa [tools/dataset-reviewer](../tools/dataset-reviewer/README.md). Selecciona la carpeta local del repositorio, importa este CSV y exporta un manifiesto actualizado. Toda la revisión ocurre en el navegador local; no se suben imágenes.


## Rastrear el modelo base y las LoRA por imagen

El CSV conserva la ruta/nombre original. Para cada archivo, completa por separado `base_model_identifier`, `lora_identifiers` y `lora_weights_or_settings` cuando se conozcan (si hubo varias LoRA, anótalas con sus pesos/ajustes). No renombres imágenes ni conviertas un ID opaco del nombre en el nombre de una LoRA. Esa información identifica la procedencia de generación, pero **no reemplaza** la revisión de derechos: los estados `visual_review`, `license_review` y `training_permission` siguen pendientes hasta comprobar el contenido, la procedencia y la autorización de uso.

El revisor local permite buscar por nombre o por esos campos. Después de editar, exporta el CSV y copia manualmente el resultado revisado a `data/training-labels.csv`.
