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



## Descarga reproducible desde las fuentes originales

El catálogo incluye [`scripts/fetch_asset_packs.py`](../scripts/fetch_asset_packs.py), que descarga únicamente desde las dos URL originales de OpenGameArt incluidas en una allowlist:

```bash
python scripts/fetch_asset_packs.py --pack all
# o, por separado:
python scripts/fetch_asset_packs.py --pack anime-portraits
python scripts/fetch_asset_packs.py --pack modular-64x96
```

- `anime-portraits`: archivo `allanime-11-28-2020.zip`, 3.517.503 bytes según la inspección registrada; retratos/capas de pelo, ojos y boca bajo CC0 declarado por su ficha.
- `modular-64x96`: archivo `customizable_characters_w_samples.zip`, 252.884 bytes; capas GIMP y 16 PNG RGBA de 64×96 bajo CC0 declarado por su ficha.

El script conserva descargas y extracción bajo `data/asset-cache/`, carpeta excluida de Git hasta la revisión. Verifica el tamaño esperado, ZIP/CRC, evita rutas ZIP traversal, enlaces simbólicos, miembros duplicados y expansiones excesivas, calcula SHA-256 y crea `acquisition-manifest.json` local. Si la URL cambia de contenido, se detiene en vez de extraer a ciegas. `--force` conserva copias anteriores como respaldo y nunca aprueba el uso para entrenamiento. El hash generado sirve para identificar el archivo descargado, pero no equivale a una firma criptográfica publicada por el autor.


## Nuevos candidatos anime modulares revisados (18-10-2026)

Esta ronda prioriza piezas que sirvan para montar personajes en la aplicación. **Compatibilidad para montaje y permiso para entrenar IA son dos decisiones distintas.** No se descargaron estos packs ni se copiaron sus imágenes al repositorio durante esta investigación; se registraron las fichas originales y sus condiciones visibles.

### 1) [HMLF001 Anime Boy 800px — LinXueLian](https://linxuelian.itch.io/customchar-hmlf001-malebust)

- La página declara **CC BY-SA 4.0** y ofrece varios ZIP: cuerpo base, Warlock, Shopkeeper, Heavy Scarf, Kawamuru Hair y Vampire Config.
- Indica piezas PNG separadas en carpetas numeradas de capas, una base de 600×800 px, y uso de imágenes apiladas en Ren'Py o un editor; los elementos de ciertos paquetes pueden mezclarse si comparten la misma base.
- **Uso propuesto:** primer candidato gratuito para probar composición anime por capas (cabello, expresiones, ropa y accesorios) con atribución y cumplimiento ShareAlike.
- **Límite:** es un personaje masculino de busto/parte superior; no resuelve por sí solo el cuerpo entero ni una biblioteca de piernas y calzado independientes.
- **Entrenamiento IA:** pendiente. La licencia de assets para juegos no se interpreta aquí como aprobación automática para entrenamiento generativo. Antes de incorporarlo al corpus, solicitar autorización expresa o revisar legalmente el uso exacto.

### 2) [ANime ZCharacter — Saeed Ahmed Tunio](https://saeedahmed126.itch.io/anime-zcharacter)

- La ficha describe PNG transparentes independientes: cabeza calva, cabello frontal/trasero, orejas, ojos/cejas/boca, torso y brazos, cintura, pantalones/piernas y zapatos. Es el candidato visualmente más cercano, entre los hallados en esta ronda, a un kit anatómico de cuerpo completo.
- **Atención al precio:** aunque el texto lo llama gratuito, el apartado de compra indica que se debe pagar un mínimo de **USD 1** para descargarlo. La página lista `main_hero.zip` (998 kB) y `Anime_Facial_Animations.zip` (53 MB).
- Los términos visibles permiten usos personales y comerciales y modificaciones, pero prohíben redistribuir los archivos originales. No se encontró una autorización explícita de entrenamiento IA.
- **Uso propuesto:** compositor privado/local tras adquirirlo y respetar los términos. No subir sus PNG originales al repositorio ni entrenar con ellos sin permiso explícito del autor.

### 3) [The Rose Charisma — Trines Studio](https://trinesstudio.itch.io/rose-charisma-modular-anime-male-sprite-pack)

