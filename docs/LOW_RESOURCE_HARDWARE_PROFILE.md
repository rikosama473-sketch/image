# Perfil local de bajo consumo para IMAGE

## Objetivo

IMAGE debe priorizar la generación local en orden de menor riesgo: recuperar metadatos, probar una base ya disponible, medir una imagen real y recién después decidir si se entrena una LoRA propia. Este perfil está pensado para PCs con 16 GB de RAM de sistema y una APU AMD con gráficos integrados que reserva parte de la memoria para vídeo. Es un punto de partida, no una garantía de compatibilidad ni de rendimiento.

## Perfil inicial recomendado

| Parámetro | Valor inicial | Motivo |
|---|---:|---|
| Imágenes por trabajo | 1 | Evitar picos de memoria de lote |
| Resolución de prueba | 512×512 | Mantener moderado el trabajo por imagen |
| Pasos | 12 | Prueba funcional rápida; subir luego si la calidad lo justifica |
| Dispositivo en Diffusers actual | CPU | Las opciones GPU integradas en ese motor son CUDA/MPS; no selecciona Vulkan de AMD |
| Precisión | Automática | El motor usa FP32 en CPU para el perfil conservador |
| LoRA | Desactivada al primer arranque | Aislar primero los problemas de carga de la base |
| Descarga remota | Desactivada | No descargar pesos sin elección/autorización explícita |

La interfaz ofrece el botón **Aplicar perfil** dentro de “Ajustes de generación”. El perfil no selecciona ni descarga automáticamente un modelo. Debe elegirse una carpeta compatible existente en “Modelo base”.

## Orden de pruebas

1. Ejecutar el inventario de metadatos en local y revisar los identificadores de modelo, hashes y LoRAs que se recuperen. No deducir el modelo solo por el nombre del archivo.
2. Si ya existe un modelo compatible con Diffusers, generar una única imagen a 512×512, 12 pasos, CPU. Registrar el resultado real, el tiempo, RAM máxima aproximada y cualquier error. No contar una carga de modelo ni una prueba de sintaxis como generación exitosa.
3. Si CPU es demasiado lenta, investigar un backend local con soporte para AMD integrado antes de instalar pesos más grandes.

## Candidato secundario: stable-diffusion.cpp

El proyecto oficial [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) declara soporte para modelos SD 1.x, LoRA, SafeTensors/GGUF y backends CPU/Vulkan. Su documentación de [backends](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/backend.md) explica que el backend y la ubicación de los pesos pueden configurarse por separado. Por ello merece una prueba local CPU frente a Vulkan para una APU Radeon.

Esto **no prueba** que el driver, binario o modelo concreto funcione bien en esta PC. Tampoco significa que el motor ya esté integrado en la interfaz de IMAGE. No descargar binarios o pesos automáticamente: seleccionar una release/build adecuada de forma explícita, verificar origen/hash cuando estén publicados y probar un solo modelo compatible. Si la prueba pasa, registrar PNG producido, tamaño, backend, parámetros, tiempo y memoria; solo entonces diseñar un adaptador para el creador web.

El motor Diffusers sigue siendo la ruta de referencia para el flujo LoRA actualmente integrado; la compatibilidad de una LoRA entre formatos/ejecutores debe probarse, no asumirse.

## Entrenamiento LoRA

No comenzar con las 759 entradas de la colección. Antes se requiere:

- procedencia, licencia y permiso de entrenamiento revisados;
- grupo coherente de estilo/base y captions revisadas;
- separación de validación sin duplicados/variantes obvias entre conjuntos;
- preflight completo con el modelo base compatible.

En esta PC, primero optimizar y medir **inferencia**. El entrenamiento LoRA sobre CPU puede ser extraordinariamente lento; no hay una cifra garantizada por el número de núcleos ni por la RAM. Solo lanzar un pequeño piloto después de conocer el tiempo, la memoria libre, el estado de los permisos y la viabilidad del modelo. No modificar los originales.

## Referencias técnicas

- [Diffusers — reducción de uso de memoria](https://github.com/huggingface/diffusers/blob/main/docs/source/en/optimization/memory.md)
- [stable-diffusion.cpp — modelos y backends soportados](https://github.com/leejet/stable-diffusion.cpp)
- [stable-diffusion.cpp — selección de backend y presupuesto de memoria](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/backend.md)

Las cifras reales de tiempo/RAM, la compatibilidad Vulkan y la calidad de las salidas se consideran pendientes hasta probarse en el hardware objetivo.
