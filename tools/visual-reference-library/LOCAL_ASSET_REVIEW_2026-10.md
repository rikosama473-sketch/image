# IMAGE — Auditoría visual inicial de la biblioteca local

**Fecha:** 2026-10-21  
**Fuente:** `tools/avatar-maker/assets/image-library.json`  
**Rama de trabajo:** `work/easy-avatar-maker-2026-10`

## Resultado ejecutado

El generador `scripts/build_visual_contact_sheets.py` se ejecutó con los archivos del repositorio y produjo un artefacto descargable de GitHub Actions.

| Comprobación | Resultado |
|---|---:|
| Entradas del catálogo procesadas | 764 |
| Archivos de imagen legibles | 764 |
| Archivos faltantes o ilegibles | 0 |
| Hojas de contacto producidas | 16 |
| Grupos de duplicados exactos por hash | 1 |
| Archivos sobrantes dentro de esos grupos | 1 |
| Revisión adicional de casi duplicados | Ahora se genera una cola de candidatos por hash perceptual (distancia ≤ 3); cada pareja requiere comprobación visual y nunca se elimina automáticamente. |

La revisión en hojas de contacto muestra que el catálogo local está formado principalmente por ilustraciones completas de personajes, a menudo con variaciones de pose, encuadre o peinado. No corresponde marcar esas ilustraciones como recortes de ojos o cabello listos para combinar. En el inventario inicial, los assets también están clasificados como `full_illustration`; los nombres genéricos no permiten saber qué forma de ojo o corte tiene cada personaje.

## Duplicado exacto encontrado

Los siguientes dos archivos son idénticos por contenido SHA-256 en el manifiesto de esta ejecución:

- `from-PixAI-2051739918923127209-0.png` (catálogo `local-0447`)
- `from-PixAI-2052089408399777103-1.png` (catálogo `local-0449`)

No se elimina ninguno automáticamente. El informe lo marca como candidato a consolidación para no borrar recursos sin confirmación.

## Piezas ya identificadas en el catálogo semántico

Hay cinco máscaras candidatas de cabello —bob, largo liso, coleta alta, coletas dobles y trenza lateral— y cuatro candidatos más de rostro/cabeza/cuerpo/ropa. Todas permanecen como `pending_visual_review`. No se consideran recortes utilizables hasta comprobar pelo pegado al rostro, artefactos, transparencia, línea y alineación.

## Próxima clasificación: cómo hacerlo sin falsear los resultados

1. Abrir las hojas de contacto y elegir imágenes cuya cara o peinado merezcan revisión detallada.
2. Añadir a cada referencia un nombre descriptivo y etiquetas de rasgos observables (forma exterior de ojo, iris, pupila, pestañas; largo de pelo, flequillo, mechones laterales, coleta, trenza).
3. Separar las imágenes de referencia de las piezas extraídas; guardar coordenadas, alineación y revisión del alfa si se hace un recorte.
4. Revisar los derechos de uso por separado. Una imagen que está en el repositorio o en Pinterest no tiene automáticamente permiso para redistribuirse ni para entrenamiento.
5. Generar nuevas imágenes solo después de que exista una especificación visual clara y un flujo de salida probado.

## Artefacto descargable de esta ejecución

[Hojas de contacto, manifiesto CSV y reporte de duplicados (GitHub Actions)](https://github.com/rikosama473-sketch/image/actions/runs/39604889219/artifacts/12347792216)

El artefacto de esta corrida fue creado en el commit `5ef16cf73a6d06f4c814b22fbec9ae2724b17b2e`. El catálogo de imágenes no cambió después de esa corrida; si se modifican los assets, habrá que regenerar las hojas.
