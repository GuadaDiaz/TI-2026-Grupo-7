## 1. Algoritmo Propio (Sorteo A)

El algoritmo implementado es **Markov de Orden 1 combinado con Huffman Estático**.

### Funcionamiento

El compresor no asume independencia entre los símbolos, sino que explota la probabilidad condicional.

1. **Estadística (Markov):** Se lee el archivo original construyendo un modelo de transición de estados de orden 1 (frecuencia de cada byte dado el byte inmediatamente anterior).
2. **Árboles de Huffman:** Para cada "byte anterior" (contexto) detectado, se construye un árbol de Huffman estático independiente. Esto asigna códigos binarios más cortos a las transiciones más probables.
3. **Codificación:** Se vuelve a recorrer el archivo, codificando cada símbolo según el árbol de Huffman correspondiente a su contexto actual. Los bits se agrupan en bytes y se persisten en disco.

---

## 2. Formato Comprimido Propio (`.tdi`)

El archivo `.tdi` generado consta de dos partes bien diferenciadas: una **cabecera** (header) y el **cuerpo de datos binarios** (payload).

### Estructura de la Cabecera

Para garantizar la decodificación exacta y autónoma sin depender del archivo original, la cabecera almacena los metadatos necesarios serializados mediante la librería nativa `pickle` de Python.
Contiene un diccionario con:

- `primer_byte`: El símbolo inicial del archivo (ya que no posee contexto previo).
- `longitud_original`: Tamaño exacto del archivo en bytes (necesario para descartar el padding final).
- `estadisticas`: El diccionario de frecuencias de transición de Markov, necesario para reconstruir exactamente la misma topología de árboles de Huffman en el descompresor.

### Payload (Datos)

A continuación de la cabecera serializada, se encuentra el flujo contiguo de bytes producto de la codificación de Huffman. El último byte puede contener _padding_ (ceros de relleno a la derecha) si la longitud total de bits no es múltiplo de 8.

---

## 3. Instalación y Dependencias

El desarrollo fue realizado completamente con la biblioteca estándar de Python, cumpliendo con el requisito de no delegar el núcleo del algoritmo a librerías de compresión externas.

**Requisitos:**

- Python 3.x
- No requiere `requirements.txt` ya que solo utiliza librerías nativas (`sys`, `heapq`, `pickle`, `collections`).

---

## 4. Instrucciones de Uso

Las herramientas proveen una interfaz de línea de comandos (CLI) limpia para su automatización.

### Para Comprimir

```bash
python compressor.py <archivo_original> <archivo_comprimido.tdi>
```

_Ejemplo:_ `python compressor.py pruebas/prueba_2_texto_natural.txt salida.tdi`

### Para Descomprimir

```bash
python decompressor.py <archivo_comprimido.tdi> <archivo_recuperado>
```

_Ejemplo:_ `python decompressor.py salida.tdi recuperado.txt`

---
