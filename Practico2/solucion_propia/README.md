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
├── tests/                 # Corpus oficial de la cátedra (sin modificar) y documentación
│   ├── prueba_1_pequena.txt
│   ├── prueba_2_texto_natural.txt
│   ├── prueba_3_alta_repeticion.txt
│   ├── prueba_4_baja_repeticion.txt
│   ├── README_pruebas.txt
│   └── archivos_comprimidos_pea/   # .pea que genera benchmark.py con PeaZip (local, no se versiona)
│
└── results/               # Resultados reproducibles generados por benchmark.py
    └── tabla_comparativa.md
```

Los archivos de `tests/` deben conservar exactamente los bytes publicados por la cátedra (ver SHA-256 en `README_pruebas.txt`). El `.gitattributes` del repositorio evita que Git en Windows convierta sus saltos de línea a CRLF.

---

## 2. Descripción del Algoritmo Propio

El compresor explota la **probabilidad condicional** entre símbolos contiguos, asumiendo una fuente con memoria de **orden 1**:

$$P(S_n \mid S_{n-1}, S_{n-2}, \dots) \approx P(S_n \mid S_{n-1})$$

### Etapas del Algoritmo:

1. **Recolección de Estadísticas (Markov):** En una primera pasada sobre los bytes del archivo original, se contabilizan las frecuencias de transición entre cada byte previo ($S_{n-1}$, el "contexto") y el byte actual ($S_n$).
2. **Generación de Árboles de Huffman Independientes:** Para cada contexto detectado, se construye una cola de prioridad (`heapq`) y un árbol de Huffman estático independiente. De este modo, los símbolos más frecuentes condicionados a ese contexto reciben códigos binarios más cortos.
3. **Codificación:** En la segunda pasada, cada byte se codifica usando el código correspondiente a su contexto anterior. Los bits resultantes se empaquetan en bytes contiguos y se escriben al archivo `.tdi`.
4. **Descompresión:** El descompresor valida la cabecera, reconstruye las tablas inversas de búsqueda (código $\to$ byte para cada contexto), decodifica el flujo de bits bit a bit hasta recuperar la longitud exacta del archivo original y verifica que el SHA-256 coincida con el del original.

### Ejemplo paso a paso (prueba 1)

La prueba 1 tiene 64 bytes: `ABRACADABRA ABRACADABRA⏎TOMATOMATOMA$⏎BANANA_BANANA⏎ERRECONERRE⏎`.

**Paso 1, estadística de Markov.** Se cuentan las 63 transiciones. Aparecen 14 contextos; algunos ejemplos:

| Contexto (byte anterior) | Sucesores observados | Códigos de Huffman del contexto |
|---|---|---|
| `B` | `R`: 4, `A`: 2 | `A` → `0`, `R` → `1` |
| `R` | `A`: 4, `R`: 2, `E`: 2 | `A` → `0`, `E` → `10`, `R` → `11` |
| `A` | `B`: 4, `N`: 4, `C`: 2, `D`: 2, `T`: 2, `⏎`: 2, ` `: 1, `$`: 1, `_`: 1 | `B` → `01`, `N` → `10`, `⏎` → `000`, `C` → `001`, `D` → `1101`, … |
| `T` | `O`: 3 | `O` → `0` (contexto determinista) |

El mismo símbolo recibe códigos distintos según el contexto: `A` cuesta 1 bit después de `B` o de `R`, pero no tiene código después de `A` porque esa transición nunca aparece. Seis contextos son **deterministas** (`D`, ` `, `T`, `M`, `$`, `_`): tienen un único sucesor posible.

**Paso 2, codificación.** El primer byte (`A`) no tiene contexto y va en la cabecera. Después, cada byte se codifica con la tabla de su byte anterior:

```text
A→B   B→R   R→A   A→C   C→A   A→D   D→A  ...
 01    1     0    001    1   1101    0   ...
