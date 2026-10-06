# Resultados del Benchmark (Grupo 7)

Generado por `benchmark.py` el 2026-10-06 11:45.

## Protocolo de medición

- **Corpus:** archivos de `tests/` (corpus común de la cátedra); SHA-256 en la tabla de integridad.
- **Corridas:** 3 por archivo y solución; se informa la **mediana** de los tiempos.
- **Tiempos:** en milisegundos, medidos con `time.perf_counter()`. Las tres soluciones se ejecutan como subprocesos, por lo que todos los tiempos incluyen el arranque del proceso.
- **Baseline:** `gzip -n -6` (gzip 1.13), ejecutado como subproceso.
- **Solución externa:** PeaZip 11.3.0, `pea.exe PEA <salida> 0 PCOMPRESS2 SHA3_256 CRC32 RIPEMD160 HIDDEN FROMCL <archivo>` (formato PEA, PCOMPRESS2 = zlib nivel 6, control de volumen SHA3_256, de objeto CRC32 y de stream RIPEMD160, sin cifrado), ejecutado como subproceso; descompresión con `pea.exe UNPEA`.
- **Weissman:** $W = \alpha \cdot (R / R_{ref}) \cdot [\log(T_{ref}) / \log(T)]$, con $\alpha = 1$, tiempos de compresión en ms y referencia gzip-6. Sin pisos ni ajustes de tiempo. La prueba 1 no se usa para el ranking temporal.
- **Weissman global (oficial):** sobre las pruebas 2 a 4. $R_{global} = \sum S_o / \sum S_c$ y $T_{global}$ = mediana del tiempo total de compresión del corpus.
- **Entorno:** Windows-11-10.0.26200-SP0, Python 3.12.9, CPU: Intel64 Family 6 Model 154 Stepping 4, GenuineIntel.

## Tabla resumen (formato de la consigna)

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

## Tabla detallada de métricas

| Archivo | Solución | $S_o$ (B) | $S_c$ (B) | $H$ (B) | $O$ (%) | $R$ | Ahorro (%) | Tamaño relativo (%) | $T_{comp}$ (ms) | $T_{descomp}$ (ms) | $V_c$ (MB/s) | $V_d$ (MB/s) | Weissman | Integridad |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| prueba_1_pequena.txt | **Python TDI** | 64 | 342 | 328 | 95.91 | 0.19 | -434.38 | 534.38 | 75.15 | 63.45 | 0.0009 | 0.0010 | n/a (prueba 1) | OK (SHA-256) |
|  | **GZIP (Ref)** | 64 | 59 | 18 | 30.51 | 1.08 | 7.81 | 92.19 | 20.92 | 24.61 | 0.0031 | 0.0026 | n/a (prueba 1) | OK (SHA-256) |
|  | **PeaZip** | 64 | 276 | - | - | 0.23 | -331.25 | 431.25 | 750.82 | 775.37 | 0.0001 | 0.0001 | n/a (prueba 1) | OK (SHA-256) |
| prueba_2_texto_natural.txt | **Python TDI** | 102400 | 42043 | 1850 | 4.40 | 2.44 | 58.94 | 41.06 | 107.29 | 104.18 | 0.9545 | 0.9829 | 0.0287 | OK (SHA-256) |
|  | **GZIP (Ref)** | 102400 | 1919 | 18 | 0.94 | 53.36 | 98.13 | 1.87 | 18.99 | 20.69 | 5.3936 | 4.9498 | 1.0000 | OK (SHA-256) |
|  | **PeaZip** | 102400 | 2142 | - | - | 47.81 | 97.91 | 2.09 | 737.91 | 729.23 | 0.1388 | 0.1404 | 0.3993 | OK (SHA-256) |
| prueba_3_alta_repeticion.txt | **Python TDI** | 102400 | 20586 | 333 | 1.62 | 4.97 | 79.90 | 20.10 | 84.49 | 74.83 | 1.2120 | 1.3684 | 0.0332 | OK (SHA-256) |
|  | **GZIP (Ref)** | 102400 | 914 | 18 | 1.97 | 112.04 | 99.11 | 0.89 | 27.54 | 23.61 | 3.7182 | 4.3378 | 1.0000 | OK (SHA-256) |
|  | **PeaZip** | 102400 | 1139 | - | - | 89.90 | 98.89 | 1.11 | 720.63 | 726.01 | 0.1421 | 0.1410 | 0.4043 | OK (SHA-256) |
| prueba_4_baja_repeticion.txt | **Python TDI** | 102400 | 120467 | 36795 | 30.54 | 0.85 | -17.64 | 117.64 | 121.57 | 166.91 | 0.8423 | 0.6135 | 0.4722 | OK (SHA-256) |
|  | **GZIP (Ref)** | 102400 | 85207 | 18 | 0.02 | 1.20 | 16.79 | 83.21 | 24.65 | 31.69 | 4.1538 | 3.2316 | 1.0000 | OK (SHA-256) |
|  | **PeaZip** | 102400 | 85459 | - | - | 1.20 | 16.54 | 83.46 | 777.94 | 740.18 | 0.1316 | 0.1383 | 0.4800 | OK (SHA-256) |

## Weissman global (pruebas 2 a 4)

| Solución | $\sum S_o$ (B) | $\sum S_c$ (B) | $R_{global}$ | $T_{global}$ (ms) | $W$ global |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Python TDI | 307200 | 183096 | 1.678 | 315.64 | 0.3722 |
| GZIP (Ref) | 307200 | 88040 | 3.489 | 86.01 | 1.0000 |
| PeaZip | 307200 | 88740 | 3.462 | 2229.04 | 0.5732 |

## Integridad (SHA-256)

| Archivo | SHA-256 original | Reconstruido TDI | Reconstruido gzip | Reconstruido PeaZip |
| :--- | :--- | :---: | :---: | :---: |
| prueba_1_pequena.txt | `8a0d7e04cc6347ca94cf03f7329ad7bf5881bfaff6d26da42e86166822c20051` | idéntico | idéntico | idéntico |
| prueba_2_texto_natural.txt | `410d0deaf3cdfd3a51595d084445727ccc1c2c154b910738e0e32934bbbae403` | idéntico | idéntico | idéntico |
| prueba_3_alta_repeticion.txt | `a54f4a85a8695e1bec7cf49603301d97bd08c89f98dddb09fb0605fa1f88e36e` | idéntico | idéntico | idéntico |
| prueba_4_baja_repeticion.txt | `7b7b0ac6050531d99b338e2db14c188565bbf12f4b08a97b4398b7eda28b6d61` | idéntico | idéntico | idéntico |

> **Notas:** $H$ de gzip son los 18 B fijos del formato (10 B de cabecera + 8 B de trailer). El formato PEA guarda dentro del archivo la ruta absoluta de la entrada (entre 117 y 125 B en esta medición): forma parte de su tamaño comprimido y depende de la carpeta donde esté el repositorio. Por eso no se informa su $H$.
