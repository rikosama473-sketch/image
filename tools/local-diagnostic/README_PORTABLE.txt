IMAGE Local Diagnostic — Windows Portable

QUÉ HACE
- Comprueba información básica de Windows, CPU, RAM disponible y nombres de adaptadores gráficos cuando están expuestos por el registro.
- Inspecciona imágenes de la carpeta que elijas, una por una, leyendo cabeceras y metadatos; calcula SHA-256 por bloques para ayudar a detectar duplicados exactos.
- Extrae identificadores técnicos observables de modelo/LoRA, resolución, tamaño y cobertura de metadatos.
- Si seleccionas la raíz del proyecto IMAGE, cuenta los estados del manifiesto data/training-labels.csv y busca model_index.json bajo models/.
- Crea IMAGE-Diagnostic-Bundle.zip con diagnostic_summary.json e image_inventory.csv.

QUÉ NO HACE
- NO genera imágenes; NO carga pesos; NO entrena; NO instala software; NO descarga modelos.
- NO modifica, mueve, renombra ni borra las imágenes fuente.
- NO recorre todo el disco: solo examina la carpeta que elijas y subcarpetas permitidas.
- NO incluye texto de prompt/negative prompt en los informes ni hace peticiones de red.
- NO sube nada automáticamente. Tú decides si adjuntas el ZIP al chat.

USO
1. Extrae este ZIP a una carpeta normal.
2. Ejecuta IMAGE-Local-Diagnostic.exe (no necesita Python instalado).
3. Elige la carpeta del proyecto IMAGE o la carpeta concreta que contiene tus imágenes. No selecciones C:\ ni todo tu disco.
4. Espera a que termine. No se abre un modelo ni se usa la GPU para IA.
5. Abre la carpeta de informes que se indica en pantalla y, antes de compartir, revisa READ_BEFORE_SHARING.txt.
6. Adjunta IMAGE-Diagnostic-Bundle.zip aquí si decides compartirlo. No hace falta enviar imágenes originales.

SEGURIDAD
- Ejecuta como usuario normal, nunca como administrador.
- No desactives Windows Defender ni otras protecciones para ejecutar el programa.
- El ejecutable es una herramienta de diagnóstico, no el generador IMAGE.
- Si el antivirus lo bloquea, no lo fuerces: usa el script fuente que está en el repositorio o inspecciona el resultado del build de GitHub.
- El ZIP no contiene las imágenes ni los prompts; incluye nombres/rutas relativas de archivo, identificadores de modelo/LoRA y hashes de imágenes. Revísalo antes de compartir.

LÍMITES
- Por defecto escanea como máximo 1.500 imágenes, recorre un máximo de 2.500 carpetas y solo calcula hashes de ficheros de hasta 100 MB. No carga los píxeles completos de las imágenes.
- Los modelos se inspeccionan estructuralmente; no se prueba su generación ni su compatibilidad real.
