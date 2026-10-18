# Prototipo del modelo propio

Este directorio contiene un baseline de GAN condicional pequeño iniciado con pesos aleatorios. No descarga checkpoints y no usa Haruka v2, SDXL, Stable Diffusion, LoRA como modelo independiente ni DMD2.

## Dependencias de entrenamiento

```bash
python -m pip install -r requirements-training.txt
```

## 1. Etiquetar y revisar datos

Editar `data/training-labels.csv`. Una fila solo se usa cuando:

- `visual_review=approved`
- `license_review=approved`
- `training_permission=approved`
- `hair`, `clothing`, `legs`, `pose` y `background` contienen valores consistentes.

El script no entrena con las 516 imágenes por defecto: requiere aprobación expresa por fila. Si no hay un conjunto suficientemente revisado, la ejecución se detiene.

## 2. Entrenar

```bash
python ml/train.py --epochs 200 --batch-size 4 --device cpu
```

El modelo usa 64×96 RGBA y un lote pequeño. Es una prueba de viabilidad; el resultado puede ser incoherente, repetir siluetas o sobreajustarse. Entrenar en CPU puede ser lento. El consumo de RAM depende del equipo y debe medirse.

## 3. Generar

Tras entrenar, elige categorías que existan en el manifiesto:

```bash
python ml/generate.py --checkpoint outputs/training/checkpoint-epoch-0200.pt --hair long-dark --clothing casual --legs tights --pose front-standing --background transparent --count 4
```

Los nombres anteriores son ejemplos, no categorías predefinidas. Usa los valores que tú etiquetes.

## Limitaciones
- Una salida RGBA no implica transparencia correcta si los originales tenían fondo opaco.
- Las etiquetas permiten condicionamiento global, pero con 100 imágenes no se garantiza intercambio perfecto de cabello/ropa/piernas.
- El objetivo de 2 GB todavía no está validado. Este prototipo usa PyTorch; una futura versión de inferencia compacta debe medirse y, si es necesario, exportarse a un runtime más ligero.
- No subir checkpoints, salidas generadas ni datos privados al repositorio; están excluidos por `.gitignore`.
