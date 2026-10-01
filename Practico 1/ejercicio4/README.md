# Ejercicio 4 — Índice de Coincidencia (IC)

## Descripción General

Calcula el Índice de Coincidencia de bytes para un archivo de texto y uno comprimido, mostrando cómo la compresión aproxima la distribución de bytes a la uniforme.

## Fundamentos Teóricos

El Índice de Coincidencia mide la probabilidad de que dos elementos extraídos aleatoriamente de un conjunto sean idénticos.

Al procesar los archivos como flujos binarios puros (_raw byte streams_), el análisis expone los siguientes comportamientos fundamentales:

- **Para un archivo .txt (codificado en UTF-8 o ASCII)**, el IC de bytes se mantendrá alto (usualmente entre 0.06 y 0.09) por la redundancia estructural: espacios repetidos, vocales dominantes y patrones sintácticos predecibles.

- **Para un archivo .zip**, el valor esperado aleatorio no es 0.038, sino aproximadamente 0.0039. Un algoritmo de compresión eficiente elimina la redundancia de los datos, forzando una distribución casi uniforme que representa máxima entropía.

## Dependencias

Este ejercicio no requiere librerías externas. Utiliza únicamente la librería estándar de Python:
- Python 3.8+
- `collections`, `pathlib`

## Ejecución

Para replicar el análisis empírico, es crítico que el script se ejecute estando ubicado dentro de la carpeta `ejercicio4`.

```bash
cd ejercicio4
python main.py
```

El programa utilizará los archivos `archivos/texto_puro.txt` y `archivos/archivo_comprimido.zip` ya incluidos en la carpeta.
