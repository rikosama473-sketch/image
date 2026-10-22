# DISEÑO
## Atlas visual de diseño de personajes anime — documento de trabajo

**Estado:** base visual + censo exhaustivo de fuentes · **Versión:** 0.2 · **Actualizado:** 21/10/2026 · **Formato maestro:** Markdown  
**Objetivo:** construir un catálogo grande, visual y consultable de peinados, ojos, iris, cejas, nariz, boca, rostro y combinaciones originales para diseñar personajes. Este material se mantiene separado del código principal del proyecto.

> **Cómo leer esta guía:** las miniaturas son referencias enlazadas a sus fuentes públicas. Abre la fuente desde cada imagen para verla en mayor tamaño y comprobar su contexto. Las imágenes de terceros no se consideran propiedad del proyecto ni se presentan como material libre de derechos. Antes de empaquetarlas localmente o redistribuirlas habrá que comprobar licencia, atribución y condiciones de uso.

---

## Índice

1. [Peinados y siluetas](#1-peinados-y-siluetas)
2. [Flequillos y marco del rostro](#2-flequillos-y-marco-del-rostro)
3. [Ojos: forma, pestañas e iris](#3-ojos-forma-pestañas-e-iris)
4. [Nariz, boca y proporciones](#4-nariz-boca-y-proporciones)
5. [Forma del rostro y lenguaje de diseño](#5-forma-del-rostro-y-lenguaje-de-diseño)
6. [Bibliotecas y tableros para ampliar](#6-bibliotecas-y-tableros-para-ampliar)
7. [Taxonomía para llegar a cientos de fichas](#7-taxonomía-para-llegar-a-cientos-de-fichas)
8. [Combinaciones originales iniciales](#8-combinaciones-originales-iniciales)
9. [Registro de fichas y control de calidad](#9-registro-de-fichas-y-control-de-calidad)

---

## Actualización de investigación — 21 de octubre de 2026

La biblioteca de IMAGE tiene una segunda vista orientada a búsqueda rápida. El documento de diseño sigue siendo una guía para reconocer las formas; el censo interactivo es el índice de fuentes, previews y permisos.

- [**Censo visual interactivo — 284 fichas con vistas previas registradas**](./censo-visual-interactivo.html): busca por nombre/rasgo y filtra por cabello, ropa, ojos, accesorios, tutoriales, colecciones o packs. Las advertencias rojas indican lo que viene mezclado o lo que necesita revisión.
- [Censo exhaustivo de fuentes — 153 URLs canónicas únicas](./censo-exhaustivo-fuentes-waifu-2026-10-21.md): 160 registros categorizados (incluye alias), fuentes de cabello, ropa, ojos, accesorios, tutoriales y packs con estado de licencia.
- [Índice JSON de referencia](./indice-visual-componentes.json): 284 registros con miniaturas capturadas de metadata/enlaces de fuentes y campos para rasgos objetivo, elementos extra, prompt, tipo de recurso, derechos y estado de placa monocroma.
- [Auditoría de bibliografía](./auditoria-bibliografia-censo-waifu-2026-10-21.md): URLs de los sitios consultados.
- [Atlas inicial de peinados y constructor de prompts](./atlas-peinados-interactivo.html): interfaz anterior enfocada en recetas de peinados y prompts para PixAI.

**Control de calidad:** 284 registros tienen URL de preview, pero las miniaturas aún no se han validado una por una dentro del navegador final; algunas URLs remotas podrían caducar o no cargar. La lista de 244 direcciones es única por normalización de URL, no por hash visual: el mismo dibujo alojado en dos plataformas puede seguir apareciendo más de una vez. No se han descargado o recortado las imágenes de todos los sitios.

**Placa monocroma:** 0 referencias cuadradas en blanco y negro tienen licencia de reutilización confirmada. Las búsquedas monocromas son candidatas, no assets terminados. Las páginas comerciales pueden permitir el uso de los resultados de arte mientras prohíben redistribuir los PSD/PNG fuente.

---

## 1. Peinados y siluetas

### Planchas de referencia

| Miniatura visual | Qué permite estudiar | Fuente |
|---|---|---|
| <a href="https://ar.pinterest.com/viktorsuarez9/referencia-anime-cabello/"><img src="https://i.pinimg.com/originals/73/7f/f0/737ff0f5af49749be0b6ba4460d503af.jpg" width="210" alt="Plancha numerada de 50 peinados anime"></a> | **50 siluetas de cabello.** Cortes cortos, medios y largos, ondas, trenzas, recogidos y variaciones de volumen. Es un mapa inicial para separar las siluetas sin confundirlas con el color. | [Abrir referencia original / tablero](https://ar.pinterest.com/viktorsuarez9/referencia-anime-cabello/) |
| <a href="https://www.pinterest.com/ideas/anime-female-ponytail-hairstyles/944451166577/"><img src="https://i.pinimg.com/originals/cb/c4/4f/cbc44f57d587d6afe46d25c133982c12.jpg?nii=t" width="210" alt="Nueve variaciones de peinado anime"></a> | **Nueve familias de peinado.** Suelto, coleta, coletas dobles, moños, trenzas, ondas, frente despejada y accesorios. | [Abrir referencia](https://www.pinterest.com/ideas/anime-female-ponytail-hairstyles/944451166577/) |
| <a href="https://jp.pinterest.com/pin/617274692708948689/"><img src="https://i.pinimg.com/originals/60/01/16/6001165fa910ea3737f5d025482e5d3d.jpg" width="210" alt="Variantes de coletas dobles"></a> | **Coletas dobles / twin tails.** Cambiar altura, longitud y punto de amarre cambia la silueta y la lectura de edad o energía. | [Abrir referencia](https://jp.pinterest.com/pin/617274692708948689/) |
| <a href="https://hairstyles.lokerroom.com/10-anime-hairstyles-with-bangs/"><img src="https://i.pinimg.com/originals/46/07/16/460716809a206cbe475c0e4b7c2bb4c2.jpg" width="210" alt="Variaciones de flequillo y corte bob"></a> | **Flequillo y bob.** Flequillo recto, lateral, irregular, mechones de marco y variaciones del corte corto. | [Abrir página de referencia](https://hairstyles.lokerroom.com/10-anime-hairstyles-with-bangs/) |

### Familias de peinado que deben convertirse en fichas individuales

| Familia | Variantes a distinguir visualmente |
|---|---|
| Corto | pixie, bob recto, bob asimétrico, bob redondeado, bixie, crop, garçon, undercut, rapado lateral, nuca corta |
| Medio | lob, shag, wolf cut, capas suaves, capas marcadas, corte en V, corte en U, puntas hacia fuera, puntas hacia dentro |
| Largo | liso pesado, liso liviano, capas largas, hime cut, corte en V, corte en U, mechones frontales largos, cabello hasta cintura, extralargo |
| Textura | lacio, ondas suaves, ondas profundas, rizo abierto, rizo espiral, afro voluminoso, crespo compacto, mechones húmedos, despeinado, electrizado |
| Recogido | coleta alta, media y baja; coleta lateral; doble coleta; moño alto, bajo y doble; semirrecogido; nudo superior; recogido desordenado |
| Trenzado | trenza simple, francesa, holandesa, espiga, corona, lateral, doble, trenzas pequeñas de marco, trenza incorporada al flequillo |
| Volumen y silueta | compacto, triangular, campana, redondeado, expandido lateral, alto en coronilla, pesado hacia atrás, levantado por viento |
| Rasgos distintivos | ahoge, cowlick, mechón sobre un ojo, mechón central, puntas en estrella, dos mechones largos delanteros, patillas largas, mechón de color distinto |

---

## 2. Flequillos y marco del rostro

El flequillo debe catalogarse separado del corte principal. Un mismo bob, cabello largo o coleta tiene una lectura muy diferente según la línea de la frente.

| Tipo | Rasgos que hay que registrar |
|---|---|
| Recto compacto | línea horizontal uniforme; puede ser pesado o ligero |
| Recto abierto | dos bloques separados al centro o en un punto ligeramente desplazado |
| Cortina | dos secciones que enmarcan sienes y pómulos |
| Lateral largo | mechón diagonal que dirige la mirada |
| Lateral corto | rompe la simetría sin cubrir demasiado el ojo |
| Despuntado | puntas irregulares y ritmos de mechones variables |
| Dentado | picos claros, separados y gráficos |
| Fragmentado | pequeños grupos de pelo con espacios visibles |
| Sobre los ojos | tapa ambos ojos de modo parcial o completo |
| Sobre un ojo | recurso asimétrico; comprobar que no sea igual en todos los personajes |
| Sin flequillo | frente despejada, raya al centro o lateral |
| Rizado | rizos definidos en la frente, sin convertir todo el volumen en una sola masa |
| Ahuecado | flequillo elevado que revela la línea frontal |
| Dos mechones frontales | enmarcan pómulos o mandíbula y sobreviven al recogido |
| Flequillo + mechón discordante | un solo mechón largo, claro u oscuro para romper la simetría |

**Control para futuras miniaturas:** cada ficha de flequillo debe incluir al menos frente y tres cuartos cuando sea posible, no solo un recorte aislado que oculte cómo se conecta con el resto del pelo.

---

## 3. Ojos: forma, pestañas e iris

### Planchas de referencia

| Miniatura visual | Qué permite estudiar | Fuente |
|---|---|---|
| <a href="https://kknews.cc/comic/ekmj8zz.html"><img src="https://i1.kknews.cc/3bOdmWRf7c1zCDtkOD54QbjAvZxywNc4ug/0.jpg" width="210" alt="Plancha de formas de ojos, pestañas, iris y brillos"></a> | **Plancha de ojos por componentes:** inclinación, apertura, pestañas, forma de iris y patrones de brillo. Lo importante es variar cada componente por separado. | [Abrir fuente](https://kknews.cc/comic/ekmj8zz.html) |
| <a href="https://www.impress.co.jp/newsrelease/2024/06/20240620-03.jpg"><img src="https://www.impress.co.jp/newsrelease/2024/06/2024062002-03.jpg" width="210" alt="Variaciones de iris, reflejos y cejas"></a> | **Iris, brillos y cejas.** Sirve para estudiar cómo pequeños cambios de reflejo, pupila y arco superior alteran el carácter. | [Ver imagen original](https://www.impress.co.jp/newsrelease/2024/06/2024062002-03.jpg) |
| <a href="https://storage.googleapis.com/dgzxjscixvclne/anime-eyes-nose-and-mouth.html"><img src="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/0a7c1336-2869-4384-bf36-847cb39be293/d6ac4hq-f3f65e84-d2af-4d09-a47d-964203de2619.jpg/v1/fill/w_1024%2Ch_1338%2Cq_75%2Cstrp/20_anime_eyes__12_noses__and_20_mouths_by_sbtrulz-d6ac4hq.jpg" width="210" alt="Lámina de ojos, narices y bocas de anime"></a> | **Muestra multiparte:** muchas formas de ojos, narices y bocas en una sola lámina. Algunas líneas son deliberadamente simples; estudiar la forma, no calcar el personaje. | [Abrir referencia](https://storage.googleapis.com/dgzxjscixvclne/anime-eyes-nose-and-mouth.html) |

### La ficha de ojo no es una única etiqueta

Registra los elementos por separado:

| Capa | Valores que deben explorarse |
|---|---|
| Contorno | redondo, almendrado, estrecho, ancho, caído, ascendente, triangular, cuadrado, parcialmente cerrado, monólido estilizado |
| Inclinación | neutra, exterior ascendente, exterior descendente, inclinación desigual entre ambos ojos |
| Apertura | muy abierta, media, fina, entrecerrada, párpado pesado, cansada, medio cerrada |
| Párpado superior | línea fina, gruesa, doble, gráfica, segmentada, sombreada, casi ausente |
| Pestañas | discretas, largas, abanico, puntas gruesas, agrupadas, una sola punta exterior, inferiores marcadas, casi inexistentes |
| Iris | circular, ovalado, vertical, estrecho, anillado, radial, degradado, dos tonos, patrón geométrico, patrón orgánico |
| Pupila | redonda, ovalada, vertical, estrella, rombo, corazón, cruz, anillo, múltiple, hendida, pequeña o casi invisible |
| Brillos | uno principal, dos puntos, banda horizontal, ventana cuadrada, estrella, rombo, brillo inferior, aro, reflejo múltiple, asimétrico |
| Detalle interior | rayos radiales, anillos concéntricos, motas, pétalos, constelación, fractura, remolino, patrón de cristal, patrón de reloj |
| Estilo de color | plano, dos tonos, degradado vertical, degradado radial, borde oscuro, borde luminoso, heterocromía, iris con anillo exterior |
| Lectura emocional | inocente, alerta, cansada, hostil, calculadora, curiosa, ausente, orgullosa, melancólica, sobrenatural |

**No repetir por accidente:** si dos personajes tienen la misma forma exterior, variar de manera consciente como mínimo dos capas internas (iris, pupila, brillo, pestañas o párpado). Cambiar únicamente el color no cuenta como diseño suficientemente diferente.

---

## 4. Nariz, boca y proporciones

| Miniatura visual | Qué permite estudiar | Fuente |
|---|---|---|
| <a href="https://www.animeoutline.com/how-to-draw-anime-and-manga-noses/"><img src="https://www.animeoutline.com/wp-content/uploads/2013/01/anime-noses.jpg" width="210" alt="Cinco niveles de simplificación de nariz anime"></a> | **Narices en tres cuartos, perfil y frente.** Desde marca mínima hasta nariz con puente, ala y sombra. | [AnimeOutline: narices](https://www.animeoutline.com/how-to-draw-anime-and-manga-noses/) |
| <a href="https://www.animeoutline.com/12-anime-facial-expressions-chart-drawing-tutorial/"><img src="https://www.animeoutline.com/wp-content/uploads/2017/06/facial_features_placement_anime_face.png" width="210" alt="Colocación proporcional de ojos, nariz, orejas y boca"></a> | **Proporciones básicas.** Comparar colocación de ojos, nariz, orejas y boca antes de personalizar el rostro. | [AnimeOutline: expresiones y proporciones](https://www.animeoutline.com/12-anime-facial-expressions-chart-drawing-tutorial/) |
| <a href="https://storage.googleapis.com/dgzxjscixvclne/anime-eyes-nose-and-mouth.html"><img src="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/0a7c1336-2869-4384-bf36-847cb39be293/d6ac4hq-f3f65e84-d2af-4d09-a47d-964203de2619.jpg/v1/fill/w_1024%2Ch_1338%2Cq_75%2Cstrp/20_anime_eyes__12_noses__and_20_mouths_by_sbtrulz-d6ac4hq.jpg" width="210" alt="Muestra comparativa de narices y bocas anime"></a> | **Variantes pequeñas de boca y nariz.** Útil para comparar formas sin distraerse con peinado, vestimenta ni color. | [Abrir lámina multiparte](https://storage.googleapis.com/dgzxjscixvclne/anime-eyes-nose-and-mouth.html) |

### Nariz

- Marca mínima: punto, coma o pequeño trazo.
- Puente corto con sombra lateral.
- Nariz definida por una sola curva.
- Punta visible en tres cuartos.
- Nariz con ala y fosa simplificadas.
- Perfil con puente recto, cóncavo o convexo.
- Sombra bajo la punta.
- Nariz gráfica de dos trazos.
- Nariz realista estilizada para diseños seinen.
- Nariz suave y pequeña para diseños de rasgos redondeados.

### Boca

- línea neutra corta;
- curva mínima ascendente o descendente;
- sonrisa cerrada;
- sonrisa ladeada;
- sonrisa abierta con bloque de dientes;
- boca abierta pequeña de sorpresa;
- boca triangular de estilo cómico;
- labios definidos con línea superior;
- labio inferior sugerido por sombra;
- boca apretada;
- puchero;
- temblor de labio;
- sonrisa cansada;
- sonrisa peligrosa;
- expresión inexpresiva con línea casi horizontal.

Para evitar bocas intercambiables, registrar forma, apertura, asimetría, grosor de línea y presencia de sombra como rasgos separados.

---

## 5. Forma del rostro y lenguaje de diseño

| Miniatura visual | Qué permite estudiar | Fuente |
|---|---|---|
| <a href="https://in.pinterest.com/pin/35958497009778271/"><img src="https://i.pinimg.com/736x/9a/4a/fe/9a4afeea3d938b63abd59fe6dce71bad.jpg" width="210" alt="Comparación de proporciones faciales anime por edad y tipo"></a> | **Rostro por proporciones y edad visual:** mejillas redondas, mandíbula afilada, rostro más largo y rasgos más maduros. No usar la edad como único indicador del diseño. | [Abrir referencia](https://in.pinterest.com/pin/35958497009778271/) |

### Variables de rostro

| Variable | Rango de exploración |
|---|---|
| Silueta general | circular, ovalada, corazón, diamante, cuadrada, alargada, triangular, trapecio suave |
| Mejillas | llenas, suaves, planas, angulosas, hundidas, con rubor marcado |
| Mandíbula | curva, estrecha, angular, ancha, suave, cuadrada, puntiaguda |
| Mentón | redondo, corto, fino, prominente, plano, dividido por sombra |
| Pómulos | discretos, altos, marcados, anchos, suavizados |
| Frente | corta, media, alta, cubierta por flequillo, despejada |
| Orejas | pequeñas, visibles, cubiertas, puntiagudas de fantasía, con accesorios |
| Asimetría | flequillo desigual, párpados diferentes, sonrisa ladeada, ceja elevada, marca facial |
| Edad visual | infantil estilizada, juvenil, adulta, madura; valorar proporciones completas y no solo el tamaño de los ojos |

---

## 6. Bibliotecas y tableros para ampliar

Estos enlaces son puntos de búsqueda, no una garantía de que todas las imágenes puedan descargarse o reutilizarse. Para cada elemento individual se debe conservar la fuente exacta.

| Recurso | Uso principal |
|---|---|
| [Animefacelab — biblioteca de referencias](https://animefacelab.com/) | Referencias de rostro y cabello, con etiquetas de ángulo y características. |
| [Animefacelab — bob corto de frente](https://animefacelab.com/references/hair-ref-001/) | Ejemplo de ficha con silueta, textura, volumen, flequillo y rasgos clave. |
| [CoolKidDoodles — anime eyes reference sheet](https://coolkiddoodles.com/anime-eyes-reference-sheet/) | Formas de ojos, reflejos, pestañas y ejercicios de referencia. |
| [AnimeOutline — guía de ojos](https://www.animeoutline.com/how-to-draw-anime-eyes-and-eye-expressions/) | Construcción y expresividad de ojos. |
| [AnimeOutline — expresiones faciales](https://www.animeoutline.com/12-anime-facial-expressions-chart-drawing-tutorial/) | Cambios de expresión y colocación de rasgos. |
| [Pinterest — referencias de ojos anime](https://mx.pinterest.com/dilanserr09/anime-eyes/) | Tablero amplio para descubrir nuevos diseños; verificar cada imagen y su autor. |
| [Pinterest — formas de ojos](https://cl.pinterest.com/asda227/eye-shapes-most-anime-lol/) | Contraste entre contornos y aperturas. |
| [Pinterest — cabello anime](https://ar.pinterest.com/viktorsuarez9/referencia-anime-cabello/) | Búsqueda de peinados diversos. |
| [Pinterest — hair cuts](https://ar.pinterest.com/dimspro/hair-cuts/) | Cortes de cabello, siluetas y variaciones. |
| [Pinterest — ojos y cabello](https://ar.pinterest.com/1mluz/eyes-hair-references/) | Referencias combinadas. |
| [AnimeWorld — guía de rostros](https://animeworld.com/howtodraw/animagess/2a-faces.html) | Ojos, nariz, boca, orejas, forma facial y cabello. |

---

## 7. Taxonomía para llegar a cientos de fichas

El catálogo no debe ser una lista plana de nombres. Cada elemento tendrá un ID, una miniatura, etiquetas y una fuente. Una ficha puede combinar etiquetas de distintas capas, pero no debe confundirse una combinación generada con una referencia real.

### IDs propuestos

- `HAI-0001`: peinado/silueta
- `BNG-0001`: flequillo
- `EYE-0001`: contorno del ojo
- `LASH-0001`: pestañas y párpado
- `IRI-0001`: iris y pupila
- `GLT-0001`: brillos y reflejos
- `BRW-0001`: cejas
- `NOS-0001`: nariz
- `MTH-0001`: boca
- `FAC-0001`: forma de rostro
- `EXP-0001`: expresión
- `COM-0001`: combinación original de piezas

### Campos obligatorios de una ficha

| Campo | Qué guardar |
|---|---|
| ID | Identificador estable, nunca reutilizado |
| Nombre | Nombre corto y legible en español |
| Categoría / subcategoría | Por ejemplo, cabello → corto → bob asimétrico |
| Miniatura | Imagen pequeña que se vea dentro del documento |
| Enlace de origen | Página original desde donde se consultó la referencia |
| Autor / licencia | Si se puede averiguar; si no, marcar **pendiente de verificar** |
| Rasgos observables | 2–5 detalles que expliquen por qué la pieza es diferente |
| Variaciones cercanas | Enlaces a estilos parecidos, sin duplicar la ficha |
| Compatibilidad | Formas de rostro, longitudes o estilos con los que combina |
| Estado | descubierto, verificado, catalogado, duplicado o descartado |
| Nota de originalidad | Qué habría que modificar para convertirlo en un diseño propio |

### Lotes de expansión visual

1. **Cabello:** cortes cortos, medios y largos; textura; flequillos; recogidos; trenzas; vista frontal, perfil, tres cuartos y espalda.
2. **Ojos:** contorno, ángulo, apertura, párpado, pestañas, iris, pupila, brillos, paletas y patrones.
3. **Rostro:** forma general, mandíbula, mentón, mejillas, nariz, boca, cejas y orejas.
4. **Expresiones:** neutral, alegría, tristeza, furia, miedo, sorpresa, vergüenza, sospecha, cansancio, sonrisa contenida, risa abierta y expresión sobrenatural.
5. **Lenguajes gráficos:** ojos suaves, líneas angulares, formas geométricas, pestañas mínimas, iris ornamental, estilo limpio de TV, sombreado dramático, acabado de ilustración y diseños más caricaturescos.
6. **Combinaciones:** elegir piezas independientes y describir por qué funcionan juntas; no asumir que todos los componentes comparten automáticamente el mismo estilo.

---

## 8. Combinaciones originales iniciales

Estas son propuestas de combinación, no referencias copiadas ni imágenes que ya estén dibujadas. Servirán como briefs para producir miniaturas propias con un estilo coherente.

| ID | Pelo | Ojos | Rostro / boca | Idea de lectura |
|---|---|---|---|---|
| COM-0001 | bob asimétrico con un mechón largo | almendrados descendentes, iris radial | mentón fino, sonrisa casi invisible | calma observadora con una amenaza implícita |
| COM-0002 | largo liso con raya lateral | ojos estrechos, párpado superior pesado | mandíbula angulosa, boca recta | autoridad fría sin recurrir a cejas permanentemente fruncidas |
| COM-0003 | ondas cortas y puntas hacia fuera | ojos redondos con pupila pequeña | mejillas suaves, boca ladeada | energía caótica y sentido del humor |
| COM-0004 | doble coleta baja irregular | ojos ascendentes, brillos geométricos | rostro corto, puchero mínimo | apariencia juguetona con una mirada calculadora |
| COM-0005 | corte corto peinado hacia atrás | iris oscuro con aro fino | cejas rectas, nariz de pocos trazos | persona reservada y disciplinada |
| COM-0006 | cabello rizado voluminoso | ojos anchos, reflejos múltiples | labios definidos, pómulos suaves | presencia cálida y expresiva |
| COM-0007 | trenza lateral con mechones sueltos | iris de dos tonos y pestañas discretas | nariz mínima, sonrisa cansada | carácter práctico, experiencia y vulnerabilidad |
| COM-0008 | hime cut con puntas rectas | ojos estrechos con brillo en banda | rostro alargado, labios pequeños | elegancia rígida y autocontrol |
| COM-0009 | corte en capas, volumen en coronilla | ojos de apertura desigual | ceja levemente elevada, sonrisa asimétrica | ironía y desconfianza |
| COM-0010 | recogido alto con mechones delanteros | iris anillado, pupila vertical | mandíbula fina, boca neutra | personaje con elemento sobrenatural |
| COM-0011 | cabello corto mojado o pegado | ojos cansados, pestañas casi ausentes | sombra nasal lateral y labios secos | escena de desgaste físico, no glamur |
| COM-0012 | pelo muy largo con ondas amplias | ojos redondos con patrón de pétalos | mentón suave, sonrisa contenida | apariencia amable que no debe quedar genérica |

---

## 9. Registro de fichas y control de calidad

### Próximo lote a clasificar

| Estado | Categoría | Objetivo |
|---|---|---|
| En curso | Cabello | Separar las siluetas de las planchas en fichas individuales, eliminar duplicados y registrar fuente por cada referencia. |
| Pendiente | Ojos | Construir miniaturas por capa: forma, pestañas, iris, pupila y brillo, evitando que todas las opciones sean el mismo ojo con distinto color. |
| Pendiente | Rostro | Añadir nariz, boca, cejas, mandíbula y proporciones por separado. |
| Pendiente | Combinaciones | Preparar combinaciones originales y, cuando sea posible, ilustraciones de prueba consistentes entre sí. |
| Pendiente | Formato descargable | Exportar una versión Word/PDF con cuadrículas de miniaturas y enlaces, además del Markdown que se puede mantener en GitHub. |

### Criterios para aceptar una nueva ficha

- [ ] Incluye miniatura visible, no solo el nombre de un estilo.
- [ ] Conserva el enlace exacto de origen.
- [ ] Su etiqueta dice qué rasgo la distingue.
- [ ] No es un duplicado de otra ficha.
- [ ] Tiene licencia/atribución registrada o el estado queda marcado como desconocido.
- [ ] La referencia se categoriza por separado de cualquier adaptación original.
- [ ] La imagen pequeña sigue siendo legible al verla en una cuadrícula.

**Regla editorial:** una colección de enlaces no equivale a un atlas visual terminado. La meta es que cada referencia importante pueda reconocerse por la miniatura y el nombre, y que cada ficha explique cómo variar ese rasgo sin convertir todos los personajes en copias con colores distintos.

---

## Fuentes de esta primera base

- [AnimeOutline — colocación de rasgos faciales](https://www.animeoutline.com/12-anime-facial-expressions-chart-drawing-tutorial/)
- [AnimeOutline — narices anime](https://www.animeoutline.com/how-to-draw-anime-and-manga-noses/)
- [Animefacelab — referencias de cabello y rostro](https://animefacelab.com/)
- [CoolKidDoodles — referencia de ojos anime](https://coolkiddoodles.com/anime-eyes-reference-sheet/)
- [Pinterest — referencias de cabello](https://ar.pinterest.com/viktorsuarez9/referencia-anime-cabello/)
- [Pinterest — ojos y cabello](https://ar.pinterest.com/1mluz/eyes-hair-references/)


---

## 10. Planchas numeradas: de la imagen al nombre del peinado

La idea es que cada imagen funcione como un mapa. Se conserva la plancha completa, se numeran mentalmente sus cuadros de izquierda a derecha y de arriba abajo, y después cada número recibe un nombre descriptivo y un prompt que permita recrear **ese tipo de peinado**, no solo “pelo bonito”.

### Plancha A — veinte variantes de coletas, trenzas y recogidos

**Referencia original:** [Pinterest — Low pigtails drawing / Hairstyle sketch](https://jp.pinterest.com/pin/395542779792570224/)

**Imagen de la plancha (20 miniaturas):**

<a href="https://jp.pinterest.com/pin/395542779792570224/"><img src="https://i.pinimg.com/736x/b5/d5/e7/b5d5e76ccb2447c49a7e10c4ce196fc3.jpg" alt="Plancha con 20 estilos de cabello, numerados por posición" width="560"></a>

La imagen original no tiene números impresos. Esta guía les asigna números por posición: fila 1 = 1–4, fila 2 = 5–8, fila 3 = 9–12, fila 4 = 13–16, fila 5 = 17–20. La identificación es descriptiva y sirve como índice; no pretende ser el nombre oficial del ilustrador.

| Nº | Nombre para el catálogo | Rasgos visuales que conviene nombrar |
|---:|---|---|
| 1 | Coletas dobles altas | Dos colas, puntos de amarre altos, volumen medio, mechones sueltos cerca de las sienes |
| 2 | Coletas dobles bajas | Dos colas a la altura de la nuca, caída suave, silueta baja |
| 3 | Coletas dobles finas y rectas | Dos colas delgadas, poco volumen, caída casi recta |
| 4 | Coletas dobles largas y gruesas | Dos colas largas, mechones densos, volumen notable |
| 5 | Coletas segmentadas tipo burbuja | Dos colas separadas en segmentos por varias ataduras |
| 6 | Coletas altas con volumen redondeado | Dos colas altas, masas de pelo amplias y redondeadas |
| 7 | Coletas cortas con ligas pequeñas | Dos coletas cortas, amarres discretos, puntas a la altura de la cabeza o cuello |
| 8 | Coletas cortas con puntas hacia fuera | Coletas cortas, extremos levantados, silueta juguetona |
| 9 | Coletas largas retorcidas | Dos colas largas con mechones en espiral o torsión visible |
| 10 | Coletas largas con rizos en las puntas | Base recogida, longitud amplia, puntas rizadas |
| 11 | Coletas dobles onduladas | Dos colas largas, onda suave en la mayor parte del largo |
| 12 | Dos trenzas laterales | Dos secciones trenzadas, una a cada lado de la cabeza |
| 13 | Dos moños altos con mechones rizados | Moños dobles sobre la cabeza y mechones largos rizados a los lados |
| 14 | Coletas dobles altas extralargas | Amarres altos, gran longitud, colas que caen por debajo de los hombros |
| 15 | Semirrecogido con coleta | Parte superior recogida; cabello restante queda suelto |
| 16 | Coletas dobles con amarres ocultos | Dos colas; las ligas quedan tapadas por mechones de cabello |
| 17 | Coletas bajas rizadas | Dos colas bajas con rizos definidos |
| 18 | Coleta lateral con lazo grande | Una cola desplazada a un lado; accesorio voluminoso en el amarre |
| 19 | Moños dobles con mechones laterales largos | Dos moños y dos mechones que enmarcan la cara |
| 20 | Coletas dobles texturizadas y despeinadas | Dos colas con mechones irregulares, volumen desigual y puntas sueltas |

### Cómo se codifica cada peinado para PixAI

**No alcanza con escribir “twin tails” o “long hair”.** Para obtener una forma más controlada, registrar el peinado en componentes independientes. PixAI y otros generadores de difusión suelen interpretar mejor las descripciones concretas en inglés, por eso los prompts siguientes usan etiquetas inglesas y las explicaciones quedan en español. Los resultados varían según el modelo, LoRA, peso de etiquetas y parámetros.

| Componente | Qué especificar | Ejemplos de etiquetas para probar |
|---|---|---|
| Familia principal | Corte o estructura que organiza el cabello | `twin tails`, `ponytail`, `braid`, `bun hairstyle`, `half-up hairstyle`, `bob cut`, `layered long hair` |
| Cantidad y simetría | Una cola, dos colas, dos moños, lado único, simétrico o asimétrico | `twin tails`, `single side ponytail`, `double buns`, `asymmetrical hairstyle` |
| Altura del amarre | Coronilla, alto, medio, nuca, lateral | `high twin tails`, `mid-height ponytails`, `low twin tails`, `side ponytail` |
| Largo | Hasta orejas, mandíbula, cuello, hombros, pecho, cintura, muslos | `short pigtails`, `shoulder-length hair`, `waist-length hair`, `thigh-length hair` |
| Grosor/volumen | Delgado, medio, denso, voluminoso, compacto | `thin ponytails`, `thick voluminous twin tails`, `compact hair silhouette` |
| Textura | Recta, ondulada, rizada, trenzada, retorcida, despeinada | `straight hair`, `wavy hair`, `curly ends`, `twisted twin tails`, `messy hair` |
| Flequillo | Recto, abierto, lateral, cortina, dentado o ausente | `blunt bangs`, `curtain bangs`, `side-swept bangs`, `wispy bangs`, `no bangs`, `exposed forehead` |
| Frente | Totalmente cubierta, parcialmente cubierta o visible | `forehead covered by bangs`, `partially exposed forehead`, `fully exposed forehead` |
| Raya y nacimiento | Raya al centro, lateral, zigzag, mechón frontal, nacimiento despejado | `center part`, `side part`, `zigzag part`, `loose front strands` |
| Marco facial | Mechones junto a sienes, mejillas y mandíbula | `face-framing strands`, `long sidelocks`, `cheek-length side locks` |
| Puntas | Rectas, hacia fuera, hacia dentro, rizadas, dentadas | `flipped-out ends`, `inward-curled ends`, `blunt ends`, `spiky tips` |
| Amarre/accesorio | Goma, cinta, lazo, pinza o sin accesorio visible | `small hair ties`, `large ribbon bow`, `concealed hair ties`, `hair clips`, `no hair accessories` |
| Orden | Pulido, con algunos mechones sueltos, despeinado | `neat hairstyle`, `a few loose strands`, `tousled hairstyle` |
| Vista necesaria | Frontal para leer flequillo; tres cuartos y perfil para leer el volumen | `front view`, `three-quarter view`, `side view`, `hairstyle reference sheet` |

**Regla de construcción:** escoger una etiqueta de cada grupo necesario, no amontonar sin criterio sinónimos contradictorios. Por ejemplo, no mezclar `high twin tails` con `low twin tails`, ni `blunt bangs` con `no bangs` en el mismo prompt.

### Prompt maestro reutilizable para PixAI

Usá esta plantilla cuando quieras generar una vista del peinado sin cambiar el diseño del personaje. Reemplazá los campos entre corchetes por las características elegidas:

**Prompt positivo (inglés):**

```text
masterpiece, best quality, anime character design, clean professional anime lineart,
[character identity and established art style],
[hairstyle family], [number and symmetry of tied sections],
[attachment height and position], [hair length], [hair thickness and volume],
[hair texture], [bangs type], [forehead coverage], [parting],
[face-framing strands], [ends shape], [hair accessories],
clear readable hair silhouette, separated hair locks, coherent hair roots and strand flow,
hair design study, head and shoulders, front view, neutral expression,
plain light background, no text, single character
```

**Negative prompt (inglés):**

```text
worst quality, low quality, blurry, messy unreadable hair silhouette, fused hair strands,
random extra ponytails, extra buns, extra braids, asymmetrical ties when symmetry is required,
hair accessories not specified, bangs covering eyes unless requested, bald, receding hairline,
multiple people, duplicate character, collage, grid, text, labels, watermark, logo,
cropped top of head, cropped hair tips, out of frame
```

**Para obtener una lámina con muchas opciones:** cambiá `single character` por `hairstyle variation sheet, 4 columns, 5 rows, twenty separate numbered hairstyle studies` y pedí fondo uniforme. Sin embargo, muchos generadores deforman el texto, los números y la cantidad de cuadros. Para un resultado fiable, generá cada estilo individualmente y montá la plancha en un editor después.

### Prompts por número — estilos de la Plancha A

Los prompts de esta tabla son **bloques específicos para añadir al prompt maestro**, no prompts completos. Añadí el color del cabello, el modelo/LoRA de estilo y el diseño de personaje por separado.

| Nº | Bloque de prompt (inglés) |
|---:|---|
| 1 | `high twin tails, two symmetrical ponytails attached high on the back of the head, medium volume, loose temple strands, clean smooth hair flow, forehead partially exposed` |
| 2 | `low twin tails, two symmetrical ponytails tied near the nape, soft natural fall, moderate length, understated hair ties, relaxed silhouette` |
| 3 | `thin straight twin tails, two narrow symmetrical ponytails, low hair volume, long straight strands, fine tapered ends, minimal accessories` |
| 4 | `thick long twin tails, two dense voluminous ponytails, heavy flowing hair masses, long tapered tips, clear separation between left and right tails` |
| 5 | `bubble twin ponytails, two high ponytails divided into several rounded segments by small hair elastics, evenly spaced sections, distinct bubble silhouette` |
| 6 | `high full twin ponytails, two high ponytails with rounded voluminous bases, fluffy hair masses, curved outer silhouette, balanced left-right volume` |
| 7 | `short twin pigtails, two small ponytails tied close to the sides of the head, small discreet hair ties, short ends near the neck, compact silhouette` |
| 8 | `short outward-flipped twin tails, short paired ponytails with tips flicking outward, playful sharp ends, medium-high attachment points, lightweight hair volume` |
| 9 | `long twisted twin tails, two long symmetrical ponytails with visible rope-like twists, defined spiral sections, smooth roots and tapered ends` |
| 10 | `long twin tails with curled ends, two long ponytails, straight upper lengths, large soft curls concentrated at the tips, controlled separated curls` |
| 11 | `long wavy twin tails, two symmetrical ponytails with continuous soft S-waves, flowing strands, medium volume, naturally tapered ends` |
| 12 | `twin braids, two separate three-strand braids falling on either side of the head, visible braid crossings, tied ends, neat symmetrical structure` |
| 13 | `double space buns with long curled sidelocks, two rounded buns high on the head, long spiral locks framing both cheeks, exposed crown, playful but tidy silhouette` |
| 14 | `extra-long high twin ponytails, two high attachment points, very long thick ponytails falling below the waist, flowing tapered strands, broad dramatic silhouette` |
| 15 | `half-up ponytail hairstyle, upper half of the hair gathered into one ponytail at the back of the crown, lower half left loose, layered face-framing strands, visible separation between tied and loose sections` |
| 16 | `twin ponytails with concealed elastics, two symmetrical ponytails, each hair tie wrapped and hidden by a strand of hair, smooth roots, seamless polished attachments` |
| 17 | `low curly twin pigtails, two ponytails tied near the nape, defined ringlets and springy curls, curls concentrated along the lengths, soft face-framing strands` |
| 18 | `single side ponytail with oversized ribbon bow, one ponytail placed to one side of the head, large bow clearly attached at the base, long flowing tail, asymmetrical silhouette` |
| 19 | `double buns with long side locks, two compact buns placed symmetrically on the upper sides of the head, two long loose locks framing the face, clear separation between buns and loose hair` |
| 20 | `messy textured twin ponytails, two ponytails with uneven loose strands, layered flyaways, irregular ends, slightly asymmetrical volume, intentionally tousled but clearly readable structure` |

### Ejemplo: diseñar un peinado largo desde sus partes

Este ejemplo sirve cuando no se quiere copiar un nombre genérico como “long anime hair”. Ajustá cada parte hasta llegar a la forma que necesitás.

**Nombre catalogable:** cabello extralargo en capas, con flequillo cortina abierto, raya central suave y mechones largos para enmarcar el rostro.

| Parte | Decisión del ejemplo | Cómo cambiarla |
|---|---|---|
| Largo principal | cintura | hombros, pecho, cadera, cintura, muslos |
| Corte/capas | capas largas, puntas en V suave | una sola longitud, U, V profunda, capas escalonadas |
| Volumen | medio; concentrado desde media melena | pegado a la cabeza, volumen en coronilla, volumen lateral |
| Textura | ondas amplias desde la mitad del largo | liso, ondas suaves, rizos, ondas solo en puntas |
| Raya | central, ligeramente irregular | lateral, sin raya visible, zigzag |
| Flequillo | cortina en dos partes | recto, lateral, wispy, dentado, sin flequillo |
| Frente | parcialmente visible entre las dos secciones | cubierta, casi despejada, totalmente despejada |
| Marco de cara | dos mechones que llegan al pecho | sienes cortas, pómulos, mandíbula, mechones asimétricos |
| Puntas | afinadas y algo separadas | rectas, redondeadas, hacia fuera, dentadas |
| Accesorios | ninguno | horquillas, lazo, cinta, joya o broches |
| Silueta general | larga, elegante, claramente separada del torso | compacta, triangular, expansiva, asimétrica |

**Prompt positivo de ejemplo (inglés):**

```text
masterpiece, best quality, anime character design, long waist-length layered hair,
soft deep V-shaped back silhouette, medium natural volume, large loose waves starting
below the shoulders, smooth crown, subtle center part, open curtain bangs split into
two clear sections, partially exposed forehead, two long face-framing sidelocks reaching
the chest, tapered separated ends, visible individual hair locks, coherent strand direction,
hair flowing behind the shoulders, no hair accessories, clean professional anime lineart,
front three-quarter view, head and upper torso, plain light background
```

**Negative prompt de ejemplo (inglés):**

```text
short hair, bob cut, pixie cut, high ponytail, twin tails, buns, braids,
blunt full-covering bangs, hair covering both eyes, short sidelocks, blunt uniform ends,
excessive random flyaways, tangled strands, extra hair accessories, text, watermark,
multiple views, collage, cropped hair
```

> Este es un ejemplo de cómo describir el peinado por componentes, no una afirmación de que el pin [OC ideas 13](https://jp.pinterest.com/pin/1137299712187575540/) muestre exactamente esta combinación. Esa referencia queda incluida para comparar diseños de OC; antes de crear una ficha numerada para sus elementos hay que revisar la imagen concreta y no inferir sus rasgos solo por el título de Pinterest.

### Formato que tendrá cada nueva plancha

Cuando se añada otra referencia, no dejarla como un enlace suelto. Usar esta ficha:

| Campo | Contenido |
|---|---|
| ID de plancha | `SHEET-HAI-000X` |
| Imagen completa | Miniatura visible y enlace al original |
| Distribución | Número de columnas × filas y total de cuadros |
| Método de numeración | Izquierda a derecha, arriba abajo |
| Leyenda | Número, nombre del estilo, partes diferenciadoras |
| Prompt por opción | Bloque positivo específico para PixAI |
| Negative prompt | Rasgos que deben evitarse solo en ese estilo |
| Estado de inspección | Verificado visualmente / pendiente de revisar |
| Crédito y uso | Página fuente, autor si se conoce, condiciones de uso por verificar |

### Referencias de planchas

- [Plancha A — 20 peinados, Pinterest](https://jp.pinterest.com/pin/395542779792570224/)
- [Plancha de inspiración para personajes OC, Pinterest](https://jp.pinterest.com/pin/1137299712187575540/)

**Última sincronización (22/10/2026):** el censo visual y el índice JSON contienen 284 registros, 253 candidatos de imagen directa y 5 vistas de embed de Pixiv. No se pudo renderizar el HTML mediante el visor remoto de solo lectura del entorno, de modo que las miniaturas aún no se consideran validadas una por una en el navegador final. La sintaxis JavaScript del visor fue comprobada. La deduplicación perceptual y las placas cuadradas monocromas con licencia siguen pendientes.

**Última ampliación de categorías (22/10/2026):** el censo llegó a 284 registros con referencias de calzado anime, tiaras, tutorial de accesorios, kanzashi, cinturones y chokers. Siete nuevas referencias se etiquetaron como candidatas y no como assets reutilizables, porque autoría o licencia aún no se confirmaron.

**Última actualización (22/10/2026):** el índice consolidado llegó a 284 registros tras añadir tutoriales y recursos de tiaras, calzado, kanzashi, pendientes, chokers y sistemas modulares de personajes. Incluye 267 candidatos de imagen directa y 5 embeds Pixiv; los previews no se han cargado uno por uno en el navegador final, y la deduplicación perceptual sigue pendiente. Ninguna placa B/N cuadrada cuenta con licencia de reutilización confirmada.

**Última ampliación (22/10/2026):** 284 fuentes registradas con miniaturas; 279 candidatas de imagen directa y 5 embeds Pixiv. La investigación amplió accesorios/calzados y añadió documentación de herramientas que separan flequillo, laterales, pelo principal y adornos en capas. La página HTML se sincronizó desde el JSON y pasó comprobación de sintaxis, pero no se pudo comprobar visualmente cada miniatura por bloqueo del visor remoto.
