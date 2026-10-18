# Especificación de IMAGE

## Producto
Generador de personajes anime de uso local, estilo limitado, interfaz sencilla y consumo de memoria medido. Debe permitir cambiar atributos visuales controlados, no actuar como un generador de escenas universal.

## Generación esperada
- Cuerpo/personaje completo en un estilo anime constante.
- Controles: peinado, categoría de ropa, tipo de pierna/calzado, pose, paleta.
- Fondo: transparente cuando los datos realmente tengan alfa/segmentación; en caso contrario, fondo plano o estilizado añadido en una fase de composición. No confundir fondo eliminado con fondo blanco.
- Tamaño inicial de investigación: 64×96; aumentar únicamente después de medir los errores anatómicos y el coste de RAM.
- Salida final: PNG; versiones compactas opcionales para vista previa.
- Semilla y parámetros guardados para reproducir generaciones.

## Modelo
- Inicialización aleatoria; no checkpoint general de terceros, LoRA dependiente de base ni DMD2/teacher distillation.
- Baseline futuro: GAN convolucional condicional pequeño a baja resolución, comparado con un VAE si el GAN colapsa o produce demasiados defectos.
- Las condiciones se entrenan a partir de etiquetas explícitas de cabello, ropa, piernas, pose y fondo. Sin esas etiquetas, no se puede prometer que cada selector controle su atributo.
- Dataset piloto: seleccionar 100 imágenes auditadas del corpus existente si son adecuadas. No entrenar automáticamente las 434 imágenes completas.
- Data augmentation solo dentro de límites que no alteren anatomía/etiquetas; espejado solo si la pose/ropa lo permite.

## Presupuesto
- Objetivo de inferencia: ≤ 2 GB de RAM del sistema, medido con proceso/modelo y herramienta de interfaz activos.
- Entrenamiento: presupuesto aparte; no prometer que cabe en 2 GB.
- Registrar el peak RSS, tiempo por imagen y tamaño del checkpoint.
- No utilizar pesos de una IA externa para inicializar, acelerar ni destilar la arquitectura del generador propio.

## Condiciones para elegir el conjunto
Cada imagen debe tener:
1. Origen identificado; el nombre del archivo es solo una pista.
2. Revisión visual humana y revisión de posibles personajes/logos de terceros.
3. Permiso de entrenamiento registrado.
4. Una etiqueta de estilo y valores para pelo, ropa, piernas, pose y fondo.
5. Dimensión y canal alfa comprobados.
6. Revisión de duplicados exactos y perceptuales.

## Prohibiciones del pipeline
- No entrenar por defecto sobre todo el directorio.
- No cambiar ni borrar originales automáticamente.
- No incluir imágenes sin permiso verificado.
- No declarar el modelo como entrenado o el objetivo de 2 GB como cumplido hasta medirlo.
