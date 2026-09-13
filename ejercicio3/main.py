import math
import os
from collections import Counter

def analizar_entropia_archivo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
        return

    tamano_total = os.path.getsize(ruta_archivo)
    if tamano_total == 0:
        print(f"El archivo '{ruta_archivo}' está vacío.")
        return

    with open(ruta_archivo, 'rb') as f:
        datos = f.read()

    # Contar la frecuencia de aparición de cada byte (0-255). 
    frecuencias = Counter(datos)

    entropia = 0.0
    for byte, apariciones in frecuencias.items():
        p_i = apariciones / tamano_total
        entropia -= p_i * math.log2(p_i)

    entropia_maxima = 8.0
    redundancia = entropia_maxima - entropia

    print(f"--- Análisis de: {os.path.basename(ruta_archivo)} ---")
    print(f"Tamaño: {tamano_total} bytes")
    print(f"Entropía (H): {entropia:.4f} bits/símbolo")
    print(f"Redundancia (R): {redundancia:.4f} bits/símbolo")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    analizar_entropia_archivo(r".\archivos\archivo.txt")
    analizar_entropia_archivo(r".\archivos\archivo.zip")
    pass