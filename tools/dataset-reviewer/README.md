# Revisor local del dataset

Abre `index.html` en un navegador o sirve esta carpeta con un servidor local sencillo. Todo el procesamiento se ejecuta en el navegador; no hay solicitudes de red en el código y las imágenes no se suben.

1. Selecciona la carpeta raíz de tu clon de `image`.
2. Opcionalmente carga `data/training-labels.csv` para conservar el inventario y cualquier etiqueta anotada.
3. Revisa una página de imágenes por vez (24 imágenes), asigna estados y categorías.
4. Descarga `training-labels.csv` y sustituye el manifiesto del repositorio después de revisar el archivo.

Marca las tres aprobaciones solo después de comprobar visualmente el contenido, las licencias y la autorización de entrenamiento. Conserva cada nombre original como pista de procedencia y completa `base_model_identifier`, `lora_identifiers` y `lora_weights_or_settings` cuando se conozcan; la herramienta permite buscar por esos campos. No adivina LoRA desde IDs del nombre. Esta herramienta no recorta fondos, no cambia imágenes y no determina legalmente el permiso.


La interfaz no se conecta a GitHub ni escribe sobre archivos originales. El manifiesto descargado debe copiarse manualmente a `data/training-labels.csv` después de comprobarlo. Ningún estado de autorización se marca automáticamente.


Los datos del modelo base y las LoRA identifican cómo se generó una imagen; son diferentes del permiso para reutilizarla o entrenar con ella. Las imágenes que usen una LoRA de terceros requieren verificar también las condiciones de la imagen de salida, la LoRA/base y los derechos sobre personajes o referencias.


## Diferenciar LoRA de origen y LoRA destino

- `lora_identifiers` y `lora_weights_or_settings` describen la LoRA/configuración con la que se generó la imagen, si se conoce.
- `lora_target_identifiers` es la etiqueta manual para la LoRA que quieres asociar, enviar o probar con esa imagen después.

El nombre original del archivo se conserva porque puede ayudar a identificar el destino. No se infiere automáticamente una LoRA desde el nombre ni se considera ese nombre una prueba de procedencia o de permiso de entrenamiento.
