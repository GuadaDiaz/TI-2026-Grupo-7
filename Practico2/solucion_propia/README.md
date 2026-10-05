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

## 5. Solución Externa y Baseline

Para cumplir con la comparativa exigida por la cátedra, el proyecto evalúa el rendimiento del compresor propio contra dos alternativas:

1. **Baseline de la Cátedra:** `gzip -6` (nivel de compresión por defecto, utilizando la herramienta estándar).
2. **Solución Externa (Sorteo B):** **PeaZip**.
   - Formato utilizado: **PEA**.
   - Algoritmo utilizado: **PCOMPRESS2**.
   - Compresión equivalente: **Deflate nivel 6** (en PeaZip esto corresponde a la opción de compresión *Normal* o *Default*).

---

## 6. Automatización del Benchmark

Se provee el script `benchmark.py` que automatiza la medición de métricas (tamaño original, tamaño comprimido, ratio, ahorro de espacio, tiempo de compresión y **Weissman Score**) sobre el corpus de prueba para los tres compresores de manera simultánea.

### Requisitos adicionales para el Benchmark

Para que el script `benchmark.py` funcione correctamente, se asume que las siguientes herramientas de consola están instaladas en el sistema en las rutas predeterminadas, o que se modifiquen las variables correspondientes al principio del script:

- `pea.exe`: Motor de compresión backend de PeaZip (usualmente en `C:\Program Files\PeaZip\pea.exe`).
- `gzip.exe`: Herramienta gzip (ej. la provista por Git Bash en `C:\Program Files\Git\usr\bin\gzip.exe`).

### Instrucciones de Ejecución

Para ejecutar todas las pruebas, ubíquese en el directorio `Practico2/solucion_propia` y ejecute:

```bash
python benchmark.py
```

El script procesará iterativamente los 4 archivos en la carpeta `pruebas/`, generará los archivos comprimidos correspondientes (`.gz`, `.tdi`, `.pea`), medirá los tiempos y luego calculará todas las métricas solicitadas, imprimiendo una tabla en consola.

---

## 7. Ejemplo de Resultados (Benchmark)

Al ejecutar el benchmark sobre el corpus oficial (archivos de 100 KB y uno de 66 bytes), se obtienen resultados similares a los siguientes:

**Prueba 1 (Archivo muy pequeño - 66 bytes)**
*Finalidad: Observar el costo de cabecera.*
- El baseline `gzip` comprime a 82 bytes.
- Nuestro formato `.tdi` aumenta el tamaño a 446 bytes debido al almacenamiento explícito del diccionario de Markov mediante *pickle*.
- `PeaZip` (PEA) sufre el mismo problema de cabecera, generando un archivo de 315 bytes.

**Prueba 2 (Texto natural - 100 KB)**
*Finalidad: Distribución lingüística real.*
- `gzip` y `PeaZip` logran un ratio sobresaliente (aprox. 50:1).
- Nuestro compresor `.tdi` logra un ratio de **2.44:1** (ahorro de casi 60%), demostrando que el modelo de Markov + Huffman captura correctamente las frecuencias condicionales del lenguaje.

**Prueba 3 (Alta repetición - 100 KB)**
*Finalidad: Rachas largas y patrones.*
- `gzip` y `PeaZip` tienen un desempeño extremo gracias a LZ77 (ratios > 100:1).
- Nuestro compresor `.tdi` mejora su ratio a **4.96:1** (ahorro del 80%) al detectar contextos predecibles (símbolos que siempre son seguidos por el mismo símbolo).

**Prueba 4 (Baja repetición / Pseudoaleatorio - 100 KB)**
*Finalidad: Baja redundancia.*
- `gzip` y `PeaZip` logran achicar levemente el archivo (ahorro del ~16%) aprovechando cualquier pequeño patrón residual.
- Por el contrario, nuestro compresor `.tdi` aumenta el tamaño (ahorro negativo). Esto ocurre porque en un archivo de alta entropía casi todos los contextos posibles existen, lo que infla enormemente el diccionario de la cabecera sin aportar un ahorro real en los datos.
