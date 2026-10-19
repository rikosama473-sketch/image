# Prompt 1 — catálogo de identidades visuales

> Estado: primera pasada visual, no una extracción de prompts originales. La asignación de los nombres **Pibara**, **Chie** y **Sunna** a los grupos visuales es provisional porque los PNG revisados no conservan metadatos de prompt recuperables.

## Regla para consolidar prompts parecidos

La identidad base describe los rasgos estables del personaje. **No incluye tipo de peinado ni largo del cabello.** Esas opciones se guardan en la sección de variantes y se combinan con la identidad solo al generar una imagen.

- Conservar como detalles de identidad el color del cabello, el color de ojos cuando se ve claramente, el tono de piel, rasgos faciales y accesorios realmente recurrentes.
- Mover largo, corte, flequillo, trenzas, coletas y recogidos fuera del prompt base.
- Gafas, cintas y adornos se tratan como accesorios opcionales si no aparecen en todas las referencias.
- No agrupar personajes únicamente porque compartan estilo de dibujo, pose o color de cabello.
- Una referencia cuyo personaje no pueda identificarse queda como «pendiente», no se fuerza a uno de estos grupos.

## Estilo común recomendado

~~~text
polished 2D anime illustration, clean confident dark line art, smooth cel shading, controlled soft highlights, expressive face, consistent character design, simple light background, one character only, clear silhouette, reference-sheet composition, neutral fully clothed outfit unless another outfit is explicitly requested, no text, no watermark
~~~

Prompt negativo común:

~~~text
different character, changed eye color, changed hair color, inconsistent face, multiple people, duplicate body, extra limbs, extra fingers, distorted hands, blurry, low quality, text, signature, watermark
~~~

## Personaje 1 — Chie (asignación visual provisional)

**Rasgos estables observados:** mujer anime adulta; piel clara de tono cálido; ojos marrón/ámbar; cabello castaño oscuro con mechones inferiores o laterales más claros; rostro redondeado, nariz pequeña y rubor suave. Las gafas finas y la cinta púrpura aparecen en varias referencias, pero no en todas, así que deben ser controles opcionales.

**Prompt base — sin corte ni largo:**

~~~text
adult anime woman, warm light skin, large warm brown-amber eyes, soft rounded oval face, small nose, subtle cheek blush, dark chestnut-brown hair with a few lighter brown-beige strands, gentle confident expression, recognizable consistent facial identity, [HAIRSTYLE_VARIANT], [ACCESSORY_VARIANT], [OUTFIT_VARIANT], [POSE_AND_FRAMING], polished 2D anime illustration, clean confident dark line art, smooth cel shading, warm peach highlights, simple light background, one character only, no text, no watermark
~~~

**Variantes de cabello separadas (no incluirlas en la identidad base):**
- short layered bob
- asymmetrical bob with longer face-framing strands
- loose hair with long side locks
- half-up style or high ponytail

**Variantes de accesorios:**
- thin round glasses and purple headband
- no glasses, no headband
- plain neutral hair tie

**Referencias visuales vistas:** 0.png, 10.png, 15.png, 20.png, 25.png, 30.png, from-PixAI-2039891611644662625-1.png, from-PixAI-2040054293872617600-0.png, from-PixAI-2040105417460881711-3.png, from-PixAI-2040495574707665084-3.png, from-PixAI-2040509679436025490-1.png, from-PixAI-2040841113301050781-0.png, from-PixAI-2040841992312727659-0.png, from-PixAI-2054076421982483879-2.png.

## Personaje 2 — Pibara (asignación visual provisional)

**Rasgos estables observados:** mujer anime adulta; piel clara; ojos azules intensos; cabello negro o azul muy oscuro; cejas expresivas y rubor suave. Los adornos circulares blancos y las cintas azules son una señal visual útil, pero se mantienen como accesorio controlable.

**Prompt base — sin corte ni largo:**

