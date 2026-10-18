# Baseline experimental legado: GAN condicional desde cero

> **No es la ruta principal vigente de IMAGE.** Se conserva solo como experimento comparativo de muy bajo nivel. La meta actual es adaptar un modelo generativo base compatible mediante una LoRA propia y construir el motor local alrededor de esa combinación.

Este directorio contiene un GAN condicional pequeño iniciado con pesos aleatorios. No descarga checkpoints y no proporciona la capacidad de un generador moderno de texto a imagen. Úsalo para comparación experimental, no como solución principal de arte similar a la colección.

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
python ml/train.py --max-images 100 --epochs 200 --batch-size 4 --device cpu
```

El modelo usa 64×96 RGBA y un lote pequeño. Es una prueba de viabilidad; el resultado puede ser incoherente, repetir siluetas o sobreajustarse. Entrenar en CPU puede ser lento. El consumo de RAM depende del equipo y debe medirse.

El valor predeterminado limita el piloto a 100 imágenes aprobadas escogidas de forma pseudoaleatoria reproducible mediante la semilla. No asume que el primer bloque de 100 archivos sea representativo. Usa `--max-images 0` solo después de revisar todo el conjunto y querer entrenar con todas las imágenes aprobadas.

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

## 4. Exportar para inferencia ligera

Cuando exista un checkpoint propio:

```bash
python -m pip install -r requirements-training.txt
python ml/export_onnx.py --checkpoint outputs/training/checkpoint-epoch-0200.pt
```

Para usar el generador sin importar PyTorch, instala el runtime de CPU:

```bash
python -m pip install -r requirements-inference.txt
python ml/generate_onnx.py --hair long --clothing casual --legs tights --pose front-standing --background plain --count 4
python ml/benchmark_onnx.py --count 24 --batch-size 1
```

El informe guardado en `outputs/onnx/memory-benchmark.json` mide RSS pico del proceso y latencia en ese equipo. Para aceptar el límite de 2 GB, repetir la prueba en la PC objetivo con el motor/interfaz abiertos; el RSS del proceso no equivale al consumo total del sistema.

