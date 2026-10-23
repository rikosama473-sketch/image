# IMAGE — Taller manual de peinados

## Elegir imágenes que puedan ponerse encima de una base plana

El visor de referencias diferencia tres casos en **Uso como capa**:

- **Piezas separadas · requiere base compatible:** paquetes de PNG/XCF con cabello en capas. Empiezan alineados a la plantilla original del recurso; no son universales.
- **Piezas editables · alinear sobre otra base:** sprites o recortes que requieren ajustar tamaño, posición y puntos de unión para otra cabeza.
- **Solo referencia · no es una capa PNG:** hojas con varias cabezas, guías de peinado o vistas previas comerciales. Ayudan a elegir el diseño, pero no se deben importar como un único mechón ni se consideran recortes independientes.

### Fuentes añadidas y límites comprobados

- [HMLF001 de LinXueLian](https://linxuelian.itch.io/customchar-hmlf001-malebust): PNG por carpetas/capas, licencia CC BY-SA 4.0 declarada. Se marca como **base compatible requerida**; sus piezas de 600×800 no encajan automáticamente en toda cabeza.
- [Anime Girl and Boy Portraits — OpenGameArt](https://opengameart.org/content/anime-girl-and-boy-portraits): licencia CC0 declarada y proyecto XCF por capas; el autor menciona dos cortes femeninos y dos masculinos. El paquete sirve como base modular pequeña, no como biblioteca de cientos de cortes.
- [AiryOnline — guía de cabello](https://ko-fi.com/s/4e91f1cc07): separa flequillo frontal, lateral y cabello posterior en variantes. La imagen es una guía de un modelo concreto, no un conjunto de PNG de cabello listo para reutilizar.
- [Syntelligence — coleta y cabello por capas](https://syntelligence.jp/article/57529): la página declara uso gratuito personal/comercial de sus ilustraciones IA. La hoja se clasifica como referencia, porque presenta varias vistas completas y no entrega capas capilares independientes.
- Las dos imágenes Pinterest aportadas por el usuario quedan registradas como referencias pendientes: no se ha verificado su autoría original ni sus permisos.

La biblioteca no descarga automáticamente assets protegidos ni convierte hojas de referencia en capas. Para adaptar un corte a una nueva base plana, hay que aislar el cabello en una pieza transparente, eliminar restos de la cabeza anterior, verificar el alfa, alinear coronilla/ojos/orejas y guardar las coordenadas del recorte. IMAGE no etiquetará ese recorte como aprobado hasta que se revise visualmente.

Esta herramienta existe para construir **varios looks del mismo personaje** sin sustituir su rostro, ojos, cuerpo o vestuario cada vez que cambia el pelo.

## Biblioteca visual compartida de IMAGE

Usá también la [Biblioteca visual de ojos y cabello](../visual-reference-library/index.html) para revisar referencias externas, etiquetar las ilustraciones locales y documentar qué máscaras se pueden separar. Las recetas guardadas son especificaciones; no se presentan como PNG finales. El generador de hojas de contacto es `python scripts/build_visual_contact_sheets.py`.

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

## Tu estilo visual: anime 2D de producción, tipo Madhouse / Trigger

**El criterio principal es la coincidencia de dibujo, no el color.** El visor se abre ahora directamente en una galería de referencias monocromáticas o line art de anime de producción. Prioriza contornos legibles, siluetas limpias, mechones agrupados y vistas de modelo útiles para separar cabello en capas.

El archivo [`hairstyle-web-references.json`](hairstyle-web-references.json) registra 33 fuentes, pero el visor muestra de inicio solo las 15 marcadas como **anclas Madhouse/Trigger o line art anime compatible**. Las fuentes de sprites, pixel art y estilos ajenos quedan fuera del conjunto principal; existe un filtro explícito para mostrarlas si hiciera falta. No se usa el color del cabello como criterio de búsqueda.

### Referencias prioritarias del lenguaje de dibujo

- [Trigger — Kill la Kill, modelo y bocetos de cabello](https://characterdesignreferences.com/art-of-animation-6/art-of-kill-la-kill): contorno angular, mechones direccionales y siluetas expresivas.
- [Trigger — Little Witch Academia, giro de cabeza](https://characterdesignreferences.com/art-of-animation-8/art-of-little-witch-academia): corte corto en vistas frontal, lateral y trasera.
- [Trigger — Little Witch Academia, cabello largo y ondas](https://characterdesignreferences.com/art-of-animation-8/art-of-little-witch-academia): volumen de pelo largo, caída y curvas por grupos.
- [Madhouse — Perfect Blue, hojas de modelo](https://characterdesignreferences.com/art-of-animation-3/perfect-blue): cabello corto y largo desde distintos ángulos; útil para mantener la silueta constante.
- [Anime TV — A Certain Scientific Railgun](https://characterdesignreferences.com/art-of-animation-8/art-of-a-certain-scientific-railgun): cabello largo recogido, mechones frontales y vistas laterales.
- [Anime TV — Girls und Panzer](https://characterdesignreferences.com/art-of-animation-9/art-of-girls-und-panzer): bob y contorno de mandíbula desde varias direcciones.
- [Guía line art de unos 50 peinados](https://www.pinterest.com/pin/569494315363825774/): fuente complementaria para descubrir variedad de cortes sin depender del color.
- [Comparación de cortes en line art](https://syntelligence.jp/article/57539): cabello corto, largo y coletas dobles sobre cabezas consistentes.

Las hojas de producción y referencias de series están protegidas por sus titulares. Se enlazan para estudiar lenguaje de dibujo y continuidad, no para copiar o redistribuir los originales. Las miniaturas se cargan desde sus fuentes: si un sitio cambia la URL o bloquea la vista previa, el visor ofrece un enlace para abrir la fuente original.

### Cómo usar el filtro

1. Ejecutá `tools/avatar-maker/start-avatar-maker.bat` y abrí `http://127.0.0.1:8766/tools/hairstyle-workbench/index.html`.
2. Entrá en **Visor de 120 diseños**. El visor abrirá primero **Mi estilo · line art anime**, no las recetas esquemáticas.
3. Elegí **Solo mi estilo** para combinar las referencias de Madhouse/Trigger con las hojas line art compatibles. Los otros estilos están ocultos por defecto.

Las 120 recetas conceptuales siguen disponibles como ideas de composición, pero no se consideran modelos visuales finales ni reemplazan una biblioteca de recortes. El siguiente trabajo artístico debe usar el lenguaje visual de estas hojas como referencia al normalizar las piezas: silueta posterior, flequillos, mechones laterales, recogidos y accesorios. El color puede añadirse después o no usarse en absoluto.

### Fuentes reutilizables y licencias

El catálogo conserva además cinco enlaces a paquetes de OpenGameArt con licencias declaradas, pero no se muestran en la galería principal porque parte de ellos usa pixel art u otros estilos. No se han extraído todavía en PNG aprobados. Antes de incorporarlos, cada archivo debe pasar un filtro de estilo; tener licencia reutilizable no significa que encaje con el arte de IMAGE.
