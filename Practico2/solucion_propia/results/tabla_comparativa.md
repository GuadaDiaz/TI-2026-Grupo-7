# Resultados del Benchmark (Grupo 8)

## Tabla Detallada de Métricas

| Archivo | Algoritmo | $Size_o$ (B) | $Size_{comp}$ (B) | $H$ (B) | $Ratio$ | $Ahoroo$ (%) | $Porcentaje$ (%) | $Vel_c$ (MB/s) | $Vel_d$ (MB/s) | Tiempo (ms) | Weissman | Integridad |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| prueba_1_pequena.txt | **Python TDI** | 66 | 434 | 420 | 0.15 | -557.58% | 657.58% | 0.0005 | 0.0006 | 120.55 | 0.0675 | OK |
|  | **GZIP (Ref)** | 66 | 61 | 10 | 1.08 | 7.58% | 92.42% | 0.0577 | - | 1.14 | 1.0000 | OK |
|  | **PeaZip** | 66 | 346 | - | 0.19 | -424.24% | 524.24% | 0.0026 | - | 25.00 | 0.1261 | OK (GUI) |
| prueba_2_texto_natural.txt | **Python TDI** | 103524 | 42502 | 2169 | 2.44 | 58.94% | 41.06% | 0.3798 | 0.3985 | 272.55 | 0.0186 | OK |
|  | **GZIP (Ref)** | 103524 | 1927 | 10 | 53.72 | 98.14% | 1.86% | 39.7848 | - | 2.60 | 1.0000 | OK |
|  | **PeaZip** | 103524 | 2218 | - | 46.67 | 97.86% | 2.14% | 3.2351 | - | 32.00 | 0.5772 | OK (GUI) |
| prueba_3_alta_repeticion.txt | **Python TDI** | 102793 | 20714 | 412 | 4.96 | 79.85% | 20.15% | 0.4331 | 0.5294 | 237.32 | 0.0138 | OK |
|  | **GZIP (Ref)** | 102793 | 679 | 10 | 151.39 | 99.34% | 0.66% | 53.1257 | - | 1.93 | 1.0000 | OK |
|  | **PeaZip** | 102793 | 972 | - | 105.75 | 99.05% | 0.95% | 3.6712 | - | 28.00 | 0.4827 | OK (GUI) |
| prueba_4_baja_repeticion.txt | **Python TDI** | 102400 | 121034 | 37362 | 0.85 | -18.20% | 118.20% | 0.4005 | 0.3821 | 255.67 | 0.2925 | OK |
|  | **GZIP (Ref)** | 102400 | 85234 | 10 | 1.20 | 16.76% | 83.24% | 24.1128 | - | 4.25 | 1.0000 | OK |
|  | **PeaZip** | 102400 | 85527 | - | 1.20 | 16.48% | 83.52% | 3.5310 | - | 29.00 | 0.6815 | OK (GUI) |

> **Nota:** El archivo GZIP se calcula sin medir descompresión y PeaZip se mide manualmente vía GUI.
