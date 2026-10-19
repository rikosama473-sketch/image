# IMAGE — Editor modular de personajes

Esta rama cambia el objetivo principal de IMAGE: el producto es un editor local para componer personajes 2D a partir de imágenes y piezas, no un generador por difusión.

## Ejecutar

Se requiere Python 3.10 o posterior. No necesita PyTorch, modelos generativos, LoRA, GPU ni conexión a servicios de IA.

Desde la raíz del repositorio:

~~~powershell
python ml/character_editor_server.py --assets-dir "D:\Carpeta\Con\Mis\Imagenes" --open-browser
~~~

También se puede omitir el argumento de carpeta para indexar las imágenes del propio checkout. El servidor escucha únicamente en 127.0.0.1:8766. No escanea todo el disco: solo la carpeta indicada y sus subdirectorios, con límites explícitos.

En Windows se puede abrir el archivo Start-Character-Editor.bat de esta carpeta y elegir la carpeta de imágenes en el selector.

## Flujo actual

1. Explorar y buscar imágenes de la carpeta seleccionada.
2. Añadir imágenes como capas de referencia o pieza.
3. Arrastrar una capa por el lienzo, ajustar posición, dimensiones, rotación, opacidad y orden.
4. Seleccionar una capa y usar Recortar pieza para extraer un fragmento rectangular.
5. Opcionalmente, intentar hacer transparente una región de color uniforme conectada al borde de la pieza.
6. Exportar un PNG transparente y guardar/cargar un proyecto JSON.

Los originales son de solo lectura. Las piezas recortadas quedan incrustadas dentro del proyecto JSON. Las capas que solo enlazan una imagen conservan la ruta relativa, por lo que para reabrirlas hay que usar la misma carpeta de origen.

## Límites importantes

- Las miles de imágenes son una fuente de referencias, no un conjunto de piezas anatómicas ya limpias.
- El recorte rectangular, el pincel manual para borrar/restaurar y la eliminación aproximada de un color de fondo permiten preparar piezas simples, pero no aíslan automáticamente pelo, brazos, manos o ropa de una ilustración completa.
- Lo que está oculto detrás del torso, cabello o vestimenta no existe en los píxeles visibles y necesita redibujarse o retocarse.
- El editor no usa IA ni entrenamiento. No realiza cargas remotas ni escribe en la carpeta de imágenes.
- Se indexan hasta 10.000 imágenes en hasta 5.000 directorios; se omiten archivos de más de 100 MB. Para una colección mayor, conviene escoger carpetas por personaje o tema.
- Es un primer editor de composición y extracción, no un editor de animación con esqueleto ni un reemplazo completo de Krita o GIMP.

## Siguiente etapa

Mejorar la preparación de piezas: guardado de piezas con etiquetas y puntos de anclaje (cabeza, cuello, hombros, codos, muñecas, cadera, rodillas y tobillos). Eso permitirá que las piezas se ensamblen con menos ajustes. La clasificación no debe alterar ni sobrescribir los originales.