```

En total se generan 110 bits, que ocupan 14 bytes de payload. La cabecera ocupa 328 B, así que el archivo `.tdi` mide 342 B. En un archivo tan chico, el costo de transmitir el modelo domina el resultado (ver sección 9).

---

## 3. Formato Comprimido Propio (`.tdi`) y Cabecera

El archivo `.tdi` consta de tres partes: **firma**, **cabecera** y **cuerpo de datos (payload)**.

| Parte | Tamaño | Contenido |
|---|---|---|
| Firma (*magic bytes*) | 4 B | `TDMH` (TDI, Markov + Huffman). Permite detectar archivos que no son `.tdi` |
| Versión | 1 B | Versión del formato (actualmente `1`) |
| Cabecera | variable | Diccionario serializado con `pickle` (ver campos abajo) |
| Payload | variable | Códigos de Huffman concatenados, con *padding* de ceros en el último byte |

### Campos de la cabecera

- `primer_byte`: el byte inicial del archivo (no tiene contexto previo); `None` si el archivo está vacío.
- `longitud_original`: número total de bytes del archivo original. Le indica al descompresor dónde terminan los datos, para descartar el *padding* final.
- `sha256`: hash SHA-256 del archivo original (32 B). El descompresor lo usa para validar la integridad.
- `estadisticas`: transiciones de Markov `{byte_anterior: {byte_actual: frecuencia}}`. Permite al descompresor construir exactamente los mismos árboles de Huffman.

El tamaño de la cabecera depende de cuántos pares (contexto, símbolo) aparecen en el archivo: 328 B en la prueba 1, 1 850 B en la prueba 2, 333 B en la prueba 3 y 36 795 B en la prueba 4.

> **Seguridad:** `pickle` solo debe usarse para abrir archivos `.tdi` de confianza. La firma y las validaciones de la cabecera detectan archivos incompatibles o dañados, pero no protegen contra un archivo armado con mala intención.

### Payload

Flujo binario contiguo con los códigos de Huffman concatenados. El último byte incluye _padding_ de ceros a la derecha si la longitud total de bits no es múltiplo de 8.

---

## 4. Instalación y Dependencias

- **Python 3.8+**
- **Dependencias:** Ninguna librería externa. El compresor, el descompresor y el benchmark usan exclusivamente la biblioteca estándar de Python (`sys`, `os`, `io`, `time`, `heapq`, `pickle`, `hashlib`, `collections`, `math`, `statistics`, `gzip`, `shutil`, `subprocess`, `platform`, `datetime`).
- Por este motivo, **no se requiere archivo `requirements.txt` ni `pyproject.toml`**.
- Herramientas externas que usa el benchmark (las busca automáticamente):
  - **gzip** (baseline). En Windows lo provee Git for Windows (`C:\Program Files\Git\usr\bin\gzip.exe`). Si no lo encuentra, usa el módulo `gzip` de Python y lo indica en los resultados.
  - **PeaZip** (solución externa). Se usa `pea.exe`, el motor de línea de comandos que se instala con PeaZip (`C:\Program Files\PeaZip\pea.exe`). Si no lo encuentra, omite las filas de PeaZip.

---

## 5. Instrucciones de Uso

Todos los comandos se ejecutan desde el directorio `Practico2/solucion_propia/`:

### Compresión

```bash
python compressor.py tests/prueba_2_texto_natural.txt salida.tdi
```

```text
=== Compresor TDI: Markov orden 1 + Huffman estático por contexto ===
Archivo de entrada:    tests/prueba_2_texto_natural.txt
Archivo de salida:     salida.tdi
Parámetros:            orden 1 | 51 contextos (18 deterministas) | formato TDMH v1
Tamaño original:       102400 B
Tamaño comprimido:     42043 B (cabecera 1850 B, overhead 4.40 %)
Ratio de compresión:   2.436
Ahorro de espacio:     58.94 %
Tiempo de compresión:  51.90 ms
SHA-256 del original:  410d0deaf3cdfd3a51595d084445727ccc1c2c154b910738e0e32934bbbae403
```

### Descompresión

```bash
python decompressor.py salida.tdi recuperado.txt
```

```text
=== Descompresor TDI: Markov orden 1 + Huffman estático por contexto ===
Archivo de entrada:       salida.tdi
Archivo de salida:        recuperado.txt
Parámetros:               orden 1 | 51 contextos | formato TDMH v1 | cabecera 1850 B
Tamaño comprimido:        42043 B
Tamaño reconstruido:      102400 B
Ratio de compresión:      2.436
Ahorro de espacio:        58.94 %
Tiempo de descompresión:  66.72 ms
Integridad SHA-256:       OK (410d0deaf3cdfd3a51595d084445727ccc1c2c154b910738e0e32934bbbae403)
```

(Los tiempos varían de una ejecución a otra.)

### Verificación de Integridad (SHA-256)

El descompresor verifica automáticamente que `SHA256(original) = SHA256(reconstruido)`, usando el hash guardado en la cabecera. Si no coinciden, informa el error y no genera el archivo de salida. También puede comprobarse manualmente:

En PowerShell:

```powershell
Get-FileHash tests/prueba_2_texto_natural.txt -Algorithm SHA256
Get-FileHash recuperado.txt -Algorithm SHA256
```

En Linux / Git Bash:

```bash
sha256sum tests/prueba_2_texto_natural.txt recuperado.txt
```

### Detección de Errores

Ante un error, los programas muestran un mensaje en `stderr`, terminan con un código distinto de 0 y **no generan** el archivo de salida:

| Situación | Mensaje (resumido) | Código de salida |
|---|---|:---:|
| Cantidad de argumentos incorrecta | `Uso: python ...` | 1 |
| Archivo de entrada inexistente o que es una carpeta | `no existe el archivo ...` / `... no es un archivo` | 2 |
| Archivo de salida igual al de entrada | `el archivo de salida no puede ser el mismo que el de entrada` | 2 |
| Archivo que no es `.tdi` (por ejemplo, un `.txt` o un `.gz`) | `el archivo no tiene formato .tdi (firma inválida)` | 3 |
| Versión de formato desconocida | `versión de formato N no soportada` | 3 |
| Cabecera truncada o mal formada | `cabecera inválida o truncada` | 3 |
| Payload truncado | `datos insuficientes: se recuperaron X de N bytes` | 3 |
| Bits que no corresponden a ningún código | `datos corruptos: ...` | 3 |
| Datos de más al final del archivo | `el archivo tiene N bytes de más ...` | 3 |
| Datos alterados que igual se decodifican | `falla de integridad: el SHA-256 ... no coincide` | 4 |

### Ejecución del Benchmark Automatizado

```bash
python benchmark.py
```

El script ejecuta las mediciones sobre la carpeta `tests/`, imprime un resumen en consola y exporta los resultados a `results/tabla_comparativa.md`.

---

## 6. Solución Externa y Baseline

Para cumplir con la comparativa requerida por la cátedra:

1. **Baseline oficial:** `gzip -n -6` (Deflate nivel 6, sin guardar nombre ni timestamp). El benchmark lo ejecuta como subproceso, igual que el compresor propio, para medir ambos en el mismo entorno. Además descomprime la salida y verifica su SHA-256.
2. **Solución externa (Sorteo B):** **PeaZip 11.3.0**, integrado mediante `pea.exe`, su motor de línea de comandos:

   ```text
   pea.exe PEA <salida> 0 PCOMPRESS2 SHA3_256 CRC32 RIPEMD160 HIDDEN FROMCL <archivo>
   pea.exe UNPEA <archivo.pea> <carpeta> RESETDATE SETATTR EXTRACT2DIR HIDDEN
   ```

   - **Formato PEA, compresión PCOMPRESS2** (nivel *Normal*). El flujo comprimido dentro del `.pea` empieza con `78 9C`, la firma zlib del nivel por defecto (6): equivale a Deflate nivel 6, como pide la consigna.
   - **Controles de integridad:** SHA3_256 por volumen, CRC32 por objeto y RIPEMD160 por stream. **Sin cifrado.** Es la misma configuración que usa la interfaz gráfica de PeaZip para el formato PEA: lo verificamos comparando byte a byte la cabecera de un `.pea` creado desde la interfaz con los generados por línea de comandos.
   - Parámetros: `0` = un solo volumen; `HIDDEN` = sin ventanas, para poder automatizar la medición.
   - El benchmark ejecuta `pea.exe` como subproceso, igual que a las otras dos soluciones. Después descomprime con `UNPEA` y verifica el SHA-256 del archivo extraído.
   - `pea.exe` exige la ruta absoluta del archivo de entrada, y el formato PEA la guarda dentro del archivo comprimido. Esos 117–125 B (según la carpeta donde esté el repositorio) forman parte del tamaño de PeaZip.
   - En `tests/archivos_comprimidos_pea/` queda una copia local del `.pea` de cada prueba, generada en la última corrida del benchmark. Esa carpeta no se sube al repositorio (está en `.gitignore`): los `.pea` contienen la ruta local de quien corrió el benchmark y se pueden regenerar en cualquier momento.

---

## 7. Métricas y Fórmulas Evaluadas

Sea $S_o$ el tamaño original en bytes y $S_c$ el tamaño comprimido en bytes:

- **Ratio de compresión:** $R = \frac{S_o}{S_c}$  
  _(R > 1 indica reducción; R < 1 indica expansión)._
- **Ahorro de espacio (%):** $A = \left(1 - \frac{S_c}{S_o}\right) \times 100$
- **Tamaño relativo (%):** $P = \left(\frac{S_c}{S_o}\right) \times 100$
- **Throughput de compresión:** $V_c = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de compresión (s)}}$ (1 MB = $10^6$ B)
- **Throughput de descompresión:** $V_d = \frac{\text{Tamaño original (MB)}}{\text{Tiempo de descompresión (s)}}$
- **Overhead de cabecera (%):** $O = \left(\frac{H}{S_c}\right) \times 100$, con $H$ = tamaño exacto de la cabecera en bytes (firma incluida). Para gzip, $H$ = 18 B (10 B de cabecera + 8 B de trailer).
- **Weissman Score:**
  $$W = \alpha \times \left(\frac{R}{R_{ref}}\right) \times \left[\frac{\log(T_{ref})}{\log(T)}\right]$$
  donde $\alpha = 1$, los tiempos de compresión $T$ y $T_{ref}$ se expresan obligatoriamente en **milisegundos (ms)** y la referencia es `gzip -n -6`. No se aplica ningún piso ni ajuste a los tiempos.
  - **Weissman global (oficial):** se calcula sobre el corpus de rendimiento (pruebas 2 a 4) con $R_{global} = \sum S_o / \sum S_c$ y $T_{global}$ = mediana del tiempo total de compresión del corpus.
  - El Weissman por archivo se informa solo como referencia, y no se calcula para la prueba 1 porque la consigna la excluye del ranking temporal.
- **Protocolo:** 3 corridas por archivo y solución; se informa la mediana de los tiempos. Las tres soluciones se ejecutan como subprocesos, así que sus tiempos incluyen el arranque del proceso. Por eso los tiempos del compresor propio en el benchmark son mayores que los que informa `compressor.py` (≈20 ms más, por el arranque del intérprete de Python).

---

## 8. Resultados del Benchmark

Resultados de `python benchmark.py` sobre el corpus oficial (Windows 11, Python 3.12.9, gzip 1.13, PeaZip 11.3.0). La tabla completa, con throughput, overhead, tiempos de descompresión y SHA-256 de las tres soluciones, está en [`results/tabla_comparativa.md`](results/tabla_comparativa.md).

| Archivo | Algoritmo | Ratio | Tiempo | Ratio gzip | Tiempo gzip | Weissman |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| prueba_1_pequena.txt | Markov O(1) + Huffman (TDI) | 0.19 | 75.15 ms | 1.08 | 20.92 ms | n/a (prueba 1) |
| prueba_1_pequena.txt | PeaZip (PEA) | 0.23 | 750.82 ms | 1.08 | 20.92 ms | n/a (prueba 1) |
| prueba_2_texto_natural.txt | Markov O(1) + Huffman (TDI) | 2.44 | 107.29 ms | 53.36 | 18.99 ms | 0.0287 |
| prueba_2_texto_natural.txt | PeaZip (PEA) | 47.81 | 737.91 ms | 53.36 | 18.99 ms | 0.3993 |
| prueba_3_alta_repeticion.txt | Markov O(1) + Huffman (TDI) | 4.97 | 84.49 ms | 112.04 | 27.54 ms | 0.0332 |
| prueba_3_alta_repeticion.txt | PeaZip (PEA) | 89.90 | 720.63 ms | 112.04 | 27.54 ms | 0.4043 |
| prueba_4_baja_repeticion.txt | Markov O(1) + Huffman (TDI) | 0.85 | 121.57 ms | 1.20 | 24.65 ms | 0.4722 |
| prueba_4_baja_repeticion.txt | PeaZip (PEA) | 1.20 | 777.94 ms | 1.20 | 24.65 ms | 0.4800 |

### Weissman global (pruebas 2 a 4)

| Solución | $R_{global}$ | $T_{global}$ (ms) | $W$ global |
| :--- | :---: | :---: | :---: |
| Python TDI | 1.678 | 315.64 | **0.3722** |
| GZIP (Ref) | 3.489 | 86.01 | 1.0000 |
| PeaZip | 3.462 | 2229.04 | **0.5732** |

$W < 1$ en las dos soluciones: con esta métrica, gzip-6 ofrece el mejor compromiso entre ratio y tiempo. PeaZip logra casi el mismo ratio que gzip, porque usa el mismo Deflate nivel 6, pero `pea.exe` tarda ≈720 ms incluso con un archivo vacío. Su tiempo lo domina el arranque de la aplicación, no la compresión.

---

## 9. Análisis por Tipo de Archivo

Entropía de orden 0 ($H_0$), entropía condicional del modelo de orden 1 ($H(X \mid X_{-1})$) y longitud media obtenida con Huffman por contexto, en bits por símbolo:

| Archivo | $H_0$ | $H(X \mid X_{-1})$ | Huffman por contexto | Contextos (deterministas) | Pares (contexto, símbolo) |
|---|:---:|:---:|:---:|:---:|:---:|
| prueba_1 | 3.311 | 1.501 | 1.746 | 14 (6) | 32 |
| prueba_2 | 4.230 | 3.079 | 3.140 | 51 (18) | 333 |
| prueba_3 | 2.764 | 1.351 | 1.582 | 11 (2) | 30 |
| prueba_4 | 6.569 | 6.505 | 6.537 | 95 (0) | 9 025 |

- **Prueba 1 (64 B, archivo muy pequeño):** la cabecera domina el resultado: 328 de 342 B (overhead del 96 %). Ningún compresor que transmita un modelo puede ganar en un archivo tan chico. gzip llega a 59 B porque su overhead es fijo (18 B). Este archivo se usa para explicar el algoritmo paso a paso (sección 2), no para el ranking.
- **Prueba 2 (texto natural):** el modelo de orden 1 reduce la incertidumbre de 4.23 a 3.08 bits/símbolo, y el Huffman por contexto (3.14) queda a un 2 % de esa cota. El techo de este método para el archivo es un ratio de ≈2.6, y se obtiene 2.44. gzip y PeaZip llegan a ≈50× porque el texto se repite a gran escala: tiene 1 124 líneas, pero solo 68 distintas. LZ77 (dentro de Deflate) aprovecha esas repeticiones largas, mientras que un modelo que solo mira el byte anterior no puede verlas.
- **Prueba 3 (alta repetición):** la entropía condicional es baja (1.35), pero Huffman no puede usar menos de 1 bit por símbolo. En contextos como `C` (→ `A` 80 %, `O` 20 %) o `N` (→ `A` 78 %, `E` 22 %), la entropía es de ≈0.71–0.77 bits y Huffman gasta 1 bit. Además, los contextos deterministas se codifican con 1 bit (`"0"`) aunque podrían usar 0 bits. Por eso el resultado es 1.58 bits/símbolo, con un ratio de 4.97. gzip supera 100× porque codifica las rachas `AAAA…` y los bloques `ABAB…` como coincidencias largas.
- **Prueba 4 (baja repetición):** son 95 caracteres imprimibles casi equiprobables ($H_0$ = 6.57 ≈ $\log_2 95$). Un símbolo no depende del anterior: la diferencia 6.57 → 6.51 es el sesgo del estimador con ≈1 078 muestras por contexto, no una dependencia real. El modelo no aporta información, pero obliga a transmitir 95 × 95 = 9 025 pares de frecuencias (36 795 B de cabecera, 30.5 % del archivo), y por eso el archivo se expande (ratio 0.85). gzip y PeaZip solo ganan el paso de 8 a ≈6.6 bits por carácter (ratio 1.20).
- **PeaZip frente a gzip:** los dos usan Deflate nivel 6, así que comprimen los datos prácticamente igual. Pero PeaZip ocupa entre 217 y 252 B más en todas las pruebas (por ejemplo, 276 B contra 59 B en la prueba 1). Esa diferencia son los metadatos del formato PEA: la ruta absoluta del archivo (117–125 B) y los controles de integridad (SHA3_256, RIPEMD160 y CRC32). En los tiempos, `pea.exe` tarda ≈720 ms aunque el archivo esté vacío, contra ≈20 ms de gzip, porque es una aplicación con interfaz gráfica que se inicializa en cada ejecución. Por eso su Weissman es bajo pese a tener un ratio casi igual al de gzip.

**Conclusión:** el compresor propio es eficaz cuando la redundancia es local, es decir, cuando depende del símbolo inmediatamente anterior: en las pruebas 2 y 3 llega muy cerca de la cota $H(X \mid X_{-1})$. No puede aprovechar repeticiones de largo alcance, que es lo que explota Deflate. Su punto débil es el costo de transmitir el modelo cuando hay muchos contextos con muchos sucesores.

### Mejoras posibles

- Guardar en la cabecera las **longitudes de código** (Huffman canónico, 1 B por símbolo) en lugar de las frecuencias, con un formato binario propio en lugar de `pickle`. Según nuestras estimaciones, la cabecera de la prueba 4 bajaría de ≈37 KB a ≈12 KB y el ratio pasaría de 0.85 a ≈1.07.
- Usar códigos de **0 bits** en los contextos deterministas: la prueba 3 ahorraría ≈1 KB.
