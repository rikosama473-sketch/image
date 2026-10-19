# Memoria del proyecto IMAGE: datos aprendidos, estilo y dataset

**Actualizado:** 2026-10-19  
**Repositorio:** https://github.com/rikosama473-sketch/image  
**Rama de trabajo:** `work/style-lora-training-2026-10`  
**Estado:** apuntes de diagnóstico; no implica que el modelo local o el entrenamiento ya estén funcionando.

Este archivo conserva los hallazgos para las siguientes sesiones y separa datos observados, datos comunicados por el usuario y aspectos aún pendientes de comprobar.

## 1. Objetivo del proyecto

Crear un generador local de imágenes que pueda aproximarse al estilo visual de las imágenes de referencia del usuario, con recursos modestos y sin depender de generar imágenes en la nube. La vía candidata es utilizar un modelo base compatible y, si los resultados y los derechos de uso lo permiten, entrenar una LoRA propia con un conjunto de imágenes cuidadosamente seleccionado.

Prioridades:
- Proteger la estabilidad del PC; evitar cargas inesperadas de RAM/VRAM, descargas automáticas grandes y entrenamiento prematuro.
- Conservar intactas las imágenes originales.
- No confundir semejanza visual con reproducción exacta del modelo remoto.
- Registrar por separado los hechos comprobados, las pistas y las hipótesis.
- No cambiar `main` ni integrar cambios sin revisión/aceptación funcional.

## 2. Hardware comunicado y recursos observados

### Hardware comunicado por el usuario
- CPU: AMD Ryzen 5 5600G.
- RAM instalada: 16 GB.
- Gráficos: Radeon Graphics integrada; el usuario indicó que reserva/asigna aproximadamente 2 GB a gráficos.

### Lectura del diagnóstico local (una única medición, 2026-10-19)
- CPU detectada: `AMD Ryzen 5 5600G with Radeon Graphics`.
- Adaptador detectado por la consulta del sistema: `AMD Radeon(TM) Graphics`.
- Versión de driver informada: `31.0.21923.11000`.
- 12 procesadores lógicos.
- Windows informó: `Windows-10-10.0.22631-SP0` (la cadena exacta devuelta por la herramienta).
- RAM total detectada: 16,427,618,304 bytes (aprox. 16.43 GB decimales / 15.3 GiB).
- RAM disponible antes del escaneo: 699,158,528 bytes (aprox. 667 MiB), con 95% de uso.
- RAM disponible después del escaneo: 901,058,560 bytes (aprox. 859 MiB), con 94% de uso.

**Interpretación prudente:** la memoria estaba muy ocupada en el momento de esa medición. Es una fotografía puntual, no una prueba de que siempre esté así. Antes de instalar modelos, inferir o entrenar, volver a comprobar el uso de RAM y cerrar procesos innecesarios. No iniciar entrenamiento si queda tan poca memoria disponible.

La ruta actual de Diffusers contempla CUDA/MPS/CPU; CUDA no es el camino de aceleración de esta Radeon integrada. CPU es el fallback conservador. Se había señalado `stable-diffusion.cpp` con Vulkan como alternativa que merece pruebas, pero **no está validada en este PC ni debe considerarse integrada/funcional todavía**.

## 3. Procedencia y combinación visual indicada por el usuario

El usuario aclaró que las imágenes fueron creadas con generadores web y que la combinación que desea investigar es:
- **Modelo base indicado:** Haruka v2.
- **LoRA indicada:** Gen Pibara (en una respuesta anterior se encontró una página con el nombre Gen Pibara V1; comprobar que sea exactamente la misma versión antes de usarla).

En el historial se compartieron estas páginas para comprobar:
- Haruka v2 en PixAI: https://pixai.art/model/1861558737426484240
- Gen Pibara V1 en PixAI: https://pixai.art/model/2035047104781084932

Estas URL son referencias de investigación, no prueba de que los pesos estén disponibles localmente, sean compatibles entre sí ni puedan redistribuirse. Verificar de nuevo nombre, versión, arquitectura, formato descargable, licencia y condiciones de uso antes de descargar o entrenar.