- La página muestra 42 PNG de 768×1376 (24 combinaciones de vestuario/pose, 10 expresiones y 8 peinados), organizados para superponer outfit+pose, expresión y peinado. Precio mínimo mostrado durante la revisión: USD 9,69.
- La licencia de la ficha permite usar y modificar el recurso dentro de proyectos personales o comerciales, pero **prohíbe expresamente entrenar modelos de IA** y redistribuir los archivos originales.
- **Decisión:** referencia válida para estudiar cómo funciona un compositor y, si se adquiere, para montaje dentro de la aplicación conforme a sus términos; exclusión absoluta del dataset de entrenamiento.

### 4) [Half Human Battle Sprite — marionline / OpenGameArt](https://opengameart.org/content/half-human-battle-sprite)

La ficha indica CC0 y ofrece pequeños sprites con variantes de cazadora/cazador y estados alternativos. Son personajes terminados de pixel art, no partes separadas. Se registra como referencia secundaria para estados y animación, no como fuente principal del estilo anime de mayor resolución.

### Orden de prueba recomendado

1. **Probar primero los paquetes CC0 ya registrados localmente por el proyecto**: el Character Pack de 64×96 para verificar alineación del cuerpo/cabello/ropa, y el XCF de retratos anime para las capas de ojos/boca/peinado. Estos dos siguen siendo la ruta inicial porque no requieren comprar archivos.
2. Evaluar HMLF001 si necesitamos una prueba anime más detallada y aceptamos mantener la atribución y las obligaciones CC BY-SA.
3. Considerar ANime ZCharacter solo si el montaje requiere partes de cuerpo completo y se acepta la compra mínima; antes, confirmar con el autor permiso para entrenamiento si ese uso se vuelve necesario.
4. No incorporar The Rose Charisma al corpus generativo: sus términos prohíben ese uso.

En todos los casos la primera prueba de integración debe ser un montaje de muestra en una carpeta temporal, verificando transparencia, tamaño del lienzo, pivotes, orden de capas y licencias. La presencia de una URL en el catálogo no significa que el archivo haya sido descargado, probado o aprobado.


## Herramientas de edición y nuevas fuentes de referencia (18-10-2026)

Esta búsqueda también cubre aplicaciones para **abrir, editar, alinear, recolorear, exportar y animar** las piezas. Que el programa acepte un formato no cambia la licencia de la ilustración ni convierte el archivo en material autorizado para entrenar IA.

### Paquete de ilustraciones completas

