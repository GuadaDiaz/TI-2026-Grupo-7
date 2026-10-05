# Práctico 2: Compresión y Descompresión con Markov + Huffman

**Materia:** Teoría de la Información — UNSJ  
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
    ├── benchmark_results.csv
    ├── benchmark_results.json
    └── tabla_comparativa.md
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
Flujo binario contiguo con los códigos de Huffman concatenados. El último byte incluye *padding* de ceros a la derecha si la longitud total de bits no es múltiplo de 8.

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
  *(R > 1 indica reducción; R < 1 indica expansión).*
- **Ahorro de espacio (%):** $A = \left(1 - \frac{S_c}{S_o}\right) \times 100$
- **Tamaño relativo (%):** $P = \left(\frac{S_c}{S_o}\right) \times 100$
- **Throughput de compresión:** $V_c = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de compresión (s)}}$
- **Throughput de descompresión:** $V_d = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de descompresión (s)}}$
- **Overhead de cabecera (%):** $O = \left(\frac{H}{S_c}\right) \times 100$ (con $H$ = tamaño exacto de la cabecera en bytes).
- **Weissman Score (individual y global):**
  $$W = \alpha \times \left(\frac{R}{R_{ref}}\right) \times \left[\frac{\log(T_{ref})}{\log(T)}\right]$$
  donde $\alpha = 1$, los tiempos $T$ y $T_{ref}$ se expresan obligatoriamente en **milisegundos (ms)** y la referencia es `gzip -6`.

---

## 8. Resultados del Benchmark del Grupo

### Tabla Comparativa Principal

| Archivo | Algoritmo | Ratio ($R$) | Tiempo ($T$) | Ratio gzip ($R_{ref}$) | Tiempo gzip ($T_{ref}$) | Weissman ($W$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `prueba_1_pequena.txt` | Markov+Huffman (TDI) | 0.15 | 189.34 ms | 1.09 | 0.14 ms | 0.0001 |
| `prueba_2_texto_natural.txt` | Markov+Huffman (TDI) | 2.42 | 346.66 ms | 53.36 | 1.25 ms | 0.0017 |
| `prueba_3_alta_repeticion.txt` | Markov+Huffman (TDI) | 4.96 | 290.92 ms | 112.04 | 1.55 ms | 0.0034 |
| `prueba_4_baja_repeticion.txt` | Markov+Huffman (TDI) | 0.85 | 411.77 ms | 1.20 | 4.22 ms | 0.1685 |

### Tabla Detallada de Métricas Completas

| Archivo | $S_o$ (B) | $S_c$ (B) | $H$ (B) | $R$ | $A$ (%) | $P$ (%) | $V_c$ (MB/s) | $V_d$ (MB/s) | $O$ (%) | Integridad SHA-256 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `prueba_1_pequena.txt` | 63 | 419 | 405 | 0.15 | -565.08% | 665.08% | 0.0003 | 0.0003 | **96.66%** | **OK (Exacto)** |
| `prueba_2_texto_natural.txt` | 102,400 | 42,346 | 2,153 | **2.42** | **58.65%** | 41.35% | 0.2954 | 0.3150 | **5.08%** | **OK (Exacto)** |
| `prueba_3_alta_repeticion.txt` | 102,400 | 20,649 | 396 | **4.96** | **79.83%** | 20.17% | 0.3520 | 0.4264 | **1.92%** | **OK (Exacto)** |
| `prueba_4_baja_repeticion.txt` | 102,400 | 121,034 | 37,362 | 0.85 | -18.20% | 118.20% | 0.2487 | 0.2157 | **30.87%** | **OK (Exacto)** |

### Weissman Score Global del Corpus
- **$\Sigma S_o$:** $307,263$ bytes  
- **$\Sigma S_{c,\text{TDI}}$:** $184,448$ bytes $\implies R_{global} = 1.6659$  
- **$\Sigma S_{c,\text{gzip}}$:** $88,125$ bytes $\implies R_{global,ref} = 3.4867$  
- **$T_{global,\text{TDI}}$:** $1,238.68$ ms | **$T_{global,ref}$:** $7.16$ ms  
- **$W_{global}$:** **0.1320**  

*Interpretación:* $W < 1.0$ refleja que `gzip-6` supera a la solución evaluada. `gzip` utiliza LZ77 para reemplazar cadenas arbitrarias completas con referencias hacia atrás (alcanzando ratios $>100:1$ en repeticiones) y se ejecuta en código compilado C, mientras que nuestro compresor en Python puro modela exclusivamente la memoria de un solo byte anterior ($S_{n-1}$).

---

## 9. Análisis Detallado por Prueba

1. **`prueba_1_pequena.txt` (63 bytes):**
   Demuestra el impacto del costo de cabecera. Los metadatos de las transiciones ocupan 405 bytes ($O = 96.66\%$), superando el tamaño original.
2. **`prueba_2_texto_natural.txt` (100 KiB):**
   Muestra un comportamiento óptimo en lenguaje natural. La entropía condicional $H(S_n \mid S_{n-1})$ es sensiblemente menor a la entropía marginal de orden cero, alcanzando un ahorro neto del **58.65%** ($R = 2.42$) con un overhead de cabecera de apenas $5.08\%$.
3. **`prueba_3_alta_repeticion.txt` (100 KiB):**
   Las rachas largas hacen que los contextos sean altamente predecibles (entropía condicional cercana a 0). Huffman genera códigos de 1 o 2 bits, alcanzando el mayor ahorro (**79.83%**, ratio $4.96:1$) y el mayor throughput de descompresión (**0.43 MB/s**).
4. **`prueba_4_baja_repeticion.txt` (100 KiB):**
   Al ser pseudoaleatorio uniforme sobre 95 caracteres imprimibles, las transiciones son casi equiprobables (entropía condicional cercana al límite $\log_2 95 = 6.57$ bits). El compresor sufre expansión y la cabecera de 95 contextos ocupa $37.3$ KB ($O = 30.87\%$).
