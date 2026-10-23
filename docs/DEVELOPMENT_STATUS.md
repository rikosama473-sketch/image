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
- Ajustada una aserción del validador que aún esperaba el título antiguo del visor; la prueba ahora comprueba el título actual y la explicación de compatibilidad de capas. El primer CI reportó ese desajuste y no se rebajó la validación funcional.
- Biblioteca de peinados: añadidas fichas que distinguen `parts_same_base`, `parts_realignable` y `reference_only`; el visor dispone de un filtro de montaje y una explicación de alineación sobre bases planas.
- Añadidas las dos referencias de Pinterest aportadas por el usuario como pendientes de inspección/licencia; registradas la guía de AiryOnline, la hoja compuesta de PNGEgg, la referencia de Syntelligence sobre coleta y el paquete modular HMLF001 con licencia CC BY-SA 4.0 declarada.
- Enriquecido el recurso CC0 de OpenGameArt con su formato XCF, clases de componentes y advertencia de que sus piezas se corresponden con su propia base. Los paquetes base-específicos no se etiquetan como universales.
- El validador del taller exige metadatos de compatibilidad en cada referencia, comprueba los dos paquetes de capas y mantiene las referencias Pinterest en revisión pendiente.
- El importador limita también la memoria estimada: no permite más de 80 millones de píxeles agregados entre las capas que crea (cada una con su respaldo), además de los límites por imagen y por archivo.

- Añadida navegación compartida entre constructor, biblioteca, taller de peinados, editor manual y generador local opcional.
- Ajustado el lanzador independiente del editor manual para servir la raíz del repositorio y resolver enlaces a otros módulos.
- Añadida una prueba de navegación al workflow de validación.
- El JSON nuevo del Constructor registra la ruta, etiqueta y estado de revisión de la ilustración base y su filtro de visualización.
- El Editor manual abre proyectos propios y JSON de Character Creator/Hairstyle Workbench. Compone cada pieza en una capa rasterizada editable y conserva su procedencia, categoría, estado, ruta y transformación de origen. Si existe una máscara dibujada en el Constructor, se importa como selección.
- La transferencia admite imágenes PNG/WebP/JPEG incrustadas o rutas locales seguras; rechaza URLs externas, rutas con traversal, JSON mayores de 120 MB, imágenes mayores de 8192 px por lado/40 MP y proyectos con más de 200 capas.
- Añadida la regresión `tests/test_project_handoff.py` al workflow de validación.
- Límite explícito: las variantes adicionales del Taller permanecen en su JSON original; la imagen base se identifica como ilustración completa y no se inventan capas semánticas ni píxeles ocultos.

## Validación

