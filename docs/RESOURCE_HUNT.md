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
