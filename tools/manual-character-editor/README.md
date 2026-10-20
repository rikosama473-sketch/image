# IMAGE — Editor manual de recortes y capas

Este editor es una herramienta de edición manual, no un generador de máscaras por IA. Está pensado para preparar sprites y piezas intercambiables de personajes anime: cabello delantero/trasero, cabeza, cara, cuerpo, ropa y accesorios.

## Abrir en Windows

1. Descargá el repositorio IMAGE o actualizá tu copia local.
2. Entrá en la carpeta tools/manual-character-editor.
3. Hacé doble clic en start-editor.bat. También podés ejecutar python run_editor.py.
4. Se abre el editor en Chrome u otro navegador. No requiere instalar paquetes Python; el servidor solo escucha en 127.0.0.1.
5. Pulsá Abrir imagen y seleccioná el PNG original. El botón Ejemplo Pibara es opcional y necesita conexión a Internet.

No se suben las imágenes que abrís desde el equipo. El único acceso remoto opcional es el botón de referencia Ejemplo Pibara.

## Separar cabello, cara, cuerpo y accesorios

- Polígono/lazo: hacé clic alrededor de la silueta y doble clic para cerrarlo.
- Pincel de selección: pintá la zona; cambiá el tamaño del pincel para bordes o zonas amplias.
- Restar de la selección: activá la casilla para corregir zonas que pintaste de más.
- Varita mágica: selecciona una región conectada de color parecido al punto elegido. Bajá tolerancia para no comerte el contorno.
- Extraer selección: crea una capa transparente nueva y, por defecto, quita esa zona de la capa anterior. Así podés separar varias piezas.
- Borrar/restaurar: retocá píxeles manualmente. Restaurar vuelve a pintar desde la copia original de esa capa.
- Quitar fondo: intenta eliminar el color conectado al borde superior/izquierdo. Si elimina parte del personaje, usá Deshacer y probá con tolerancia menor.
- Exportar selección / Exportar capa: crea PNG con transparencia. El recorte ceñido está activado inicialmente; desactivalo para conservar el mismo lienzo y alineación.
- Recortar lienzo: recorta todas las capas al mismo rectángulo.
- Guardar proyecto: guarda un JSON local con capas, máscaras y selección para continuar después. Guardá también los PNG finales.

## Cómo lograr un cabello intercambiable

1. Abrí la imagen y hacé zoom hasta que se distingan los mechones.
2. Marcá solo el cabello trasero; extraelo a una capa y revisá la imagen con y sin la capa.
3. Repetí para el flequillo y accesorios que deban moverse con él.
4. Conservá una capa de cabeza/cara y otra de cuerpo.
5. Borrá del cuerpo los píxeles antiguos que sobresalgan del cabello nuevo y restaurá bordes si te llevaste piel o ropa.
6. Exportá cada capa con el mismo tamaño de lienzo si necesitás superponerlas sin cambiar su posición.

El editor conserva la imagen original en una copia de referencia por capa, pero no puede recuperar píxeles que no existían o que estaban tapados. Para un cambio totalmente limpio quizá haya que dibujar/reconstruir a mano el cuello, la nuca o zonas de ropa ocultas.

## Límites de esta versión

Incluye recorte rectangular, selección poligonal, pincel de máscara, varita por color conectado, borrador/restauración, borrado de fondo conectado a bordes, extracción no destructiva a capas, control de visibilidad/opacidad, exportación PNG y guardado de proyecto JSON. No incluye selección semántica automática, relleno generativo ni un editor de nodos.