Una respuesta anterior describió Haruka v2 como SDXL y la ficha de Gen Pibara V1 como DiT.2 XL, y citó palabras de activación `1girl`, `solo`, `white pupils` y `shiny skin`. Tratar estos datos como **pendientes de verificación en la ficha y en los archivos descargados**. No asumir que la LoRA se puede cargar directamente sobre Haruka v2: la compatibilidad exacta aún está sin demostrar.

El nombre `from-PixAI-` en archivos es una pista sobre el origen de las descargas, no una demostración de qué checkpoint se usó en cada imagen.

## 4. Diagnóstico del paquete aportado por el usuario

Paquete inspeccionado: `IMAGE-Diagnostic-Bundle.zip`. Incluía solamente:
- `diagnostic_summary.json`
- `image_inventory.csv`
- `READ_BEFORE_SHARING.txt`

No incluía imágenes originales ni texto de prompts; por tanto, se pudo analizar el inventario técnico, pero no inspeccionar visualmente el estilo.

### Resultado del escaneo
- Carpeta seleccionada en el diagnóstico: `promp mascota`. Es una etiqueta de la carpeta elegida, no necesariamente la raíz del repositorio ni la carpeta global de modelos.
- Directorios recorridos: 21.
- Imágenes escaneadas: 969.
- Errores de lectura de imágenes: 0; las 969 quedaron con estado de lectura `ok`.
- Tamaño contabilizado: 883,474,531 bytes (aprox. 883.5 MB / 0.883 GB).
- Límites de escaneo alcanzados: ninguno.
- Extensiones: 953 PNG, 15 JPG y 1 WebP.
- Nombres: 909 archivos empiezan por `from-PixAI-`; 42 nombres de archivo son PNG numéricos y 18 entran en otros patrones.
- 954 archivos tienen modo RGBA y 15 RGB. Que haya canal alfa no demuestra que exista transparencia visible.
- Indicios de metadatos de generación detectados: 0.
- Campos detectados con prompt, prompt negativo, identificador/hash de modelo base o identificador de LoRA: 0.

### Carpetas principales
- `familia pibara`: 668 imágenes.
- `sunna`: 130.
- `chie`: 113.
- `kuro`: 39.
- Raíz: 19.

Estas cantidades describen la ubicación de los archivos, no garantizan que todas las imágenes tengan el mismo estilo o que pertenezcan a la misma LoRA.

### Resoluciones más frecuentes
- 768×1280: 431.
- 720×1280: 183.
- 544×960: 183.
- 520×1080: 63.
- 520×936: 50.
- 520×1032: 23.
- 512×720: 10.
- 832×1248: 8.
- 1280×720: 2.
- 640×640: 2.
- 624×768: 2.

La mayoría son composiciones verticales. Antes de preparar datos de entrenamiento habrá que decidir si recortar, redimensionar o utilizar bucketing de aspectos según el entrenador elegido, evitando deformar las imágenes.

### Duplicados exactos detectados
Se encontraron 2 grupos (2 archivos adicionales duplicados). No borrar automáticamente:
1. `familia pibara/cami v1/from-PixAI-2036844810321321810-1 (1).png` y `familia pibara/cami v1/from-PixAI-2036844810321321810-1.png`.
2. `sunna/sunna v1/from-PixAI-2051739918923127209-0.png` y `sunna/sunna v1/from-PixAI-2052089408399777103-1.png`.

La identidad exacta se determinó con hashes SHA-256. Mantener los originales; si se prepara un dataset, dejar constancia de los duplicados y excluir copias redundantes sólo en el conjunto de entrenamiento derivado.

## 5. Lo que NO se pudo concluir

