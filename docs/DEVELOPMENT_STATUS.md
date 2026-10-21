# Estado de desarrollo de IMAGE

Fecha de revisión: 2026-10-21  
Rama de trabajo: `work/easy-avatar-maker-2026-10`  
Commit de base comprobado al iniciar este bloque: `96e6d6921af9fa98107afcb6279dd2f18fbfe8fe`  
PR de integración existente: [#19 — IMAGE Character Creator: AI, Anatomy & Asset Library](https://github.com/rikosama473-sketch/image/pull/19)  
Rama principal: `main` (no se modificó directamente).

## Identidad inmutable

IMAGE es un estudio local de creación de personajes e ilustraciones anime: biblioteca visual, constructor modular, editor por capas y generación/edición con IA opcional. No debe reducirse a un generador, un archivador o un conjunto de prototipos desconectados. Los flujos manuales deben seguir funcionando sin IA, sin claves remotas y sin GPU dedicada.

Equipo objetivo declarado: AMD Ryzen 5 5600G, 16 GB RAM y gráficos Radeon integrados. No hay mediciones verificadas todavía para inferencia de difusión local en ese equipo.

## Arquitectura y capacidades encontradas

- `tools/avatar-maker/`: constructor principal con ilustraciones PNG reales, panel de recursos, capas, transformaciones, visibilidad/opacidad, máscara de edición y guardado/recarga JSON. El flujo de edición IA usa una vista previa antes de aplicar el resultado como capa nueva. La separación semántica de una ilustración completa no se presume automáticamente.
- `tools/manual-character-editor/`: editor manual independiente con selecciones, extracción de regiones, borrador/restauración, máscaras y exportación PNG. Es el lugar para refinar una selección; no reconstruye automáticamente los píxeles ocultos.
- `tools/hairstyle-workbench/`: composición manual de piezas PNG y variantes del cabello; los recortes de muestra siguen siendo candidatos hasta revisión visual.
- `tools/visual-reference-library/`: catálogo de referencias e imágenes del repositorio, anotaciones locales, etiquetas, revisión de procedencia/licencia y recetas exportables. Las referencias enlazadas no equivalen a assets con permiso de redistribución/entrenamiento.
- `tools/image-creator/`, `ml/local_server.py` y `ml/generate_diffusion.py`: UI de inferencia local separada del servidor de herramientas. Requiere un modelo Diffusers compatible; no se presupone que haya pesos instalados. Rendimiento no verificado con el hardware objetivo.
- `data/training-labels.csv` y la documentación de `docs/`: registro de metadatos, procedencia y estrategia para seleccionar/validar un dataset. No entrenar automáticamente con la colección completa ni adivinar modelos/LoRAs a partir del nombre de archivo.

## Cambios realizados en este bloque

- Añadida navegación compartida entre constructor, biblioteca, taller de peinados, editor manual y generador local opcional.
- Ajustado el lanzador independiente del editor manual para servir la raíz del repositorio y resolver enlaces a otros módulos.
- Añadida una prueba de navegación al workflow de validación.
- El JSON nuevo del Constructor registra la ruta, etiqueta y estado de revisión de la ilustración base y su filtro de visualización.
- El Editor manual abre proyectos propios y JSON de Character Creator/Hairstyle Workbench. Compone cada pieza en una capa rasterizada editable y conserva su procedencia, categoría, estado, ruta y transformación de origen. Si existe una máscara dibujada en el Constructor, se importa como selección.
- La transferencia admite imágenes PNG/WebP/JPEG incrustadas o rutas locales seguras; rechaza URLs externas, rutas con traversal, JSON mayores de 120 MB, imágenes mayores de 8192 px por lado/40 MP y proyectos con más de 200 capas.
- Añadida la regresión `tests/test_project_handoff.py` al workflow de validación.
- Límite explícito: las variantes adicionales del Taller permanecen en su JSON original; la imagen base se identifica como ilustración completa y no se inventan capas semánticas ni píxeles ocultos.

## Validación

- Navegación integrada: commit `846d2eb89c4ac128e4a3f2472eebd2b90dceb313`; [CI 39624819395](https://github.com/rikosama473-sketch/image/actions/runs/39624819395) = `success`.
- Transferencia JSON entre módulos: commit `5b23e11660e8e9bd1a47cdb879bb6bad42e9568a`; [CI 39627167742](https://github.com/rikosama473-sketch/image/actions/runs/39627167742) = `success`.
- Pasaron validadores del constructor, taller de peinados y biblioteca; sintaxis del editor y puente de IA; diagnósticos de recorte; y las regresiones `tests/test_studio_navigation.py` y `tests/test_project_handoff.py`.
- La prueba de transferencia actual verifica estructura del JSON, despacho entre formatos, límites de importación y metadatos mediante tests de contrato/sintaxis. Todavía no se ha ejecutado una prueba visual interactiva del lienzo para abrir y exportar un proyecto real en el navegador.
- No se ejecutó una generación real de difusión ni se midió RAM/tiempo/VRAM en el Ryzen 5 5600G durante este bloque.

## Estado de integración con `main`

- Commit actual de integración: `5e1f026c776d739f77a2dbc8f87723b6d480efb4`, con primer padre la rama de trabajo y segundo padre `main` en `efb47f05b0906472062ff50b2e6fe575445ab38e`.
- Se preservaron las 37 rutas añadidas exclusivamente en `main`, incluidos los recursos generados de Pibara y `trabajo aparte/diseño.md`. No se eliminaron ni sustituyeron archivos exclusivos de la rama de trabajo.
- El único archivo que necesitó resolución semántica fue `data/character-prompt-registry.json`: se combinaron las ejecuciones por `run_id`, conservando los cinco registros de la rama y el registro `39622201248` de `main`. Resultado: seis IDs únicos; las ejecuciones compartidas no tenían diferencias.
- La rama ahora está `248` commits por delante y `0` por detrás de `main`. GitHub informa el PR #19 como `mergeable=true`, pero sigue abierto y sin fusionar. `main` no se modificó.
- Las ejecuciones de GitHub Actions para el commit de integración deben terminar antes de considerar validada la combinación completa. Los validadores del bloque de interoperabilidad sí pasaron en `5b23e11660e8e9bd1a47cdb879bb6bad42e9568a`.

## Problemas y límites conocidos

- El PR #19 sigue abierto. En la revisión inicial de esta sesión GitHub reportó `mergeable=false`; no se ha realizado merge ni se ha forzado ninguna referencia.
- Las vistas anatómicas generadas anteriormente se documentaron como borradores con deriva de identidad; no deben marcarse como referencias canónicas.
- El catálogo mezcla ilustraciones completas, recortes candidatos, referencias externas y recursos derivados. Mantener esas clases y su procedencia separadas.
- La generación por IA local depende de instalar manualmente un modelo compatible. La edición mediante proveedor remoto es opcional y requiere configurar la clave en el entorno.
- Las anotaciones de la biblioteca se almacenan en el navegador hasta exportarlas; no asumir sincronización automática entre equipos.

## Decisiones vigentes

1. No modificar `main` directamente mientras se consolida el PR de trabajo.
2. No fusionar ramas enteras solo por similitud de nombre; integrar por función y verificar el diff.
3. No descargar modelos grandes en esta fase.
4. Preservar imágenes originales, proyectos, metadatos y archivos generados con revisión pendiente.
5. No declarar como semántica una capa que en realidad sea un recorte de la ilustración completa.
6. Las pantallas, referencias y recetas no se cuentan como funciones implementadas si no existe la operación correspondiente.

## Siguiente tarea concreta

Confirmar que los workflows iniciados por el commit de integración terminan en verde. Después, probar en un navegador real ambos traspasos: Constructor → Editor manual y Taller de peinados → Editor manual, incluyendo visibilidad/opacidad, guardar/reabrir y exportar PNG transparente. A continuación evaluar el motor local IA en el Ryzen 5 5600G sin GPU dedicada; no dar por utilizable un checkpoint hasta medir memoria, duración y calidad. Mantener las referencias y máscaras candidatas marcadas como pendientes.