**[Free Anime Character Sprites: Full-Body Portraits — FreeGameSprites](https://freegamesprites.com/en/packs/anime-portraits)**

- La ficha declara CC0 para cada uno de sus 40 PNG de 384×512; indica que la descarga incluye `README.md` y `LICENSE.txt`.
- Sus personajes aparecen sobre fondo transparente y muestran cuerpo completo, ropa y equipamiento, por lo que podrían servir para una galería de personajes, pruebas de interfaz o referencias visuales de estilo.
- **No es un kit modular:** cada imagen es una ilustración estática completa. No incluye capas de ropa, boca/ojos animados, rig o ciclos de movimiento. Un lienzo común tampoco garantiza pies y siluetas perfectamente alineados entre imágenes.
- La web aclara que su declaración CC0 resume el catálogo, no una auditoría independiente de los derechos. Antes de integrar archivos, revisar los textos del ZIP, los registros individuales y la procedencia. No aprobarlos automáticamente para entrenamiento.

### Aplicaciones para trabajar con las piezas

| Aplicación / documentación | Para qué sirve en IMAGE | Cautelas |
|---|---|---|
| [GIMP](https://www.gimp.org/) | Abrir los XCF de las fuentes ya registradas, revisar visibilidad y orden de capas, alinear componentes, exportar copias PNG con alfa. | Trabajar con copias; el permiso viene del recurso, no de GIMP. |
| [Krita](https://krita.org/) | Dibujar piezas propias, retocar las autorizadas y mantener rostro, cabello, ropa y extremidades en capas separadas. | Probar el PSD exportado antes de una importación a Live2D. |
| [Inkscape](https://inkscape.org/) | Abrir y editar SVG, recolorear piezas vectoriales y exportar PNG a la resolución requerida. | Código, muestras y arte de cada proyecto pueden tener licencias distintas. |
| [Live2D Cubism — importación PSD](https://docs.live2d.com/en/cubism-editor-manual/psd-import/) | Validar una separación detallada de ilustración y probar rigging/deformación de capas. Útil si posteriormente se quiere animar pelo, ojos, boca o ropa. | No es banco de arte ni concede derechos de uso sobre el PSD. Su guía de PSD confirma Photoshop y Clip Studio Paint como los editores validados para importación correcta. |
| [VRoid Studio](https://vroid.com/en/studio) | Crear personajes anime originales en 3D, variar cabello/ropa y renderizar referencias consistentes desde distintos ángulos; exporta modelos VRM. | No genera por sí mismo un kit 2D de PNG. Los recursos incluidos por pixiv no son CC0 y algunos tienen cláusulas propias; leer [las directrices oficiales](https://vroid.com/en/studio/guidelines), especialmente antes de basar una aplicación generadora pública en mallas/texturas de VRoid. |

### Flujo sugerido de uso

1. **Inventariar antes de editar:** registrar URL original, autor, licencia, formato, tamaño, transparencia y qué se permite hacer con cada recurso.
2. **Abrir una copia del archivo fuente:** para XCF, empezar por GIMP; para SVG, Inkscape; para crear piezas o reparar bordes, GIMP o Krita.
3. **Conservar el lienzo de referencia:** cada cabello, ojo, boca, prenda o extremidad debe exportarse sobre la misma dimensión y coordenadas cuando sea un kit por capas. Si la fuente trae pivotes/anchors, guardarlos en un manifiesto aparte.
4. **Hacer una prueba mínima de montaje:** rostro + pelo trasero + cabeza + pelo delantero + torso + ropa. Comprobar que las capas no dejan huecos, que los bordes alfa no tienen halos y que las prendas coinciden con la base.
5. **No confundir compatibilidad con licencia:** montaje local, distribución del paquete, uso comercial y entrenamiento generativo son revisiones separadas.
6. **Mantener el rastro de generación:** en `data/training-labels.csv`, completar `base_model_identifier`, `lora_identifiers` y `lora_weights_or_settings` cuando se conozcan. No adivinar esas columnas desde el nombre del archivo, ni cambiar el nombre original que permite encontrar la procedencia.

La descarga de una fuente es solo el primer paso. La integración requiere verificar los archivos reales, el permiso de uso previsto y una muestra montada correctamente.


## Nueva ronda: PSD anime editables y herramientas de separación (18-10-2026)

Esta ronda añade recursos visualmente cercanos al objetivo anime y dos proyectos que ayudan a diseñar el compositor. **Las capas deben poder montarse y conservar el mismo anclaje; la licencia de cada pack decide por separado si se puede modificar, redistribuir o entrenar con él.** Los archivos nuevos no se han descargado ni agregado a Git.

### 1) [Girl Sprites for Visual Novels — Pepo Kukuru](https://cucurbitapepo.itch.io/girl-sprites-for-visual-novel)

**Candidato prioritario para probar un PSD por capas.** La ficha de itch.io indica que los pagos están deshabilitados y el conjunto se puede obtener gratuitamente. La versión gratuita incluye 4 peinados delanteros, 4 traseros, expresiones reducidas y cuatro opciones de ropa; no incluye zapatos. Hay ZIPs de 12 MB para la versión gratuita/premium y de 97 MB para la versión completa; esta última incluye PSD y CLIP de alta resolución. La ficha declara **CC0 1.0** y afirma que no se usó IA generativa para crear el pack.

- Uso previsto: probar cambios de peinado, ropa, expresiones y mapas de degradado en GIMP, Krita o un editor PSD compatible.
- Límite: las piezas son capas de una ilustración de personaje, no una biblioteca independiente de cada mano, brazo, pierna y zapato.
- Revisiones pendientes: inspeccionar el ZIP real y su aviso CC0, anotar el archivo exacto y validar que las capas estén bien alineadas. La autora pide no revender el pack tal cual ni con cambios menores.

### 2) [Miu Sprites — Lia](https://liah0227.itch.io/miusprites)

PSD anime de **28 MB**, con compra mínima de USD 10. La ficha enumera tres outfits (escolar, casual y traje de baño), capas de color para cuerpo/cabello/ropa y capas para ojos, cejas, boca y rubor.

- Uso previsto: referencia premium para un compositor de novela visual con cambio de vestuario, color y expresión.
- Condiciones visibles: permite juegos personales y comerciales; en proyectos comerciales pide crédito a Lia y prohíbe vender el sprite o atribuirse su autoría.
- Entrenamiento: no aprobado; la página no concede expresamente permiso para entrenamiento generativo. No comprarlo solo con la expectativa de incorporarlo al dataset.

### 3) [ImageToLayers — separación de capas anime](https://imagetolayers.org/solutions/anime-layer-decomposition)

Herramienta web que anuncia exportación a capas PNG transparentes, ZIP o PSD. Su demostración muestra 29 capas —pelo frontal/trasero, rasgos faciales, ropa, calzado y accesorios—, pero la página aclara que es un ejemplo guardado y no garantiza el mismo resultado para cada imagen. El servicio usa créditos (20 por separación) y las exportaciones gratuitas llevan marca de agua.

- Uso previsto: comprobar si una ilustración que tenemos permiso de editar se puede separar rápidamente y cuánto retoque manual necesita.
- No usarla para procesar dibujos ajenos sin autorización. Separar una imagen no elimina los derechos de su autor. Revisar términos del servicio antes de guardar o redistribuir resultados.

### 4) [character_creator — uglycygnet](https://github.com/uglycygnet/character_creator)

Prototipo LÖVE2D de compositor modular con esqueleto jerárquico, articulaciones, animaciones idle/walk y datos de personaje separados de los datos de animación. Su licencia de código es MIT, pero el propio README describe módulos de arte como placeholders: **no es un paquete de imágenes listo para usar**.

- Uso previsto: referencia pequeña para pivotes de cabeza, hombro, codo, cadera y rodilla; organización por carpetas de cabello, cara, torso, brazos, manos, piernas, pies, ropa y accesorios.
- Decisión: estudiar la arquitectura; no confundir código MIT con derechos de arte ni copiar piezas que el repositorio no incluye.

### 5) [2D Character Parts Studio — meomeo-dev](https://github.com/meomeo-dev/2d-character-parts)

Proyecto público que documenta un flujo de 19 piezas transparentes y un pipeline por etapas: referencia global, torso, miembros inferiores, miembros superiores, cabeza y expresiones; incluye plantilla SVG y script de composición PNG. En la ficha revisada no aparece una licencia explícita de código.

- Uso previsto: estudiar la lista de partes y la secuencia de composición.
- Cautela importante: depende de APIs y modelos externos de generación de imágenes; eso puede generar costos y no coincide con el objetivo de tratar el repositorio como un banco de recursos ya autorizado. No adoptar código, muestras ni salidas hasta aclarar la licencia y los términos del proveedor.

### Secuencia recomendada tras esta búsqueda

1. Probar primero el PSD CC0 declarado de **Girl Sprites for Visual Novels**; la versión gratuita permite evaluar la estructura sin comprar recursos.
2. Montar un ejemplo con peinado frontal/trasero, expresión y cambio de ropa; comparar las capas exportadas con el canvas de destino.
3. Evaluar ImageToLayers solo con una imagen propia/autorizada si hace falta separar piezas que no existan por capas.
4. Usar los dos repositorios de código como referencias de estructura, sin importar contenido no autorizado y sin añadir una API de generación externa a la arquitectura por defecto.
5. Mantener el nombre original de cada imagen y los campos de modelo/LoRA por separado: sirven para reconstruir la procedencia, no para inferir licencia ni compatibilidad automáticamente.


## Nuevos sprites anime por capas: candidatos para montaje en la aplicación (18-10-2026)

Las siguientes páginas tienen capas de expresiones, ropa o peinados y por eso sirven para investigar un compositor visual-novel. Sus restricciones de entrenamiento y redistribución son diferentes; **ninguna de estas fichas nuevas queda aprobada para entrenamiento por el hecho de tener PSD o una descarga gratuita**. En esta ronda se registraron páginas y condiciones, no se descargaron los archivos.

### 1) [Clara — Fullbody Character Sprite (Memmo)](https://memmoxt.itch.io/clara-character-sprite)

- La versión gratuita trae un PSD de cuerpo entero de 750×1500; la edición de pago (mínimo USD 1) ofrece 1000×2000. La ficha declara capas de cuerpo, ropa, cabello, expresiones y accesorios, con 28 expresiones y posiciones izquierda/derecha.
- Puede ser útil para comprobar la experiencia de cambiar capas de un personaje completo dentro de una aplicación o juego.
- **Restricciones explícitas:** la autora prohíbe el entrenamiento de IA, redistribuir el archivo como recurso y añadir nuevos peinados, ropa, expresiones o colores fuera del sistema de capas proporcionado.
- Decisión: prototipo de montaje en el ámbito permitido por su guía; **excluido del entrenamiento** y de una biblioteca que redistribuya sus archivos.

### 2) [Visual Novel Sprites! (Breezy)](https://breezy-the-cat.itch.io/visual-novel-sprites)

- Archivo RAR de 18 MB, con PSD y PNG para cuatro personajes, múltiples expresiones y una configuración de animación tipo paper.
- La página anuncia CC0, pero el autor escribe expresamente “DO NOT USE MY WORK FOR GENERATIVE AI”.
- Decisión: la exclusión directa de IA se conserva como restricción obligatoria aunque aparezca lenguaje CC0 en la misma ficha. No incorporar este recurso a los datos de entrenamiento. La disponibilidad de los PSD puede servir para estudiar capas/expresiones dentro de las condiciones de la página.

### 3) [Maihi — Free Visual Novel Sprite (AR_0)](https://ar-0.itch.io/maihi-free-visual-novel-sprite)

- La ficha lista un ZIP de 8,7 MB con personaje de cuerpo entero de aproximadamente 1700×3200, tres atuendos, zapatos y accesorios conmutables, 12 bocas, cuatro cejas, parpadeo, seis emotes y un PSD detallado.
- La autora permite editarlo y usarlo en cualquier motor y solicita el crédito: “Sprite of Maihi (or the name you give her) by AR_0 (Link to this page)”.
- No se ha localizado una licencia estándar ni un permiso explícito para entrenamiento generativo en la ficha revisada.
- Decisión: posible prueba de montaje local con la atribución requerida; pedir aclaración de derechos antes de redistribuir los archivos o entrenar un modelo.

### 4) [VN Male SpritesMaker (Chulagames / chULang)](https://chulagames.itch.io/visualnovelspritebychulang)

- PSD gratuito de 2,8 MB, lienzo 900×1000 y encuadre hasta la cintura: cinco peinados, cinco atuendos, dos accesorios, ocho bocas, cinco pares de cejas, rubor y pupilas movibles.
- La página permite uso personal y comercial dentro de proyectos y solicita crédito al autor, pero prohíbe expresamente compartir, revender o redistribuir los archivos.
- No concede de forma clara permiso de entrenamiento generativo.
- Decisión: buen candidato para una prueba local de montaje de cabello, ropa y expresiones; no añadir el PSD ni sus exports a una biblioteca pública ni al dataset de entrenamiento sin permiso separado.

### 5) [Fem/Female Visual Novel Sprite Set 2 (Eros)](https://residentrabbit.itch.io/femfemale-visual-novel-sprite-set-2)

- La página describe un PSD de 2688×5810 con 14 colores de cabello, nueve tonos de piel, numerosos colores de ropa y expresiones; el ZIP indicado es de 55 MB.
- Aunque su ficha contiene una declaración CC0, también advierte explícitamente **“DO NOT USE FOR AI OR NFTS”**.
- Decisión: excluir del entrenamiento generativo. Registrar la condición explícita para no confundir la etiqueta CC0 con una autorización general de IA.

### Qué probar primero

Para una prueba con menor tamaño de descarga, empezaría por **VN Male SpritesMaker** (PSD de 2,8 MB, uso en proyectos permitido con crédito) o por **Clara** (PSD gratis de 3,8 MB, mejor control de cuerpo entero, con importantes restricciones). Para el entrenamiento propio, no usar ninguno de esos archivos sin una autorización que lo permita de forma clara; la condición de no IA prevalece en los packs que la expresan.

La prueba técnica debe abrir el PSD, cambiar una única capa, exportar PNG transparente a una carpeta temporal y comparar la posición de ojos, cabello, ropa, manos y calzado. No publicar ni incluir los archivos fuente en el repositorio durante esta prueba.