- Catálogo de peinados y filtro de montaje: commit `021031adfb0b8db9160819686292ee7523995640`; el primer intento detectó una aserción de título obsoleta en el validador. Corregida la expectativa sin rebajar el test; [CI 39634158944](https://github.com/rikosama473-sketch/image/actions/runs/39634158944) sobre el validador corregido = `success`.

- Navegación integrada: commit `846d2eb89c4ac128e4a3f2472eebd2b90dceb313`; [CI 39624819395](https://github.com/rikosama473-sketch/image/actions/runs/39624819395) = `success`.
- Transferencia JSON entre módulos y límites de importación: commit `5b23e11660e8e9bd1a47cdb879bb6bad42e9568a`; [CI 39627167742](https://github.com/rikosama473-sketch/image/actions/runs/39627167742) = `success`.
- Integración de `main` y recursos de ambas ramas: commit de dos padres `5e1f026c776d739f77a2dbc8f87723b6d480efb4`. Todos los workflows comprobados en ese commit terminaron en verde: [IMAGE tools 39628055744](https://github.com/rikosama473-sketch/image/actions/runs/39628055744), [asset generator 39628056149](https://github.com/rikosama473-sketch/image/actions/runs/39628056149), [Character Creator 39628056209](https://github.com/rikosama473-sketch/image/actions/runs/39628056209), [manual editor 39628056386](https://github.com/rikosama473-sketch/image/actions/runs/39628056386), [contact sheets 39628045965](https://github.com/rikosama473-sketch/image/actions/runs/39628045965) y [cutout smoke test 39628055986](https://github.com/rikosama473-sketch/image/actions/runs/39628055986).
- Límite agregado de píxeles de importación: commit `4713dad7ddb9568a619521a2930714f885052f0d`. Validaciones aprobadas: [Character Creator 39628772989](https://github.com/rikosama473-sketch/image/actions/runs/39628772989), [Character Creator 39628764656](https://github.com/rikosama473-sketch/image/actions/runs/39628764656), [manual editor 39628773148](https://github.com/rikosama473-sketch/image/actions/runs/39628773148), [generator without API key 39628772958](https://github.com/rikosama473-sketch/image/actions/runs/39628772958), [IMAGE tools 39628773209](https://github.com/rikosama473-sketch/image/actions/runs/39628773209) y [cutout smoke test 39628773178](https://github.com/rikosama473-sketch/image/actions/runs/39628773178).
- La transferencia está cubierta por pruebas de contrato, validación estática de HTML/JavaScript y CI. Todavía no se ha realizado una prueba E2E visual/interactiva que abra un proyecto real en un navegador y compruebe píxeles de salida.
- No se ha generado una imagen Diffusers real en el Ryzen 5 5600G ni medido consumo/tiempo/calidad en ese hardware; el motor local permanece opcional y no validado para ese equipo.

## Estado de integración con `main`

- Rama actual de trabajo: `work/easy-avatar-maker-2026-10`; commit de código más reciente comprobado: `4713dad7ddb9568a619521a2930714f885052f0d`.
- `main` sigue en `efb47f05b0906472062ff50b2e6fe575445ab38e`; no se movió ni modificó directamente.
- El commit `5e1f026c776d739f77a2dbc8f87723b6d480efb4` integra `main` como segundo padre y conserva las 37 rutas añadidas exclusivamente en `main`, incluidos los recursos generados de Pibara y `trabajo aparte/diseño.md`.
- `data/character-prompt-registry.json` se combinó por `run_id`: los seis registros de Pibara son únicos y las entradas compartidas eran idénticas.
- Después de integrar, la comparación con `main` era `ahead_by=250`, `behind_by=0`. El PR #19 está abierto, no fusionado y GitHub informa `mergeable=true`: [PR #19](https://github.com/rikosama473-sketch/image/pull/19).

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

Abrir el taller en navegador con el lanzador local y probar el filtro «Uso como capa»: comprobar que el paquete HMLF001 y los paquetes con licencia declarada aparecen en las categorías correctas, que las vistas de referencia no se presentan como recortes aprobados y que los dos enlaces Pinterest quedan pendientes. A continuación, ejecutar el recorrido visual Constructor/Taller → Editor manual, guardar/reabrir y exportar PNG transparente. No fusionar automáticamente el PR ni recomendar un checkpoint local sin una medición real.

## Continuación verificada — 2026-10-21

- Se corrigió `tools/avatar-maker/index.html`: el botón **Centrar capa** antes forzaba cada capa seleccionada a ocupar todo el lienzo (`w=W`, `h=H`), deformando recursos importados y eliminando su escala. Ahora centra por desplazamiento (`x=(W-w)/2`, `y=(H-h)/2`) y conserva ancho, alto y proporción.
- Commit de la corrección: `1629783844ffc6bc50436738fee66fcd710cbe69` en `work/easy-avatar-maker-2026-10`.
- Verificación local del cambio: se comprobó que el handler antiguo existía exactamente una vez y se sustituyó por el nuevo. **Las pruebas automatizadas/CI de este commit todavía no se han confirmado**, por lo que no se declara el cambio validado integralmente.
- La PR #19 sigue siendo la vía de integración; no se modificó `main` ni se fusionaron ramas.
- Generación visual pendiente: el paquete anatómico de Pibara registrado en `run-39500149462` produjo 3/4 vistas, con deriva de identidad y una vista frontal recortada; no son capas semánticas aprobadas. El workflow documenta que la cuota pública ZeroGPU se agotó y admite un secreto `HF_TOKEN` para aumentar cuota; no se afirma que ese secreto esté configurado.
- La prueba de regresión para el centrado ya se añadió en `tests/test_project_handoff.py` (commit `6e044a1f8aa1e939ed8d19302fc1e337f4a9fb34`). En el commit posterior `7f1cf5896486e9c217c8707439c27c73b77c957d` se ampliaron las pruebas de contrato para cubrir guardado/recarga de capas, metadatos de procedencia y exportación PNG del editor manual. Son aserciones estáticas de código; no equivalen a una prueba interactiva de navegador y aún falta confirmar su ejecución en CI.


## Continuación de verificación — 2026-10-21 (bloque 2)

- Commit de pruebas: `7f1cf5896486e9c217c8707439c27c73b77c957d`. Añade contratos para `saveProject()`/`openProject(file)`, persistencia y restauración de PNG de capa/copia de respaldo, máscara de selección, metadatos de procedencia, y composición/exportación PNG sin pintar un fondo opaco por defecto.
- La exportación de composición se verifica por contrato: `makeComposite()` parte de un canvas nuevo, dibuja solo capas visibles respetando opacidad y `exportCanvas()` codifica `image/png`. Esto no sustituye una inspección de los píxeles del archivo exportado.
- Estado honesto: el nuevo test y el test de centrado están escritos en la rama; la ejecución de la suite y la prueba visual E2E siguen pendientes de confirmación. No se ha modificado `main` ni fusionado el PR #19.
- Próximo paso: obtener el resultado de CI de estos commits; si la suite falla, corregir el fallo real. Luego realizar la prueba interactiva Constructor → guardar JSON → Editor manual → guardar/reabrir → exportar PNG transparente, antes de aprobar assets modulares de Pibara.


## Continuación prioritaria — corrección del generador local (2026-10-22)

- Detectado un defecto en el flujo del generador local: `generate_diffusion.py` guarda cada imagen dentro de un subdirectorio `run-...`, mientras que el servidor de interfaz buscaba PNG solo en el nivel inmediato del trabajo. Eso podía marcar como fallida una generación aunque existieran PNG válidos.
- Se corrigió el descubrimiento recursivo de PNG dentro de cada trabajo, conservando la ruta relativa segura bajo `outputs/generated`.
- El ciclo de trabajo distingue resultados completos, parciales y fallidos. Si se guardan algunas imágenes pero falla el resto, la interfaz conserva las imágenes válidas e informa cuántas produjo de las solicitadas.
- Añadidas pruebas para resultados anidados, generación parcial, fallo del motor con resultados existentes, ausencia de salida y validación del payload. El workflow principal ejecuta estas pruebas y el contrato del motor.
- Estado: la implementación está comprometida en la rama de trabajo; falta confirmar el resultado de CI de esta tanda antes de contabilizar la corrección como validada.
- La generación real mediante Diffusers continúa sin calificarse como validada para el hardware objetivo mientras no se prueben un modelo compatible y una inferencia real. No se presume que el motor genere imágenes sin un modelo suministrado.

- Añadida comprobación preliminar desde la interfaz local: botón **Comprobar requisitos del motor**, endpoint `/api/diagnostics`, comprobación de paquetes Python sin importar el runtime de ML, verificación de `model_index.json`, estado de LoRA y aviso explícito de que la prueba no descarga pesos ni ejecuta inferencia. El botón no aprueba calidad o rendimiento; solo reduce errores de configuración evitables.

- Se amplió la prueba del servidor local para recorrer por HTTP real la interfaz, sus archivos JS/CSS y `/api/diagnostics`, además de verificar la respuesta a un identificador de trabajo inválido. Se añadió comprobación de sintaxis del JavaScript independiente al workflow; estas pruebas deben terminar en verde antes de considerar cerrada la tanda.

- Se terminó el flujo de clasificación de piezas: la biblioteca local muestra categorías en español y conserva tanto la categoría reutilizable elegida como la categoría de origen de la extracción. Al volver a añadir una pieza, su procedencia categórica viaja con la capa y se conserva en el JSON del Constructor.

- El generador local ahora permite explorar carpetas de modelos Diffusers existentes mediante `/api/models` y el botón **Buscar modelos locales**. La búsqueda se limita a carpetas del proyecto y cachés conocidas, valida `model_index.json`, no carga pesos y no descarga nada. El usuario elige cuándo usar una ruta detectada y puede volver a ejecutar el diagnóstico.
