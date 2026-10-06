# Práctico 2: Compresión y Descompresión con Markov + Huffman

**Materia:** Teoría de la Información  
**Grupo:** Grupo 7
**Algoritmo:** Modelo de Markov de Orden 1 combinado con Codificación de Huffman Estática por Contexto  
**Formato de salida:** `.tdi`

---

## 1. Estructura del Proyecto

El proyecto cumple estrictamente con la estructura solicitada por la cátedra:

```text
Practico2/solucion_propia/
│
├── compressor.py          # Implementación de la compresión propia
├── decompressor.py        # Implementación de la descompresión propia
├── benchmark.py           # Automatiza mediciones, imprime tablas y exporta resultados
├── README.md              # Documentación técnica, manual de uso y análisis de métricas
│
├── tests/                 # Archivos de prueba oficiales (corpus) y documentación
│   ├── prueba_1_pequena.txt
│   ├── prueba_2_texto_natural.txt
│   ├── prueba_3_alta_repeticion.txt
│   ├── prueba_4_baja_repeticion.txt
│   └── README_pruebas.txt
│
└── results/               # Resultados reproducibles generados por benchmark.py
    ├── benchmark_resultados_detallados.csv
    ├── tabla_comparativa.md
```

---

## 2. Descripción del Algoritmo Propio

El compresor explota la **probabilidad condicional** entre símbolos contiguos, asumiendo una fuente con memoria de **orden 1**:

$$P(S_n \mid S_{n-1}, S_{n-2}, \dots) \approx P(S_n \mid S_{n-1})$$

### Etapas del Algoritmo:

1. **Recolección de Estadísticas (Markov):** En una primera pasada sobre los bytes del archivo original, se contabilizan las frecuencias de transición entre cada byte previo ($S_{n-1}$, el "contexto") y el byte actual ($S_n$).
2. **Generación de Árboles de Huffman Independientes:** Para cada contexto detectado, se construye una cola de prioridad (`heapq`) y un árbol de Huffman estático independiente. De este modo, los símbolos más frecuentes condicionados a ese contexto reciben códigos binarios más cortos.
3. **Codificación:** En la segunda pasada, cada byte se codifica usando el código correspondiente a su contexto anterior. Los bits resultantes se empaquetan en bytes contiguos y se escriben al archivo `.tdi`.
4. **Descompresión:** El descompresor lee la cabecera, reconstruye las tablas inversas de búsqueda (código $\to$ byte para cada contexto) y decodifica el flujo de bits bit a bit hasta recuperar la longitud exacta del archivo original.

---

## 3. Formato Comprimido Propio (`.tdi`) y Cabecera

El archivo `.tdi` consta de dos secciones: **Cabecera (Header)** y **Cuerpo de Datos (Payload)**.

### Estructura de la Cabecera

Para garantizar que la descompresión sea 100% autónoma y reproducible sin requerir tablas externas, los metadatos se serializan mediante la librería estándar `pickle`:

- `primer_byte`: El byte inicial del archivo (no posee contexto previo).
- `longitud_original`: Número total de bytes del archivo original (indispensable para descartar el padding final).
- `estadisticas`: Diccionario de transiciones de Markov `{byte_anterior: {byte_actual: frecuencia}}`. Permite al descompresor construir exactamente los mismos árboles de Huffman.

### Payload

Flujo binario contiguo con los códigos de Huffman concatenados. El último byte incluye _padding_ de ceros a la derecha si la longitud total de bits no es múltiplo de 8.

---

## 4. Instalación y Dependencias

- **Python 3.8+**
- **Dependencias:** Ninguna librería externa. El compresor, descompresor y benchmark utilizan exclusivamente la biblioteca estándar de Python (`sys`, `heapq`, `pickle`, `collections`, `os`, `time`, `hashlib`, `math`, `statistics`, `gzip`, `csv`, `json`).
- Por este motivo, **no se requiere archivo `requirements.txt` ni `pyproject.toml`**.

---

## 5. Instrucciones de Uso

Todos los comandos se ejecutan desde el directorio `Practico2/`:

### Compresión

```bash
python compressor.py tests/prueba_2_texto_natural.txt salida.tdi
```

### Descompresión

```bash
python decompressor.py salida.tdi recuperado.txt
```

### Verificación de Integridad (SHA-256)

En PowerShell:

```powershell
Get-FileHash tests/prueba_2_texto_natural.txt -Algorithm SHA256
Get-FileHash recuperado.txt -Algorithm SHA256
```

En Linux / Git Bash:

```bash
sha256sum tests/prueba_2_texto_natural.txt recuperado.txt
```

### Ejecución del Benchmark Automatizado

```bash
python benchmark.py
```

El script ejecutará las mediciones sobre la carpeta `tests/`, imprimirá las tablas en consola y exportará los resultados actualizados a la carpeta `results/`.

---

