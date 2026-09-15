# Ejercicio 1 — Análisis Entrópico y Estructural de Archivos de Audio (WAV vs. MP3)

## Descripción General

En este ejercicio analiza la cantidad de información transportada por señales de audio, contrastando un formato sin compresión (PCM/WAV) con un formato de compresión perceptiva (MP3).
Se calcula la entropía de Shannon de un audio sin comprimir contra uno comprimido, y se grafica el histograma de bytes de cada uno.

## Fundamentos Teóricos

El proyecto calcula la **Entropía de Shannon** para determinar el límite teórico de compresión y la información promedio por byte (símbolo).

- **Archivos WAV (PCM):** Presentan alta redundancia estadística debido a la correlación temporal de las ondas acústicas naturales, resultando en una baja entropía empírica y un histograma de distribución de probabilidades altamente concentrado.
- **Archivos MP3:** Al aplicar codificación entrópica (como la codificación de Huffman) y algoritmos de compresión psicoacústica con pérdida, se elimina drásticamente la redundancia. El flujo de bytes resultante exhibe una distribución de probabilidades tendiente a la uniformidad, maximizando la entropía hacia su límite teórico de 8 bits por símbolo.

## Arquitectura y Características Técnicas

- **Procesamiento Vectorizado:** Se emplea `numpy` para la lectura directa del binario en arreglos de memoria contigua (C-arrays) y el cálculo de frecuencias relativas, logrando un rendimiento asintótico óptimo $\mathcal{O}(N)$ sin comprometer el _heap_ de la aplicación.
- **Análisis de Cabecera RIFF/WAVE a bajo nivel:** Extracción, desempaquetado y decodificación (_Little-endian_) de metadatos directamente de los bytes crudos mediante la librería estándar `struct`. Se extraen parámetros críticos como:
  - Chunk ID, Formato y Tamaño.
  - Frecuencia de muestreo (_Sample Rate_).
  - Número de canales y Bits por muestra.
  - Alineación de bloque (_Block Align_) y Tasa de bytes (_Byte Rate_).
- **Análisis Estadístico y Visualización:** Cálculo de la entropía empírica mediante `scipy.stats.entropy` y generación de histogramas comparativos con `matplotlib`.

## Dependencias

Para la ejecución de este ejercicio es necesario instalar las siguientes dependencias externas:

- Python 3.8+
- `numpy`, `scipy`, `matplotlib`

Todas están incluidas en el [`requirements.txt`](../requirements.txt) de la raíz
del repositorio. Para instalarlas:

```bash
pip install -r ../requirements.txt
```

## Ejecución

El script debe ejecutarse estando ubicado dentro de la carpeta `ejercicio1`.

```bash
cd ejercicio1
python main.py
```

El programa leerá automáticamente los archivos incluidos en la carpeta `pistas/` (`pista_uno.wav` y `pista_dos.mp3`) y abrirá una ventana con los histogramas (matplotlib).
