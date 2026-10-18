# IMAGE — generador de personajes anime

Proyecto privado e independiente para crear un generador de personajes anime de un estilo controlado, con cambios de cabello, ropa, piernas y silueta, fondos transparentes o sencillos/estilizados y una ejecución objetivo de hasta aproximadamente **2 GB de RAM del sistema**.

**No forma parte de WordWaifu ni de CharacterWord.**

## Restricciones técnicas acordadas

- El generador propio se entrenará desde inicialización aleatoria: no usar Haruka v2, SDXL, Stable Diffusion ni otro checkpoint de generación como base.
- No usar DMD2 ni destilación de un modelo docente como arquitectura central.
- Un LoRA no es un modelo independiente: requiere un modelo base compatible. Las imágenes iniciales se consideran un conjunto de entrenamiento propio desde cero, no un LoRA.
- Primera prueba a 64 × 96 píxeles con una arquitectura convolucional pequeña. Las 100 imágenes son un experimento de viabilidad; no garantizan buena anatomía o variedad.
- Entrenamiento y generación son presupuestos separados. El objetivo de 2 GB para inferencia debe probarse en hardware real; no se afirma que entrenar entre en esa memoria.
- Para variar cabello, prendas y piernas de verdad, necesitamos anotaciones por atributo, y preferentemente piezas/capas alineadas. Las imágenes completas sin etiquetas no proporcionan automáticamente control modular.

## Estado actual del repositorio

La rama `main` ya contiene **516 PNG, 485 con nombres que empiezan por `from-PixAI-` y 0 con nombres numéricos**, con un total aproximado de 478.6 MB. Son datos de inventario tomados de la API de Git; todavía no se verificaron visualmente ni se aprobaron sus derechos de entrenamiento.

No he movido ni sobrescrito las imágenes existentes. Se añadirá un inventario local de dimensiones, transparencia, hash y posibles duplicados antes de seleccionar las primeras 100.

## Prioridad inmediata: conseguir piezas gráficas compatibles

Buscar bases de cuerpo, cabezas, ojos, cabello delantero/trasero, torso, brazos, manos, pelvis, piernas, zapatos y ropa en formatos transparentes y alineados. Cada paquete debe pasar por una revisión de licencia, inventario del ZIP y prueba de ensamblaje. Ver [docs/RESOURCE_HUNT.md](docs/RESOURCE_HUNT.md).

## Carpetas nuevas

- `assets/parts/`: recursos gráficos que se puedan redistribuir de acuerdo con sus licencias; no añadir archivos ajenos hasta revisar los términos.
- `data/training-labels.csv`: inventario de las imágenes existentes y plantilla de revisión/atributos.
- `data/asset-sources.json`: páginas originales, licencias y estado de revisión.
- `scripts/audit_dataset.py`: auditoría local de dimensiones, canal alfa, SHA-256 y hash perceptual básico.
- `docs/`: definición del modelo, criterios de datos y búsqueda de recursos.

## Primera ejecución de auditoría

Instala Python 3.10+ y las dependencias:

```bash
python -m pip install -r requirements.txt
python scripts/audit_dataset.py --root . --output data/image-audit.csv
```

El script no borra ni modifica imágenes; escribe únicamente un informe CSV. Para el entrenamiento, primero revisa las imágenes y completa los campos de licencia, autorización, cabello, ropa, piernas, pose y fondo. El entrenamiento debe excluir cualquier imagen sin autorización clara.

## Uso de PixAI

Los términos oficiales de PixAI dicen que no reclama la propiedad de las imágenes que tú generas y que puedes usarlas, pero también hacen responsable al usuario de no infringir derechos de terceros. Un nombre de archivo que contiene `from-PixAI` no demuestra por sí solo que sea un resultado tuyo ni que no represente un personaje ajeno. Véase [PixAI Terms](https://pixai.art/en/terms).

## Lo que todavía no está terminado

No hay un modelo entrenado, no se ha demostrado el límite de 2 GB y las imágenes de este repositorio todavía necesitan inspección visual y de procedencia. Los documentos nuevos preparan la siguiente fase sin afirmar que esas pruebas ya se han realizado.
