# Segunda pasada de QA del censo visual — 22 de octubre de 2026

**Proyecto:** IMAGE  
**Rama examinada:** `work/interactive-hairstyle-atlas-2026-10`  
**Alcance:** consistencia de datos y revalidación de fuentes de referencia.  
**Naturaleza del índice:** investigación de referencias; no equivale a una biblioteca de assets aprobados.

## 1. Comprobaciones estructurales

Se compararon los registros de `trabajo aparte/indice-visual-componentes.json` con el arreglo integrado en `trabajo aparte/censo-visual-interactivo.html`. Para evitar falsos positivos, el arreglo se leyó con seguimiento de corchetes y llaves balanceados, respetando las cadenas entre comillas.

| Prueba | Resultado |
|---|---:|
| Registros del índice JSON | 339 |
| IDs únicos en JSON | 339 |
| URLs fuente exactas únicas en JSON | 339 |
| URLs de miniatura registradas | 315 |
| Registros PixAI | 58 |
| Registros integrados en el HTML | 339 |
| IDs del HTML coincidentes con JSON | 339 de 339 |
| URLs fuente del HTML coincidentes con JSON | 339 de 339 |
| Enlaces locales del menú con destino existente en la rama | 9 de 9 |

Esta pasada confirma la **coherencia estructural** entre ambos ficheros. No certifica que las 315 miniaturas carguen al abrir el documento en cualquier navegador, ni que URLs diferentes representen ilustraciones visualmente distintas. Tampoco es una auditoría individual de permisos de cada obra.

## 2. Fuentes Pixivision revisadas

### Ya incluida en el censo: resumen editorial de peinados

[Hairstyle Illustration Roundup — A Trip to the Salon](https://www.pixivision.net/en/a/11971), publicada el **12 de septiembre de 2026**, reúne temas como cortes cortos y bob, pelo largo y ondulado, flequillos, trenzas, coletas, twin-tails y moños. La URL ya está registrada como `CENSUS-A-13`; **no debe contarse como fuente nueva**.

### Candidata adicional: índice general de peinados

[Pixivision — artículos etiquetados #hairstyles](https://www.pixivision.net/en/t/85) mostraba **122 artículos** en la consulta del 22 de octubre de 2026 y recogía, entre otros, entradas de 2026 sobre coletas, medias coletas, trenzas y flequillo recto. La URL exacta `/en/t/85` no aparece entre los 339 registros del índice consolidado consultado. Queda anotada como **candidata para una futura incorporación**, aún no añadida ni contada.

### Discrepancia de idioma en Gothic Lolita

Existe una página inglesa [Drawings Featuring Gothic Lolita Fashion — What We Wear in the Shadows](https://www.pixivision.net/en/a/10939), publicada el **25 de agosto de 2025**. El registro `CENSUS-B-08` del JSON consultado usa `https://www.pixivision.net/ms/a/10939`, la ruta de la edición malaya, mientras el título y el texto descriptivo del registro están en inglés.

Esto parece una discrepancia de localización, no una segunda obra. La corrección recomendada es cambiar el enlace del registro existente a la edición inglesa y sincronizar la misma URL en el HTML; **esta pasada no ha modificado esos dos ficheros grandes**.

### Referencia de taxonomía que ya existe

[Drawings of Hairstyles, Hair Colors, and Hair Accessories — Uniquely You](https://www.pixivision.net/en/a/10057), de **23 de agosto de 2024**, organiza referencias de peinados, colores de pelo y accesorios capilares. Ya está representada en el índice como `EXT-PXV-001`; tampoco debe sumarse otra vez.

## 3. Límite de licencias

Las páginas de Pixivision son colecciones editoriales que enlazan o presentan obras de artistas. Que una imagen sea visible en una colección no concede permiso general para descargarla, recortarla, distribuirla junto a IMAGE ni usarla para entrenar IA. La decisión debe evaluarse para cada obra original y para cada finalidad.

Se mantiene por tanto el estado documentado: **cero placas cuadradas monocromas con permiso de reutilización confirmado**. Los registros pendientes no deben mostrarse como recursos aprobados.

## 4. Siguiente orden de trabajo recomendado

1. Corregir la discrepancia de idioma de `CENSUS-B-08` en JSON y HTML, manteniendo un solo registro para esa obra.
2. Decidir si se añade `/en/t/85` como índice de descubrimiento y etiquetarlo como colección, no como ilustración individual.
3. Priorizar una comprobación visual de las miniaturas de las fuentes elegidas para la primera versión, anotando carga y coincidencia con la obra original.
4. Continuar los 96 casos de licencia o precio incierto documentados en la auditoría de calidad. Para cada candidato, separar permiso de uso dentro del programa, redistribución de archivos y entrenamiento de IA.

## Documentos de referencia

- [Censo visual interactivo](./censo-visual-interactivo.html)
- [Atlas de peinados](./atlas-peinados-interactivo.html)
- [Índice estructurado de componentes](./indice-visual-componentes.json)
- [Auditoría de calidad del censo de 339 registros](./auditoria-calidad-censo-339-registros.md)
- [Censo profundo de fuentes](./censo-exhaustivo-fuentes-waifu-2026-10-21.md)