- El paquete no contiene las imágenes; por sí solo no permite evaluar el estilo visual.
- No se encontró `data/training-labels.csv` dentro de la raíz seleccionada; el manifiesto de entrenamiento resultó `null`.
- No se encontró una carpeta `models/` bajo la raíz seleccionada y por eso no se detectaron modelos ni LoRA **en esa ubicación**. Esto no demuestra que no existan modelos instalados en otras carpetas del PC.
- Las imágenes no mostraron metadatos que identificaran el prompt, checkpoint o LoRA original.
- No se ha comprobado la disponibilidad local de Haruka v2 ni de Gen Pibara.
- No se ha ejecutado inferencia real ni se ha entrenado una LoRA con estas imágenes.
- Que todas las imágenes sean legibles no significa que todas sean buenas muestras de entrenamiento.
- No se ha validado compatibilidad, rendimiento, velocidad ni calidad de ningún motor local en este equipo.

## 6. Herramienta de diagnóstico portable

La versión aportada por el repositorio es una herramienta de diagnóstico, **no el generador de imágenes**. Según su diseño, inspecciona encabezados/metadatos y hashes dentro de la carpeta que el usuario elige, no carga pesos ni ejecuta entrenamiento o inferencia, no hace solicitudes de red y no modifica originales. El ZIP resultante contiene el resumen y el inventario CSV, no las imágenes.

Comprobación registrada en el historial de trabajo:
- CI #128 para el HEAD `0821a0dd794b8c3af0d8d4de5addf718cda79158`: aprobado.
- Build portable de Windows, workflow run #6: aprobado.
- Enlace del build: https://github.com/rikosama473-sketch/image/actions/runs/39220572453
- Enlace de CI: https://github.com/rikosama473-sketch/image/actions/runs/39220581493
- Artefacto de diagnóstico: https://api.github.com/repos/rikosama473-sketch/image/actions/artifacts/12171391920/zip
- El artefacto se indicó con expiración el 2026-11-18. Comprobar disponibilidad antes de reutilizar el enlace.

Estos CI prueban que las comprobaciones automatizadas y la compilación del diagnóstico pasaron; no prueban que el generador produzca imágenes en este PC.

## 7. Siguiente secuencia segura de trabajo

1. **Revisar visualmente las muestras sin mover ni alterar los originales.** Crear hojas de contacto offline con miniaturas, organizadas por carpeta/estilo. No subir las 969 imágenes sin necesidad; se puede empezar por una selección curada o hojas de contacto locales.
2. **Separar por objetivo visual.** Identificar qué carpetas/personajes comparten el aspecto buscado y cuáles mezclan estilos. Las carpetas son una pista de clasificación, no etiquetas fiables por sí solas.
3. **Verificar archivos de modelo.** Confirmar si Haruka v2 y Gen Pibara se pueden descargar legalmente, qué formato ofrecen, cuál es su arquitectura y si la LoRA es compatible con el checkpoint.
4. **Preparar una prueba diminuta local.** Recién después de comprobar RAM libre y compatibilidad, probar una sola imagen de 512×512 o una configuración de bajo consumo, un proceso a la vez y sin descargas o instalaciones automáticas.
5. **Elegir el motor compatible con hardware.** Comparar un backend de bajo consumo en CPU con alternativas Vulkan para Radeon sólo mediante una prueba controlada; medir RAM, tiempo y estabilidad.
6. **Preparar un dataset derivado sin tocar el original.** Generar captions/manifiesto revisables, excluir duplicados exactos, separar validación y entrenamiento y mantener trazabilidad de cada archivo.
7. **Entrenar solamente tras la evaluación visual y técnica.** La LoRA propia podría aprender un estilo aproximado; no garantiza reproducir de forma idéntica Haruka v2 o Gen Pibara, ni recuperar los pesos privados del generador web.

## 8. Principio de continuidad

No volver a pedir al usuario el hardware, el inventario ni el origen web de estas imágenes: ya constan aquí. No afirmar que se encontró el modelo a partir del nombre de archivo, ni que el entrenamiento está hecho, ni que una ruta de aceleración funciona sin una prueba real. Cuando se añadan hallazgos, indicar fecha, evidencia y nivel de certeza.