~~~text
adult anime woman, light skin, large vivid blue eyes, dark navy-black hair, expressive slightly arched eyebrows, delicate nose, soft cheek blush, gentle playful expression, recognizable consistent facial identity, [HAIRSTYLE_VARIANT], [ACCESSORY_VARIANT], [OUTFIT_VARIANT], [POSE_AND_FRAMING], polished 2D anime illustration, clean confident dark line art, smooth cel shading, clear highlights, simple light background, one character only, no text, no watermark
~~~

**Variantes de cabello separadas:**
- side braids
- hair swept to one side with face-framing locks
- partly tied hair

**Variantes de accesorios:**
- white circular hair ornaments and blue ribbons
- white circular hair ornaments and red ribbons
- no hair ornaments

**Referencias visuales vistas:** from-PixAI-2053360197060539530-3.png, from-PixAI-2053428485067925823-0.png, from-PixAI-2053493732175854716-1.png.

## Personaje 3 — Sunna (asignación visual provisional)

**Rasgos estables observados:** mujer anime adulta; piel clara; cabello blanco plateado; rostro delicado, nariz pequeña y expresión tranquila o tímida. El color de ojos no se puede confirmar con seguridad en las muestras donde el flequillo los cubre; no fijarlo hasta comprobar una referencia despejada.

**Prompt base — sin corte ni largo:**

~~~text
adult anime woman, light peach skin, silver-white hair, delicate oval face, small nose, subtle blush, calm reserved expression, preserve the reference facial identity and the eye details that are actually visible, [HAIRSTYLE_VARIANT], [OUTFIT_VARIANT], [POSE_AND_FRAMING], polished 2D anime illustration, clean confident dark line art, soft cel shading, pale silver highlights, simple light background, one character only, no text, no watermark
~~~

**Variantes de cabello separadas:**
- long straight hair
- layered fringe partly covering the eyes
- soft face-framing strands

**Referencias visuales vistas:** from-PixAI-2052228182633453078-1.png, from-PixAI-2052475534055417979-1.png.

## Cómo usar los campos de variación

Sustituir los marcadores entre corchetes antes de generar. Ejemplo:

~~~text
[HAIRSTYLE_VARIANT] = short layered bob
[ACCESSORY_VARIANT] = thin round glasses and purple headband
[OUTFIT_VARIANT] = casual fully clothed outfit
[POSE_AND_FRAMING] = three-quarter portrait, front view
~~~

Para catalogar una imagen nueva:
1. Comparar rostro, ojos, color de cabello y accesorios estables con las referencias del personaje.
2. Si coincide, guardar la imagen como variante de ese personaje y anotar únicamente el peinado/ropa/pose en sus campos respectivos.
3. Si no coincide, crear una identidad pendiente; no copiar la imagen a una carpeta existente solo porque el dibujo se parece.
4. Mantener el nombre original del archivo y el enlace a la referencia.

## Alcance y limitaciones de esta pasada

- main contiene 759 imágenes rasterizadas según el árbol de Git revisado.
- Se examinaron visualmente ejemplos de los grupos castaño, negro/azul y blanco/plateado; **no se ha clasificado visualmente cada una de las 759 imágenes**.
- El extractor de metadatos no recupera el prompt de las muestras revisadas: sus PNG no contenían bloques de texto de prompt. Las descripciones de arriba son prompts reconstruidos visualmente, no los prompts originales de PixAI.
- Se encontró un solo par de archivos con el mismo SHA de Git; solo ese duplicado exacto se retira en esta rama. Las imágenes parecidas pero no idénticas se conservan hasta revisar su identidad.
- La petición menciona tanto conservar cinco identidades como quedarse con Pibara, Chie y Sunna. En esta primera pasada solo se asignaron tres grupos visuales con suficiente evidencia; no se inventan otras dos identidades ni se descartan archivos únicos para alcanzar una cifra.

## Registro de copia exacta retirada en esta rama

- Conservada: from-PixAI-2051739918923127209-0.png
- Copia exacta retirada: from-PixAI-2052089408399777103-1.png
- Motivo: ambos archivos tenían el mismo SHA de blob de Git; se elimina solo una copia byte por byte idéntica. La rama principal main no se modifica.
