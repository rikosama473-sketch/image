# IMAGE — Taller manual de peinados

Esta herramienta existe para construir **varios looks del mismo personaje** sin sustituir su rostro, ojos, cuerpo o vestuario cada vez que cambia el pelo.

## Abrir

1. Desde la raíz del repositorio, iniciá `tools/avatar-maker/start-avatar-maker.bat`.
2. Abrí `http://127.0.0.1:8766/tools/hairstyle-workbench/index.html`.
3. Pulsá **Cargar muestra por capas** para probar el conjunto que ya está indexado en `tools/avatar-maker/assets/catalog.json`.

La página es HTML/Canvas local. **No llama a una API, no genera imágenes y no necesita una clave de IA.** Permite importar PNG/WebP transparentes, mover/ajustar capas, conservar varios looks, duplicar una variante aunque sea parecida a otra, guardar el proyecto JSON y exportar la composición como PNG con alfa.

## Qué cambia con este taller

- La base del personaje es independiente de las variantes de peinado.
- Un corte completo puede alternarse con otro; flequillos, mechones laterales, trenzas, coletas y accesorios se pueden mantener como piezas separadas.
- Cada variante tiene un identificador propio. No existe una rutina que elimine o fusione cortes visualmente parecidos.
- Las etiquetas son acumulativas. Un mismo peinado puede ser, por ejemplo, largo + flequillo abierto + trenza lateral.
- Los PNG importados quedan incrustados en el JSON para que el proyecto se pueda mover entre carpetas. Los recursos internos conservan su ruta de origen.

## Importante sobre la muestra

Las capas integradas de Pibara son **candidatos pendientes de revisión visual**, no una biblioteca de recortes aprobados. La muestra sirve para validar que varias opciones de pelo se puedan alternar sobre un conjunto base, no para certificar el resultado artístico de esas máscaras. Si los bordes o el rostro no encajan, revisá o reemplazá las capas antes de utilizarlas como piezas finales.

Para separar una pieza manualmente, abrí también el [Editor manual de recortes](../manual-character-editor/index.html). Exportá cada pieza en un lienzo con el mismo tamaño y posición cuando sea posible; mantener el marco completo evita que los mechones salten de lugar al alternar cortes.

## Taxonomía y biblioteca

El vocabulario estructurado se encuentra en [hair-style-taxonomy.json](hair-style-taxonomy.json). Los tags se tratan como atributos, no como claves únicas: dos assets que comparten `bob_cut` pueden seguir siendo dos diseños distintos. Los términos marcados como pendientes de verificación son categorías editoriales y no deben presentarse como etiquetas oficiales verificadas de Danbooru.

## Derechos de uso

El editor no transforma un archivo en material libre de derechos. Registrá URL, autor, licencia y permiso de uso de cada recurso. Revisá los permisos antes de redistribuir ilustraciones o incorporarlas a paquetes públicos.