## 6. Solución Externa y Baseline

Para cumplir con la comparativa requerida por la cátedra:

1. **Baseline Oficial:** `gzip -6` (algoritmo Deflate, nivel de compresión estándar por defecto RFC 1952).
2. **Solución Externa:** **PeaZip** (formato PEA, algoritmo `PCOMPRESS2` equivalente a Deflate nivel 6).

---

## 7. Métricas y Fórmulas Evaluadas

Sea $S_o$ el tamaño original en bytes y $S_c$ el tamaño comprimido en bytes:

- **Ratio de compresión:** $R = \frac{S_o}{S_c}$  
  _(R > 1 indica reducción; R < 1 indica expansión)._
- **Ahorro de espacio (%):** $A = \left(1 - \frac{S_c}{S_o}\right) \times 100$
- **Tamaño relativo (%):** $P = \left(\frac{S_c}{S_o}\right) \times 100$
- **Throughput de compresión:** $V_c = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de compresión (s)}}$
- **Throughput de descompresión:** $V_d = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de descompresión (s)}}$
- **Overhead de cabecera (%):** $O = \left(\frac{H}{S_c}\right) \times 100$ (con $H$ = tamaño exacto de la cabecera en bytes).
- **Weissman Score (individual y global):**
  $$W = \alpha \times \left(\frac{R}{R_{ref}}\right) \times \left[\frac{\log(T_{ref})}{\log(T)}\right]$$
  donde $\alpha = 1$, los tiempos $T$ y $T_{ref}$ se expresan obligatoriamente en **milisegundos (ms)** y la referencia es `gzip -6`.

---

## 8. Resultados del Benchmark

## Tabla Detallada de Métricas

| Archivo                      | Algoritmo      | $Size_o$ (B) | $Size_{comp}$ (B) | $H$ (B) | $Ratio$ | $Ahoroo$ (%) | $Porcentaje$ (%) | $Vel_c$ (MB/s) | $Vel_d$ (MB/s) | Tiempo (ms) | Weissman | Integridad |
| :--------------------------- | :------------- | :----------: | :---------------: | :-----: | :-----: | :----------: | :--------------: | :------------: | :------------: | :---------: | :------: | :--------: |
| prueba_1_pequena.txt         | **Python TDI** |      66      |        434        |   420   |  0.15   |   -557.58%   |     657.58%      |     0.0005     |     0.0006     |   120.55    |  0.0675  |     OK     |
|                              | **GZIP (Ref)** |      66      |        61         |   10    |  1.08   |    7.58%     |      92.42%      |     0.0577     |       -        |    1.14     |  1.0000  |     OK     |
|                              | **PeaZip**     |      66      |        346        |    -    |  0.19   |   -424.24%   |     524.24%      |     0.0026     |       -        |    25.00    |  0.1261  |  OK (GUI)  |
| prueba_2_texto_natural.txt   | **Python TDI** |    103524    |       42502       |  2169   |  2.44   |    58.94%    |      41.06%      |     0.3798     |     0.3985     |   272.55    |  0.0186  |     OK     |
|                              | **GZIP (Ref)** |    103524    |       1927        |   10    |  53.72  |    98.14%    |      1.86%       |    39.7848     |       -        |    2.60     |  1.0000  |     OK     |
|                              | **PeaZip**     |    103524    |       2218        |    -    |  46.67  |    97.86%    |      2.14%       |     3.2351     |       -        |    32.00    |  0.5772  |  OK (GUI)  |
| prueba_3_alta_repeticion.txt | **Python TDI** |    102793    |       20714       |   412   |  4.96   |    79.85%    |      20.15%      |     0.4331     |     0.5294     |   237.32    |  0.0138  |     OK     |
|                              | **GZIP (Ref)** |    102793    |        679        |   10    | 151.39  |    99.34%    |      0.66%       |    53.1257     |       -        |    1.93     |  1.0000  |     OK     |
|                              | **PeaZip**     |    102793    |        972        |    -    | 105.75  |    99.05%    |      0.95%       |     3.6712     |       -        |    28.00    |  0.4827  |  OK (GUI)  |
| prueba_4_baja_repeticion.txt | **Python TDI** |    102400    |      121034       |  37362  |  0.85   |   -18.20%    |     118.20%      |     0.4005     |     0.3821     |   255.67    |  0.2925  |     OK     |
|                              | **GZIP (Ref)** |    102400    |       85234       |   10    |  1.20   |    16.76%    |      83.24%      |    24.1128     |       -        |    4.25     |  1.0000  |     OK     |
|                              | **PeaZip**     |    102400    |       85527       |    -    |  1.20   |    16.48%    |      83.52%      |     3.5310     |       -        |    29.00    |  0.6815  |  OK (GUI)  |

> **Nota:** El archivo GZIP se calcula sin medir descompresión y PeaZip se mide manualmente vía GUI.
