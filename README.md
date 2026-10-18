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

El árbol actual de `main` contiene **759 imágenes: 728 nombres que empiezan por `from-PixAI-` y 31 nombres numéricos**, con un total de **706.409.784 bytes (aprox. 706,4 MB)**. El manifiesto se ha sincronizado con esas 759 rutas, conservando anotaciones anteriores y dejando las 213 filas nuevas pendientes. Se conserva cada nombre original porque se usa como pista para rastrear la generación; el modelo base y la(s) LoRA se registran en columnas separadas, nunca se deducen automáticamente del nombre. Las imágenes todavía no están aprobadas para entrenamiento.

No he movido ni sobrescrito las imágenes existentes. Aún falta ejecutar la auditoría local de dimensiones, transparencia, hashes y posibles duplicados antes de seleccionar las primeras 100.

## Prioridad inmediata: conseguir piezas gráficas compatibles

Buscar bases de cuerpo, cabezas, ojos, cabello delantero/trasero, torso, brazos, manos, pelvis, piernas, zapatos y ropa en formatos transparentes y alineados. Cada paquete debe pasar por una revisión de licencia, inventario del ZIP y prueba de ensamblaje. Ver [docs/RESOURCE_HUNT.md](docs/RESOURCE_HUNT.md).

## Carpetas nuevas

- `assets/parts/`: recursos gráficos que se puedan redistribuir de acuerdo con sus licencias; no añadir archivos ajenos hasta revisar los términos.
- `data/training-labels.csv`: inventario de las imágenes existentes y plantilla de revisión/atributos.
- `data/asset-sources.json`: páginas originales, licencias y estado de revisión.
- `scripts/audit_dataset.py`: auditoría local de dimensiones, canal alfa, SHA-256 y hash perceptual básico.
- `docs/`: definición del modelo, criterios de datos y búsqueda de recursos.

## Herramientas locales

### Revisión visual y etiquetas

Abre [tools/dataset-reviewer/index.html](tools/dataset-reviewer/index.html) en el navegador o consulta su [README](tools/dataset-reviewer/README.md). Selecciona la carpeta raíz del clon local y carga opcionalmente `data/training-labels.csv`. La interfaz muestra 24 imágenes por página, permite filtrar y editar etiquetas y exporta un CSV. No sube imágenes ni modifica originales.

### Descargar los primeros paquetes gráficos CC0

Con Python 3.10+ no hace falta instalar dependencias extra para conseguir los ZIP de las fuentes originales y dejarlos en una caché local excluida de Git:

```bash
python scripts/fetch_asset_packs.py --pack all
```

Esto obtiene dos paquetes de OpenGameArt con tamaño esperado registrado: **Anime Girl and Boy Portraits** (rostro, ojos, boca y pelo; estilo anime pero sin cuerpo/piernas) y **Customizable Character Pack** (fuente GIMP y 16 ejemplos de 64×96; modular y alineado, pero pixel/cartoon). El script comprueba tamaño e integridad, calcula SHA-256, comprueba rutas ZIP inseguras y extrae bajo `data/asset-cache/`. Si el publicador cambia el archivo, el script aborta para que se revise manualmente. No mezcla los dos estilos, no marca los archivos como permitidos para IA, y no los añade automáticamente a Git. Ver [guía de recursos](docs/RESOURCE_HUNT.md).

Para refrescar deliberadamente un paquete existente conservando la copia anterior:
```bash
python scripts/fetch_asset_packs.py --pack anime-portraits --force
```

### Auditoría de dimensiones y duplicados

Instala Python 3.10+ y las dependencias:

```bash
python -m pip install -r requirements.txt
python scripts/audit_dataset.py --root . --output data/image-audit.csv
python scripts/sync_training_labels.py --root .
```

La auditoría no borra ni modifica imágenes; escribe un informe CSV con dimensiones, modo, alfa, SHA-256 y hash perceptual básico. La sincronización incorpora nuevas rutas a `data/training-labels.csv` sin borrar etiquetas revisadas. Para entrenar, completa también los estados de licencia/autorización y las etiquetas de cabello, ropa, piernas, pose y fondo.

## Uso de PixAI

Los términos oficiales de PixAI dicen que no reclama la propiedad de las imágenes que tú generas y que puedes usarlas, pero también hacen responsable al usuario de no infringir derechos de terceros. Un nombre de archivo que contiene `from-PixAI` no demuestra por sí solo que sea un resultado tuyo ni que no represente un personaje ajeno. Véase [PixAI Terms](https://pixai.art/en/terms).

## Lo que todavía no está terminado

No hay un modelo entrenado, no se ha demostrado el límite de 2 GB y las imágenes de este repositorio todavía necesitan inspección visual y de procedencia. Los documentos nuevos preparan la siguiente fase sin afirmar que esas pruebas ya se han realizado.


### Rastro del modelo base y LoRA

En `data/training-labels.csv` usa `base_model_identifier`, `lora_identifiers` y `lora_weights_or_settings` para recordar qué modelo base y qué LoRA(s)/pesos se usaron al producir una imagen. El nombre del archivo se conserva intacto y la asociación se debe confirmar manualmente. Esto ayuda a agrupar imágenes por origen, pero no convierte automáticamente ninguna imagen en apta para entrenar.
