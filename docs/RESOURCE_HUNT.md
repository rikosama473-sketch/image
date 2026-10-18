# Búsqueda de piezas gráficas compatibles

**Objetivo:** adquirir piezas reutilizables para personajes, no solo ilustraciones completas. Revisión: 2026-10-18.

## Candidatos concretos

| Recurso | Tipo de piezas | Licencia/estado | Valor para IMAGE |
|---|---|---|---|
| [Kenney Modular Characters](https://kenney.nl/assets/modular-characters) / [OpenGameArt](https://opengameart.org/content/modular-character-pack) | 425 PNG separados, seis spritesheets, seis archivos vectoriales, muchas combinaciones. | CC0 según listado de Kenney/OpenGameArt; archivo y dimensiones exactas pendientes de inspección. | Mejor primer banco para aprender alineación, orden de capas y combinaciones. Estilo cartoon, no anime. |
| [PSRC Human Mk2](https://opengameart.org/content/psrc-human-mk2-and-ultimate-devkit) | Cabeza, torso, brazos, piernas, manos, pies y plantillas de ropa. | OpenGameArt indica CC0; página oficial tiene texto informal sobre licencia. Confirmar contenido/condiciones del ZIP antes de publicar o entrenar. | Muy útil para referencia de articulación y cuerpos modulares; pixel art. |
| [Anime-style female base sprite](https://opengameart.org/content/anime-style-female-base-sprite) | Base femenina y enlaces a paquetes de rostros, cabello y accesorios. | Página enumera varias licencias (CC-BY 3.0, CC-BY-SA 3.0, GPL); validar licencia concreta de cada archivo. | Estética anime/pixel, candidato visual interesante; no integrar hasta resolver licencia. |
| [Thin Girl — ani mosity](https://queenofzan.itch.io/modular-character-sprite-thin-girl) | PNG independientes y PSD de pelo/rostro/ropa, lienzos alineados. | CC BY 4.0 con atribución; la autora excluye expresamente sus assets de datasets de IA generativa. | Puede servir para aprender composición/uso en un editor respetando términos, pero NO para entrenar nuestro modelo sin permiso separado. |
| [Modular Pixel Character Kit — monapdx](https://monapdx.itch.io/modular-pixel-character-kit) | PNG transparentes alineados, pelo, caras/tonos, fuente GIMP XCF. | Descarga gratuita indicada; no se identificó licencia estándar en la página. Revisar ZIP o preguntar al autor. | Candidato prioritario si aclaramos licencia y compatibilidad. |
| [Modular Pixel Character Creator (Female) — monapdx](https://monapdx.itch.io/modular-pixel-character-creator-female-sprites) | Base, pelo, caras y ropa alineados. | Paquete distinto; licencia y ZIP pendientes de revisión. | Candidato femenino para probar el ensamblado. |
| [Anime Girl / Michona — Hordana](https://opengameart.org/content/anime-girl) | Tiras PNG de caminar, saltar y parpadear. | CC0 según OpenGameArt; no son piezas anatómicas independientes. | Sirve para estudiar animación o crear una vista previa, no es la base principal de capas. |

## Recursos técnicos (no son bancos de arte)

- [SpriteGAN](https://github.com/thomasg8/SpriteGAN): 32×32; el proyecto informa 4.272 sprites seleccionados de un universo de 16.627 recursos CC0. Lección: curar datos, quitar casi duplicados y recortar con cuidado.
- [MDIGAN Characters](https://github.com/fegemo/mdigan-characters): completa vistas emparejadas de un mismo personaje, 64×64 RGBA; no es un generador de cuerpo libre.
- [PyTorch DCGAN tutorial](https://docs.pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html): referencia para el lazo de entrenamiento, inestabilidad y colapso de modo.
- [StyleGAN2-ADA](https://arxiv.org/abs/2006.06676): referencia conceptual sobre sobreajuste en datasets limitados; no se adopta su checkpoint ni su implementación.

## Protocolo para cada activo
1. Abrir la fuente original, registrar autor, URL, licencia y fecha.
2. Descargar sin eludir pagos/login/limitaciones; leer licencia/README del ZIP.
3. Inventariar archivos, dimensiones, color/alfa, lienzo alineado y anchors.
4. Separar los permisos para (a) importar/modificar en el motor, (b) distribuir los archivos y (c) entrenar IA. Son decisiones separadas.
5. Montar base + pelo + ropa + extremidades, exportar una vista y probar si los pivotes coinciden.
6. No copiar al dataset hasta que la licencia autorice claramente el uso para entrenamiento.


## Más candidatos localizados (18-10-2026)

| Recurso | Qué aporta | Licencia / condición | Siguiente prueba |
|---|---|---|---|
| [Paper Doll Style Sprites — OpenGameArt](https://opengameart.org/content/paper-doll-style-sprites) | Figuras, pantalones, zapatos y camisas como overlays separados; varios ZIPs. | CC BY-SA 3.0; atribución y compartir adaptaciones bajo términos compatibles. | Inspeccionar cada ZIP, lienzos y orden de capas. Estética RPG vista superior, no anime. |
| [2D female and male bone-based sprites](https://opengameart.org/content/2d-female-and-male-bone-based-sprites) | Partes 2D con pivotes en los nombres, pensadas para rotación/escalado. | CC0. El autor indica que las figuras tienen poca ropa. | Probar pivotes, muñecas, codos, rodillas y tobillos; no confundir con un paquete de ropa completo. |
| [80x64 Male and Female Sprites Character Template](https://opengameart.org/content/80x64-male-and-female-sprites-character-template) | Componentes con cabello, ropa y animaciones sencillas en plantilla 80×64. | CC0 según página. | Inspeccionar ZIP, frames y alineación; seleccionar solo los componentes que correspondan al objetivo. |
| [Paperdoll Characters (template)](https://opengameart.org/content/paperdoll-characters-template) | Maqueta base femenina/masculina simple. | CC0. | Solo referencia de estructura; no es una biblioteca detallada. |
| [Universal LPC Spritesheet Generator](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/) | Compositor en navegador que selecciona partes y exporta créditos/licencias por recurso. | Licencia mixta por activo; el conjunto debe auditarse pieza a pieza. | Estudiar UI y manifiesto de atribución, no copiar el catálogo entero. |
| [OverScore Proxy](https://opengameart.org/content/overscore-proxy-modular-low-poly-female-character-creation-set) | Base 3D femenina y cientos de modelos de ropa/accesorios. | CC0 según la página. No es un paquete 2D anime. | Solo considerar una ruta futura de renderizado 3D a sprites. |

La investigación encontró recursos útiles para probar la composición y articulación, pero no todos responden al estilo anime final. **El primer objetivo de integración debe ser el que tenga partes realmente independientes, licencia clara y una prueba de ensamblaje superada.** No se han subido los ZIPs de terceros ni se marca ningún candidato como integrado.


## Añadidos de investigación (18-10-2026)

- **[RGS_Dev — Free CC0 Modular Animated Vector Characters 2D](https://rgsdev.itch.io/free-cc0-modular-animated-vector-characters-2d)** y [su ficha en OpenGameArt](https://opengameart.org/content/free-cc0-modular-animated-vector-characters-2d): la distribución original se anuncia como CC0. La ficha describe partes separadas, 2048×2048, cabeza/cabello/ojos/boca/cuerpo/mano/pie y seis familias de animación. El paquete es de estilo cartoon/top-down, no anime. Priorizarlo para pruebas de capas/alineación/pivotes después de inspeccionar el ZIP. No usar la copia de GameDevMarket: ese espejo presenta otro Pro License y marca “Allows usage with AI? No”; son términos de distribución diferentes.
- **[rhedak — Anime Character Creator](https://github.com/rhedak/anime-character-creator)**: generador procedural anime basado en anclas anatómicas y formas SVG separadas para pelo, cara, ropa y extremidades, con código MIT. Es una referencia muy cercana a la meta de un motor ligero sin checkpoint. La licencia MIT es para el código; su README explica que algunos diseños se basaron/trazaron desde referencias generadas con IA, así que no copiamos sus carpetas `ref/` ni `ref-out/` al dataset de IMAGE sin revisión independiente.

Estos candidatos todavía no están integrados en el repositorio: los registros son enlaces y decisiones de investigación, no una afirmación de que se descargaron o probaron los archivos.


## Nueva búsqueda ampliada: capas anime, herramientas y rutas 3D (18-10-2026)

### Candidatos con utilidad más directa

| Recurso | Qué trae realmente | Licencia declarada / cautela | Decisión para IMAGE |
|---|---|---|---|
| [Anime Girl and Boy Portraits — OpenGameArt](https://opengameart.org/content/anime-girl-and-boy-portraits) | ZIP de 3,5 MB según la ficha, con fuente GIMP XCF; la página describe dos retratos femeninos y dos masculinos y capas/componentes para variar cabello, ojos y boca. | CC0 según la ficha de OpenGameArt. La fuente exacta se debe conservar en el manifiesto. | **Primer candidato anime para descargar e inspeccionar**; extraer capas por separado solo después de comprobar XCF, transparencia y nombres. Es material de rostro/peinado, no cubre cuerpo entero ni piernas. Aún no descargado ni integrado. |
| [Kenney Modular Characters](https://kenney.nl/assets/modular-characters) / [ficha OpenGameArt](https://lpc.opengameart.org/content/modular-character-pack) | 425 PNG independientes, seis spritesheets y seis archivos vectoriales. | CC0 en la ficha original. | Banco técnico para ver capas, colocación y ropa intercambiable; el estilo plano/cartoon no sirve como dataset anime por defecto. |
| [Half Body Portrait — Female Cloths](https://opengameart.org/content/half-body-portrait-female-cloths) | Un ejemplo PNG de corsé/correas que necesita la plantilla de retrato de medio cuerpo enlazada por el autor. | Ficha CC0, aunque solicita atribución a Xenodora. | Prioridad baja: sirve como overlay de prueba y no como biblioteca de vestuario. |

### Herramientas de composición y generación (referencias, no packs de entrenamiento)

- [Open Peeps Studio](https://github.com/Hantuhan/peepstudio) usa la biblioteca de ilustraciones Open Peeps (CC0) y permite mezclar cabello, cuerpos y expresiones, y exportar SVG/PNG. El estilo dibujado es genérico/cartoon, no anime. Sirve para estudiar composición y experiencia de usuario; no asumir que el código de la app comunitaria comparte la licencia CC0 de los dibujos.
- [Anime Avatar — konard](https://github.com/konard/anime-avatar) anuncia licencia Unlicense para el repositorio y divide el renderizado en componentes SVG de cara, ojos, pelo, cuerpo, piernas y fondo, además de una ruta 3D. Es una referencia de arquitectura procedural; sus `reference-images`, modelos y otros recursos requieren revisión aparte y no se añaden al dataset.
- [VRoid Studio CC0 sample models — OpenGameArt](https://opengameart.org/content/vroid-studio-cc0-models) identifica un subconjunto concreto de modelos de muestras alpha como CC0; la propia ficha advierte que otros modelos de nombre parecido tenían condiciones distintas. No son PNG por piezas, pero se pueden evaluar en el futuro para renders ortográficos controlados a sprites, usando solo el subconjunto exacto con licencia confirmada.

### Exclusiones y criterios que evitan falsas soluciones

- Las láminas de comisiones o ejemplos de separación de capas que aparecen en búsquedas de imágenes son **referencias visuales**, no recursos reutilizables por defecto. No se descarga ni se entrena a partir de ellas sin licencia/autorización clara.
- [Thin Girl — ani mosity](https://queenofzan.itch.io/modular-character-sprite-thin-girl) sigue excluido de datasets generativos según las condiciones expresas de su autora; una licencia que permite importar/editar un sprite no equivale a permiso para entrenar IA.
- [Anime Characters — Technopeasant](https://opengameart.org/content/anime-characters) figura como CC0, pero su descripción dice que los borradores se inspiran libremente en Rei y Asuka de *Evangelion*. No lo selecciono para el corpus de entrenamiento: la licencia del archivo no resuelve por sí misma derechos sobre personajes de terceros.
- [Hachi Bases](https://opengameart.org/content/hachi-bases) se deja pendiente por la procedencia de la obra original citada por el publicador; no la trato como pieza aprobada solo porque la página muestre CC0.

### Orden recomendado de trabajo

1. Descargar el XCF de **Anime Girl and Boy Portraits**, revisar licencia/estructura y exportar una muestra de ojos, boca y peinados a PNG con alfa.
2. Descargar un paquete CC0 modular como Kenney o RGS_Dev para validar alineación, orden de capas, anchors y recoloración, pero mantenerlo separado de las referencias de estilo anime.
3. Probar una composición de cabeza/cabello/ojos/ropa con nuestras propias SVG si no aparece un paquete CC0 anime completo que tenga cuerpo, piernas y vestuario independientes.
4. Registrar por pieza: URL/autor/licencia, permisos separados de uso en motor, redistribución y entrenamiento, formato, tamaño/lienzo, transparencia, pivote y prueba de ensamblaje.

**Estado tras esta búsqueda:** añadí candidaturas y reglas de selección, no afirmo que los archivos descargables ya estén dentro del repo ni que se haya aprobado un solo activo para entrenamiento.


## Aplicación opcional para extraer piezas de imágenes autorizadas

- **[Anime Cutout Studio](https://github.com/gino07172002/anime-image-cutout-studio)** (código Apache-2.0) es una aplicación de escritorio con selección corregible por el usuario para separar personajes superpuestos, extraer partes como pelo/cabeza/torso/brazos/piernas y exportar PNG transparente, PSD por capas o árbol de esqueleto Spine. La propia documentación indica una descarga de aproximadamente **1,7 GB de modelos de terceros** y remite a `NOTICE` para sus licencias individuales. Es una herramienta para procesar entradas autorizadas, no una biblioteca de imágenes ni una autorización para cortar ilustraciones ajenas. La dejo como herramienta opcional, no como dependencia de la primera versión ligera.

## Más bases editables y cuerpos 3D encontrados

- [Face — marionline (OpenGameArt)](https://opengameart.org/content/face-4): ficha CC0 con un XCF de GIMP y varias variantes PNG de tono de piel. Puede ayudar con pruebas de recoloración y organización de capas, pero es un retrato/rostro, no un personaje completo ni una biblioteca de pelo y ropa.
- [Feminine Humanoid Base Mesh — GoldenThumbs](https://opengameart.org/content/feminine-humanoid-base-mesh): ficha CC0 con archivo Blender de un cuerpo estilizado sin cabeza. Solo ruta opcional para renderizar una silueta 3D a una vista 2D controlada; no proporciona partes 2D ni estilo anime acabado.

La selección sigue priorizando los activos **2D, de licencia clara y con componentes independientemente editables**. Las herramientas que separan imágenes existentes solo se usarán con material propio o cuyo permiso de adaptación esté comprobado; separar una imagen no cambia sus derechos.


## Paquetes descargados y examinados (18-10-2026)

Se descargaron ambos ZIP desde sus páginas originales, se comprobó la integridad del archivo y se inspeccionó el árbol extraído. **No se subieron los ZIP ni sus PNG al repositorio**: los enlaces originales siguen siendo la vía de descarga, y el catálogo registra el resultado del examen.

### 1) [Anime Girl and Boy Portraits — CC0, stevenburrow](https://opengameart.org/content/anime-girl-and-boy-portraits)

Descarga oficial directa: [allanime-11-28-2020.zip](https://opengameart.org/sites/default/files/allanime-11-28-2020.zip), **3.517.503 bytes**. El ZIP pasa la prueba de integridad e incluye:
- `AllAnime/NewAnime.xcf`: GIMP XCF v003, 1000×1000.
- `Sample1.png`–`Sample8.png`: PNG RGBA 1000×1000 cada uno.
- `SampleAll.png`: PNG RGBA 2000×4000.
- No trae archivo README, LICENSE, COPYING, NOTICE ni CREDITS; guardar la URL de la ficha como fuente de la declaración CC0.

La ficha declara CC0 y describe componentes editables/coloreables para cabello, ojos y boca. **Sirve para el módulo facial/peinados; no es un cuerpo entero ni contiene piernas/vestuario modular completo.** Todavía no extraje capas del XCF ni hice ensamblaje dentro de IMAGE.

### 2) [Customizable Character Pack — CC0, rubberduck](https://opengameart.org/content/customizable-character-pack)

Descarga oficial directa: [customizable_characters_w_samples.zip](https://opengameart.org/sites/default/files/customizable_characters_w_samples.zip), **252.884 bytes**. El ZIP pasa la prueba de integridad e incluye:
- `customizable_characters.xcf`: GIMP XCF v011, 64×96.
- `sample_character_01.png`–`sample_character_16.png`: PNG RGBA 64×96 cada uno.
- No trae archivo README, LICENSE, COPYING, NOTICE ni CREDITS; guardar la URL de la ficha como fuente de la declaración CC0.

Este es el primer paquete para probar **capas de cuerpo/ropa/pelo alineadas exactamente con nuestra resolución inicial 64×96**. El estilo es pixel/cartoon, no anime acabado. Se debe inspeccionar el XCF en GIMP para confirmar orden de capas y preparar una composición de prueba antes de darlo por integrado o meterlo al conjunto de entrenamiento.

### Resultado práctico y límite

Prioridad de pruebas: (1) inspeccionar capas/anchors del Character Pack 64×96; (2) revisar el XCF anime para ojos/boca/pelo; (3) solo después evaluar si las piezas se pueden mezclar en un compositor. No mezclar directamente ambos estilos en un dataset de entrenamiento coherente. La licencia de la página se registra en el catálogo, pero la autorización para redistribuir un archivo, usarlo en el motor y entrenar un modelo sigue siendo un registro de decisión separado.

