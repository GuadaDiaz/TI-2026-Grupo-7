# Resultados del Benchmark (Grupo 7)

## Tabla Comparativa Principal

| Archivo | Algoritmo | Ratio ($R$) | Tiempo ($T$) | Ratio gzip ($R_{ref}$) | Tiempo gzip ($T_{ref}$) | Weissman ($W$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| prueba_1_pequena.txt | Markov+Huffman (TDI) | 0.15 | 168.22 ms | 1.09 | 0.13 ms | 0.0001 |
| prueba_2_texto_natural.txt | Markov+Huffman (TDI) | 2.42 | 345.01 ms | 53.36 | 1.02 ms | 0.0001 |
| prueba_3_alta_repeticion.txt | Markov+Huffman (TDI) | 4.96 | 303.41 ms | 112.04 | 1.66 ms | 0.0039 |
| prueba_4_baja_repeticion.txt | Markov+Huffman (TDI) | 0.85 | 443.09 ms | 1.20 | 4.64 ms | 0.1775 |

## Tabla Detallada de Métricas

| Archivo | $S_o$ (B) | $S_c$ (B) | $H$ (B) | $R$ | $A$ (%) | $P$ (%) | $V_c$ (MB/s) | $V_d$ (MB/s) | $O$ (%) | Integridad |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| prueba_1_pequena.txt | 63 | 419 | 405 | 0.15 | -565.08% | 665.08% | 0.0004 | 0.0004 | 96.66% | OK |
| prueba_2_texto_natural.txt | 102400 | 42346 | 2153 | 2.42 | 58.65% | 41.35% | 0.2968 | 0.3092 | 5.08% | OK |
| prueba_3_alta_repeticion.txt | 102400 | 20649 | 396 | 4.96 | 79.83% | 20.17% | 0.3375 | 0.3112 | 1.92% | OK |
| prueba_4_baja_repeticion.txt | 102400 | 121034 | 37362 | 0.85 | -18.20% | 118.20% | 0.2311 | 0.1940 | 30.87% | OK |

## Weissman Score Global del Corpus

- **R_global (TDI):** 1.6659
- **R_global (gzip):** 3.4867
- **T_global (TDI):** 1259.73 ms
- **T_global (gzip):** 7.45 ms
- **Weissman Score Global:** **0.1344**
