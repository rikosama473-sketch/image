# Auditoría de las imágenes del repositorio

## Estado de entrada
El inventario inicial contiene 516 PNG (478.6 MB en total). 485 nombres parecen venir de una exportación PixAI; eso es solo una pista de nombre. Los archivos numéricos requieren localizar su origen.

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
