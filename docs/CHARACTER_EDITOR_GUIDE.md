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


## Herramientas de diseño original

- Capa de dibujo transparente separada de las referencias.
- Pincel, borrador que solo afecta a la capa dibujable, línea, rectángulo, elipse con relleno opcional y cubo de pintura para regiones de color similares.
- Plantillas editables para camiseta, chaqueta, falda, pantalones y capa/manto. Se pueden colorear con relleno y personalizar con costuras, mangas, cintas y adornos.
- Las capas dibujables se guardan dentro del proyecto JSON; no se escribe en las imágenes originales.
- El lienzo es raster 2D: estas funciones permiten dibujar y personalizar prendas y rasgos sencillos, pero no simulan un patrón de costura profesional ni inventan anatomía o detalles ocultos automáticamente.


## Biblioteca de 288 bosquejos de prendas

La sección **Diseño original** incluye 36 tipos de ropa y 8 variaciones geométricas por tipo (288 combinaciones base): remeras clásicas, ajustadas y oversize; tops y musculosas; blusas y camisas; suéteres, buzos, camperas, blazer y abrigo; chaleco, corsé, bikini, body y uniforme; delantal; tres faldas; shorts y distintos pantalones; overol; vestidos cortos, largos, de princesa, góticos y de uniforme; kimono, capa, túnica fantástica y armadura de torso.

- **Añadir guía gris** crea una capa independiente con contorno gris claro, líneas internas de costura y algunas líneas discontinuas de construcción. Está pensada para superponerla sobre el personaje y dibujar la ropa encima.
- **Añadir prenda con color** crea una silueta coloreada editable como base. El color se toma del selector de color del panel.
- Variantes: clásica, entallada, holgada, corta, larga, manga más larga, compacta y asimétrica. Son esqueletos visuales generados con geometría 2D, no 288 ilustraciones profesionales dibujadas a mano.
- Después de añadir la capa, elige **Mover** para arrastrarla; puedes ajustar X/Y, ancho, alto, rotación y opacidad en el inspector. El pincel y las demás herramientas dibujan sobre la capa seleccionada. Duplica una plantilla para conservar una copia limpia.
- La guía no modifica la imagen de referencia. Guarda el proyecto JSON si quieres conservar las capas editables; al exportar PNG, oculta o elimina antes las guías que no quieres incluir en la imagen final.
