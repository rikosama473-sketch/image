# Revisor local del dataset

Abre `index.html` en un navegador o sirve esta carpeta con un servidor local sencillo. Todo el procesamiento se ejecuta en el navegador; no hay solicitudes de red en el código y las imágenes no se suben.

1. Selecciona la carpeta raíz de tu clon de `image`.
2. Opcionalmente carga `data/training-labels.csv` para conservar el inventario y cualquier etiqueta anotada.
3. Revisa una página de imágenes por vez (24 imágenes), asigna estados y categorías.
4. Descarga `training-labels.csv` y sustituye el manifiesto del repositorio después de revisar el archivo.

Marca las tres aprobaciones solo después de comprobar visualmente el contenido, las licencias y la autorización de entrenamiento. El nombre `from-PixAI-` no aprueba automáticamente una imagen. Esta herramienta no recorta fondos, no cambia imágenes y no determina legalmente el permiso.


La interfaz no se conecta a GitHub ni escribe sobre archivos originales. El manifiesto descargado debe copiarse manualmente a `data/training-labels.csv` después de comprobarlo. Ningún estado de autorización se marca automáticamente.
