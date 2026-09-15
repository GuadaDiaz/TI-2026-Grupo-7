# TI-2026-GRUPO-8 — Teoría de la Información

Trabajos prácticos de la materia Teoría de la Información. Cada carpeta `ejercicioN/`
es independiente y se ejecuta por separado.

## Requisitos generales

- Python 3.8+
- Cada ejercicio se debe ejecutar **con la carpeta del ejercicio como directorio de
  trabajo** (los scripts usan rutas relativas a sus propios datasets), por ejemplo:

  ```bash
  cd ejercicio1
  python main.py
  ```

- La mayoría de los ejercicios solo usa la librería estándar de Python. Los que
  necesitan dependencias externas (Ejercicios 1 y 2) están cubiertas por el
  [`requirements.txt`](requirements.txt) de la raíz del repo, instalable con:

  ```bash
  pip install -r requirements.txt
  ```

  Se detalla debajo, ejercicio por ejercicio, qué necesita cada uno.

---

## Ejercicio 1 — Entropía de archivos de audio (WAV vs. MP3)

Compara la entropía de Shannon de un audio sin comprimir (WAV/PCM) contra uno
comprimido (MP3), y grafica el histograma de bytes de cada uno. Ver también
[ejercicio1/README](ejercicio1/README).

**Dependencias:** `numpy`, `scipy`, `matplotlib` (incluidas en el
[`requirements.txt`](requirements.txt) de la raíz).
```bash
pip install -r requirements.txt
```

**Ejecución:**
```bash
cd ejercicio1
python main.py
```
Usa los archivos ya incluidos en `pistas/pista_uno.wav` y `pistas/pista_dos.mp3`.
Abre una ventana con los histogramas comparativos (matplotlib).

---

## Ejercicio 2 — Entropía de imágenes (BMP vs. JPG)

Compara la entropía de una imagen sin comprimir (BMP) contra su versión comprimida
(JPG), analiza la cabecera BMP y grafica los histogramas de bytes.

**Dependencias:** `matplotlib`, `pillow` (incluidas en el
[`requirements.txt`](requirements.txt) de la raíz).
```bash
pip install -r requirements.txt
```

**Ejecución:**
```bash
cd ejercicio2
python main.py
```
Usa `imagenes/blackbuck.bmp` y `imagenes/blackbuck.jpg`, ya incluidos.

Si querés regenerar el JPG a partir del BMP (opcional, no hace falta si ya están
los archivos en `imagenes/`):
```bash
python convetidor.py
```

---

## Ejercicio 3 — Entropía y redundancia de archivos (TXT vs. ZIP)

Calcula la entropía de Shannon y la redundancia (respecto del máximo de 8
bits/símbolo) de un archivo de texto plano y su equivalente comprimido.

**Dependencias:** ninguna (librería estándar).

**Ejecución:**
```bash
cd ejercicio3
python main.py
```
Usa `archivos/archivo.txt` y `archivos/archivo.zip`, ya incluidos.

---

## Ejercicio 4 — Índice de Coincidencia (IC)

Calcula el Índice de Coincidencia de bytes para un archivo de texto y uno
comprimido, mostrando cómo la compresión aproxima la distribución de bytes a la
uniforme. Ver también [ejercicio4/README](ejercicio4/README).

**Dependencias:** ninguna (librería estándar).

**Ejecución:**
```bash
cd ejercicio4
python main.py
```
Usa `archivos/texto_puro.txt` y `archivos/archivo_comprimido.zip`, ya incluidos.

---

## Ejercicio 5 — Almacenamiento en texto vs. binario

Genera datos simulados (nombre, dirección, DNI, flags) y los guarda tanto en JSON
(texto, longitud variable) como en binario empaquetado con `struct` (longitud
fija), comparando el tamaño resultante de cada formato.

**Dependencias:** ninguna (librería estándar).

**Ejecución:**
```bash
cd ejercicio5
python main.py
```
Sobrescribe `datos.json` y `datos.bin` con una nueva tanda de datos aleatorios en
cada corrida.

---

## Ejercicio 6 — Distancia de Hamming y de Levenshtein

Pide dos cadenas de texto por consola y calcula la Distancia de Hamming (si tienen
igual longitud), la Distancia de Levenshtein y un porcentaje de similitud.

**Dependencias:** ninguna (librería estándar).

**Ejecución (interactivo — pide texto por teclado):**
```bash
cd ejercicio6
python distancia_cadenas.py
```

---

## Ejercicio 7 — Validador de CUIT/CUIL (Módulo 11)

Valida un CUIT/CUIL argentino de 11 dígitos aplicando el algoritmo de dígito
verificador Módulo 11, mostrando el detalle del cálculo.

**Dependencias:** ninguna (librería estándar).

**Ejecución (interactivo — pide el CUIT/CUIL por teclado, con o sin guiones):**
```bash
cd ejercicio7
python validador_cuit.py
```

---

## Ejercicio 8 — Capacidad de un canal binario→cuaternario (búsqueda exhaustiva)

Pide la matriz de transición P(Y|X) de un canal 2×4 y busca, probando
P(X=0) de 0.00 a 1.00 en pasos de 0.01, la distribución de entrada que maximiza
la Información Mutua I(X;Y), es decir la Capacidad del canal.

**Dependencias:** ninguna (librería estándar).

**Ejecución (interactivo — pide las 8 probabilidades P(Y=j|X=i) por teclado):**
```bash
cd ejercicio8
python calculo_canal_exhaustiva.py
```
Cada fila ingresada debe sumar 1 (el script vuelve a pedirla si no es así).

---

## Ejercicio 9 — Canal Binario Simétrico (BSC) con Sockets TCP

Simula un Canal Binario Simétrico mediante un servidor TCP (con una probabilidad
de error `p` oculta) y un cliente que la descubre empíricamente, analiza la
convergencia del BER por Ley de los Grandes Números, y calcula la matriz del
canal, la Información Mutua y la Capacidad. Ver el detalle completo de resultados
en [ejercicio9/informe.md](ejercicio9/informe.md) y la consigna original en
[ejercicio9/consigna.txt](ejercicio9/consigna.txt).

**Dependencias:** ninguna (librería estándar).

**Ejecución (requiere dos terminales, servidor primero):**
```bash
# Terminal 1
cd ejercicio9
python servidor.py

# Terminal 2
cd ejercicio9
python cliente.py
```
El cliente se conecta a `127.0.0.1:5555`, corre la Fase 1 (BER empírico y efecto
del ruido sobre texto) y la Fase 2 (matriz del canal, Información Mutua y
Capacidad) y al terminar envía `SALIR` para cerrar la conexión. El servidor queda
escuchando para nuevas conexiones hasta que se lo interrumpa manualmente
(`Ctrl+C` en su terminal).

---

## Script auxiliar — `generador_archivos.py`

Script de raíz usado para generar el par de datasets de tamaño exactamente igual
(un `.txt` y un `.zip`) que usan los Ejercicios 3 y 4 para comparar entropía e
Índice de Coincidencia. Descarga un texto de Project Gutenberg (requiere
conexión a internet), lo comprime, y trunca el texto plano al mismo tamaño en
bytes que el ZIP resultante. **No hace falta volver a correrlo**: los archivos
que genera ya están incluidos en `ejercicio3/archivos/` y `ejercicio4/archivos/`;
solo es necesario si se quieren regenerar con datos nuevos.

```bash
python generador_archivos.py
```
