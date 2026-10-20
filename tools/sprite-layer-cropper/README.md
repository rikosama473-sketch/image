# Sprite Layer Cropper

Herramienta local para recortar una spritesheet o grilla mediante coordenadas y guardar cada recorte como PNG RGBA de tamaño uniforme.

## Requisitos

- Python 3.10+
- Pillow
- PyGithub (solo para el publicador opcional)

```bash
python -m pip install -r requirements.txt
```

## Estructura

```text
tools/sprite-layer-cropper/
├── sprite_layer_tool.py
├── publish_with_pygithub.py
├── requirements.txt
├── config/
│   └── grid.example.json
├── input/
│   └── spritesheet.png
└── output/
    ├── body/
    ├── hair/
    ├── eyes/
    ├── clothing/
    ├── accessories/
    ├── expressions/
    └── manifest.json
```

Copia la imagen fuente a `input/spritesheet.png` y copia `config/grid.example.json` a `config/grid.json`. Ajusta filas, columnas, márgenes, separaciones y asignación de cada celda.

Desde este directorio:

```bash
python sprite_layer_tool.py --input input/spritesheet.png --config config/grid.json --output output
```

También se pueden pasar rutas absolutas o rutas personalizadas con las mismas opciones.

## Configuración

- `grid.rows`, `grid.columns`: cantidad de filas y columnas.
- `grid.cell_width`, `grid.cell_height`: dimensiones opcionales de la celda. Si se omiten, se calculan a partir de la imagen, márgenes y separaciones.
- `grid.margin_x`, `grid.margin_y`: margen exterior en píxeles.
- `grid.gap_x`, `grid.gap_y`: separación entre celdas en píxeles.
- `output.width`, `output.height`: dimensiones uniformes finales.
- `output.resample`: `nearest`, `bilinear`, `bicubic` o `lanczos`.
- `cells`: cada elemento asigna una celda completa a una carpeta de capa.
- `regions`: alternativa a `cells`; cada elemento admite `bbox: [x, y, ancho, alto]` local a esa celda.

No uses `cells` y `regions` simultáneamente. Los nombres de capa se convierten en directorios; no se admiten separadores de ruta.

## Ejemplo de región

```json
{
  "row": 1,
  "column": 1,
  "layer": "hair",
  "bbox": [40, 10, 180, 120]
}
```

El rectángulo local comienza a 40 px del borde izquierdo y 10 px del borde superior de esa celda.

## Publicar archivos de texto con PyGithub

El publicador sincroniza archivos UTF-8 de un directorio local con una rama remota, creando archivos nuevos o actualizando los existentes. Usa `--remote-prefix` para conservar el directorio destino. No elimina archivos remotos y omite binarios y secretos comunes.

Define el token fuera del código:

```powershell
$env:GITHUB_TOKEN = "TU_TOKEN"
python publish_with_pygithub.py --repo rikosama473-sketch/image --directory . --remote-prefix tools/sprite-layer-cropper --branch automation/sync-text-assets
```

En Linux/macOS usa `export GITHUB_TOKEN=...`. Otorga al token solo los permisos mínimos necesarios (Contents: read/write). Nunca publiques el token ni lo guardes en Git.

Nota: PyGithub usa la API de GitHub; no realiza un `git clone`. Para clonar el repositorio localmente, utiliza `git clone https://github.com/rikosama473-sketch/image.git`.

## Limitación técnica esencial

Este programa **recorta rectángulos**: no reconoce automáticamente cabello, ojos, cuerpo o ropa dentro de una ilustración completa. Para una grilla donde cada celda ya contiene una pieza separada, asigna una celda por capa. Si una celda contiene un personaje completo, las coordenadas solo extraen una región rectangular y pueden incluir píxeles de otras partes. Para separar elementos superpuestos hace falta una máscara/segmentación y revisión de bordes; cambiar el fondo a transparente no separa objetos.

Cada PNG se ajusta proporcionalmente y se centra en un lienzo transparente del mismo tamaño. El archivo `output/manifest.json` registra dimensiones, coordenadas, salida y errores. Los originales no se modifican.
