# Piezas gráficas para el generador

Guarda aquí **solo recursos cuyo uso y redistribución estén permitidos para este repositorio**. Cada fuente debe tener entrada en `data/asset-sources.json` o en el manifiesto asociado, con autor, URL, licencia, atribución y permisos separados para modificar, redistribuir y entrenar IA.

Estructura sugerida cuando se confirmen los primeros paquetes:
- `bodies/`
- `heads-faces/`
- `hair/`
- `clothing/`
- `arms-hands/`
- `legs-feet/`
- `poses-rigs/`
- `backgrounds/`

No pongas aquí imágenes de entrenamiento sin revisión ni copies un ZIP completo solo porque sea gratis. Mantén los archivos originales fuera del repositorio si sus términos no permiten publicarlos. Para entrenar una IA, el permiso debe cubrir ese uso por separado.

## Paquetes externos pendientes de selección

Para obtener los ZIP revisados sin meterlos todavía al historial, usa `python scripts/fetch_asset_packs.py --pack all`. La descarga y extracción quedan en `data/asset-cache/` (ignorada por Git). Inspecciona los XCF en GIMP y prueba el ensamble antes de copiar cualquier parte a esta carpeta. La licencia declarada CC0 de los dos recursos facilita reutilización, pero conserva su URL/ficha y no confundas la disponibilidad de archivos con la aprobación de todas las imágenes del dataset actual. Cada pieza copiada debe tener una entrada de fuente y permisos registrados.
