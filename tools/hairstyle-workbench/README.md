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

## Biblioteca visual de 120 diseños y combinador

El botón **Visor de 120 diseños** abre una biblioteca con búsqueda por nombre, rasgos, familia y largo. Cada receta combina una silueta conceptual con variaciones de flequillo, mechones, coleta lateral o semirrecogido, ahoge y adornos. Las miniaturas se dibujan como bocetos vectoriales dentro del navegador para comparar ideas; **no son 120 PNG de cabello ni ilustraciones finales**.

Al pulsar **Probar en el lienzo**, el editor activa las piezas reales que puede emparejar por categoría y etiquetas. Si no existe un recorte exacto, la interfaz marca la base como aproximada e informa los PNG que faltan. Así no presenta una receta textual como si ya existiera el recurso visual.

### Construir combinaciones exactas

1. Importá cada recurso como PNG/WebP con transparencia: una silueta posterior/base, flequillo, mechón lateral largo, coleta o trenza parcial, ahoge y accesorio. Los recursos recortados sobre el mismo lienzo y con el mismo origen de coordenadas se alinean mejor.
2. Elegí para cada pieza su categoría y añadí etiquetas coherentes. Para el ejemplo **cabello corto + mechón largo + coleta lateral + ahoge**, usá etiquetas como `short_hair`, `long_sidelocks`, `side_ponytail` y `ahoge` en las piezas que correspondan. El corte base debe etiquetarse por separado.
3. Marcá las capas deseadas en **Combinador manual de piezas**. El editor permite varias piezas parciales; al activar otro corte completo desactiva el corte base anterior.
4. Guardá la combinación como variante y exportá el proyecto JSON para conservar posiciones, etiquetas y PNG importados. El PNG exportado refleja solo las piezas que realmente estén cargadas.

El catálogo de bocetos sirve como explorador de diseño. La disponibilidad y calidad de un peinado real depende de tener el recorte PNG correcto, la transparencia limpia, las proporciones alineadas y la revisión visual del recurso. Las máscaras candidatas existentes continúan marcadas como pendientes hasta revisarlas.

## Colección de referencias reales encontradas en la web

El visor ahora tiene dos pestañas: **120 recetas conceptuales** y **Referencias web y recursos**. Esta segunda pestaña registra 20 fuentes localizadas en la web: referencias visuales femeninas y masculinas, láminas con varias decenas de cortes, vistas laterales/traseras y cinco fuentes de recursos descargables con licencia declarada. Quince entradas incluyen vista previa remota; todas conservan enlace a su fuente y estado de licencia. Las referencias sin permiso comprobado no se copian al repositorio ni se presentan como libres de derechos.

### Fuentes con archivos/licencias declaradas

- [Anime Girl and Boy Portraits — OpenGameArt](https://opengameart.org/content/anime-girl-and-boy-portraits): el autor declara CC0 y describe un XCF de GIMP con capas editables, dos cortes femeninos y dos masculinos, y opciones de coleta. [ZIP](https://opengameart.org/sites/default/files/allanime-11-28-2020.zip).
- [Hair Animation — OpenGameArt](https://opengameart.org/content/hair-animation): CC0 declarado; contiene PSD y GIF de muestras de cabello corto/largo.
- [Hair for 24x32 bases — OpenGameArt](https://opengameart.org/content/hair-for-24x32-bases): CC0 declarado; nueve peinados de sprite, incluidos rizado y trenza. Es pixel art pequeño, no una pieza anime HD.
- [Anime LPC Hair — OpenGameArt](https://opengameart.org/content/anime-lpc-hair): CC-BY 3.0; conservar atribución.
- [Hair for male and female anime base sprites — OpenGameArt](https://lpc.opengameart.org/content/hair-for-male-and-female-anime-base-sprites): la página enumera GPL-2.0, GPL-3.0, CC-BY-3.0 y CC-BY-SA-3.0. Revisar la licencia elegida y atribuir al autor antes de redistribuir.

Estos son puntos de partida para importar y separar capas, no una afirmación de que todos los archivos ya están extraídos, alineados o aprobados para el estilo final. La pestaña identifica cada recurso, su licencia declarada, URL de origen y si es una referencia o un archivo descargable.

### Referencias visuales sin permiso de reutilización confirmado

La colección incluye láminas de variantes femeninas, masculinas, cortes cortos, mechones, coletas, trenzas y bob/hime/wolf cut. Sus miniaturas son enlaces de referencia remotos; la etiqueta **No verificada; referencia visual únicamente** significa que se pueden estudiar para descubrir diseños, pero no deben copiarse, descargarse para redistribución o transformarse en recortes integrados sin verificar permisos con quien tenga los derechos.

El próximo paso de la colección real es descargar los paquetes que permiten reutilización, extraer sus capas de cabello, normalizar transparencia y pivote, hacer control visual y convertir cada pieza aprobada a un asset individual con su licencia y atribución preservadas.
