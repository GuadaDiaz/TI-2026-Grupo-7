import os
from collections import Counter

def calcular_ic(ruta_archivo):
    """
    Calcula el Índice de Coincidencia (IC) analizando la frecuencia de bytes (0-255).
    """
    try:
        with open(ruta_archivo, 'rb') as f:
            datos = f.read()
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {ruta_archivo}")
        return None

    N = len(datos)
    
    # Prevenir división por cero si el archivo está vacío o tiene 1 byte
    if N <= 1:
        return 0.0

    # Contar la frecuencia absoluta (f_i) de cada byte
    frecuencias = Counter(datos)
    
    # Calcular sumatoria de f_i * (f_i - 1)
    suma_frecuencias = sum(f_i * (f_i - 1) for f_i in frecuencias.values())
    
    # Retornar el IC
    ic = suma_frecuencias / (N * (N - 1))
    return ic

if __name__ == "__main__":
    # Asegúrate de colocar archivos reales en el mismo directorio antes de la ejecución
    ic_txt = calcular_ic(r".\archivos\texto_puro.txt")
    ic_zip = calcular_ic(r".\archivos\archivo_comprimido.zip")
    
    if ic_txt is not None:
        print(f"IC del TXT (bytes): {ic_txt:.5f}")
    if ic_zip is not None:
        print(f"IC del RAR (bytes): {ic_zip:.5f}")