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

- Añadida navegación compartida en el constructor, biblioteca, taller de peinados, editor manual y generador local.
- Añadidos enlaces del generador local (puerto 8765) hacia los módulos servidos en el puerto 8766; el enlace indica que se trata de otro servidor.
- Ajustado el lanzador Python del editor manual para servir desde la raíz local del repositorio, de forma que sus enlaces relativos a los otros módulos resuelvan también en modo independiente. Sigue vinculado únicamente a loopback.
- Actualizado el comienzo del README para expresar la identidad modular actual y describir cómo abrir los módulos sin presentar la IA como requisito.
- Añadida una prueba estática de navegación que comprueba la presencia de los cinco módulos, la resolución de rutas locales y las rutas de vuelta desde la UI de inferencia.

## Validación

- Base preexistente: el texto de PR #19 reportaba tres trabajos CI verdes para un commit anterior de su rama; eso no sustituye la comprobación de este nuevo commit.
- Este conector permite leer/escribir GitHub y consultar ejecuciones/estados, pero no ejecuta directamente las pruebas unitarias en el equipo del usuario.
- Después de publicar este bloque, revisar los jobs de GitHub Actions asociados al nuevo commit. La navegación estática se considera validada únicamente si la nueva prueba pasa en CI.
- No se ejecutó una generación real de difusión ni se midió RAM/tiempo/VRAM en el Ryzen 5 5600G durante este bloque.

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

Revisar el diff de integración del PR #19 contra el estado más reciente de `main`, resolver las causas de `mergeable=false` por archivos/funcionalidad (sin merge automático), y ejecutar el recorrido de aceptación del editor en CI: importar PNG → editar/transformar capas → guardar y reabrir JSON → crear variante → exportar PNG transparente. En paralelo, añadir pruebas de regresión para persistencia/errores, no ampliar aún la matriz de modelos IA.
