# Revisión de recorte real — IMAGE Character Creator

**Fecha:** 2026-10-21  
**Estado:** ejecución real aprobada por las comprobaciones técnicas; calidad visual pendiente de aprobación humana.  
**Ejecución de prueba ampliada:** [GitHub Actions #15](https://github.com/rikosama473-sketch/image/actions/runs/39557772418)  
**Artefactos:** [Descargar PNG, máscara alfa, cuatro vistas de borde y métricas](https://github.com/rikosama473-sketch/image/actions/runs/39557772418/artifacts/12325464762)  
**Primera ejecución real:** [GitHub Actions #6](https://github.com/rikosama473-sketch/image/actions/runs/39556952780)  
**Fuente del arte:** `from-PixAI-2034984086876227343-0.png`, hash SHA-256 `f3777be442119b85a9ddab6c59a576f37761248a902e13289c3ff520ebcb67c0`.

## Ejecución

- Motor: `rembg 2.0.85`, modelo local `isnet-anime`.
- Python 3.12.15 / Pillow 12.3.0.
- Entrada y salida: 768×1280; 983.040 píxeles.
- API generativa: 0 llamadas; no se usó una clave de pago.
- Estado de CI: `PASS_REAL_INFERENCE`; el PNG, la máscara alfa y la previsualización se subieron a GitHub Actions.

## Medidas de alfa

Las medidas se calculan en la imagen de salida real. “Semi/partial alpha” significa cualquier valor alfa de 1 a 254, por lo que no debe interpretarse automáticamente como transparencia visible alta en todo ese conjunto.

| Medida | Resultado |
| --- | ---: |
| Píxeles alfa 0 (totalmente transparentes) | 341.075 · 34,69594% |
| Píxeles alfa 1–254 | 641.401 · 65,24668% |
| Píxeles alfa 250–254 (casi opacos) | 601.038 · 61,14075% |
| Píxeles alfa 65–249 (zona de transición) | 19.440 · 1,97754% |
| Píxeles alfa 9–64 | 7.620 · 0,77515% |
| Píxeles alfa 1–8 | 13.303 · 1,35325% |
| Píxeles alfa 255 (totalmente opacos) | 564 · 0,05737% |
| Caja de figura (alfa mayor que 8) | x=12, y=18, x2=753, y2=1280 |

La salida tiene transparencia alfa real y conserva las dimensiones originales; esto confirma funcionamiento técnico, no perfección del contorno.

## Revisión visual

Se inspeccionó el recorte real sobre tablero de transparencia y tres superficies planas (oscuro, magenta y blanco); las cuatro vistas se incluyen en el artefacto de la ejecución #15:

- El fondo claro principal se elimina y la silueta general del personaje queda conservada.
- La pose, el color, los detalles de ojos, ropa y dibujo se conservan: se usó segmentación local, no regeneración.
- Algunos mechones finos muestran un borde claro tenue sobre fondos muy contrastados; hace falta revisar esos contornos antes de aprobarlo para producción.
- No se detectó pérdida generalizada de partes del personaje, pero la métrica automática no sustituye la revisión de cabello, dedos, línea de contorno y huecos entre pelo y brazo.

## Conclusión y siguiente criterio de calidad

El motor `isnet-anime` es una base útil para quitar el fondo de retratos anime completos y el resultado es funcional como **capa candidata**. No se etiqueta como aprobado definitivo.

Para mejorar flequillos y mechones donde el alfa sea geométricamente incorrecto, la referencia upstream de rembg distingue entre decontaminación de color (`-dc`) y refinamiento de cobertura mediante alpha matting o ViTMatte (`-a` / `-vm`). La decontaminación por sí sola ajusta el color de borde, no la cobertura alfa; ViTMatte puede recuperar detalle fino pero consume más tiempo y descarga adicional. Referencia: [rembg — modos de tratamiento de bordes](https://github.com/danielgatis/rembg#choosing-an-edge-mode). No se habilita un refinador pesado automáticamente sin comparar su salida en el arte de prueba.

Este flujo solo quita el fondo del personaje completo; no genera piezas semánticas separadas de cabello, ojos, ropa o accesorios. Esas piezas siguen pendientes de un proceso independiente y de revisión visual.
