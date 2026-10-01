import os
import math
import struct
from collections import Counter
import matplotlib.pyplot as plt
# c) Frecuencia relativa y distribución de probabilidad p(i)
def calcular_probabilidades(datos):
    total_bytes = len(datos)
    conteo = Counter(datos)
    # Diccionario con el byte (0-255) y su probabilidad relativa
    return {byte: frecuencia / total_bytes for byte, frecuencia in conteo.items()}

# e) Cálculo de la Entropía de Shannon
def calcular_entropia(probabilidades):
    return -sum(p * math.log2(p) for p in probabilidades.values())


def analizar_imagenes(ruta_bmp, ruta_jpg):
    # a) Validación de formato
    if not (ruta_bmp.lower().endswith('.bmp') and ruta_jpg.lower().endswith('.jpg')):
        print("Error: Las extensiones no corresponden a .bmp y .jpg")
        return

    # Lectura binaria de los archivos
    with open(ruta_bmp, 'rb') as f_bmp, open(ruta_jpg, 'rb') as f_jpg:
        datos_bmp = f_bmp.read()
        datos_jpg = f_jpg.read()

    # b) Aislar e imprimir cabecera estándar BMP
    print("--- CABECERA BMP ---")
    firma = datos_bmp[0:2].decode('ascii')
    # Uso de struct.unpack('<I') para enteros sin signo de 4 bytes (Little Endian)
    tamano_archivo = struct.unpack('<I', datos_bmp[2:6])[0]
    ancho = struct.unpack('<I', datos_bmp[18:22])[0]
    alto = struct.unpack('<I', datos_bmp[22:26])[0]
    profundidad_color = struct.unpack('<H', datos_bmp[28:30])[0] # 2 bytes

    print(f"Firma: {firma}")
    print(f"Tamaño: {tamano_archivo} bytes")
    print(f"Ancho: {ancho} px")
    print(f"Alto: {alto} px")
    print(f"Profundidad de color: {profundidad_color} bits por píxel\n")

    prob_bmp = calcular_probabilidades(datos_bmp)
    prob_jpg = calcular_probabilidades(datos_jpg)

    
    entropia_bmp = calcular_entropia(prob_bmp)
    entropia_jpg = calcular_entropia(prob_jpg)

    print("--- ENTROPÍA (H) ---")
    print(f"BMP: {entropia_bmp:.4f} bits/símbolo")
    print(f"JPG: {entropia_jpg:.4f} bits/símbolo")

    # d) Generación de Histogramas Comparativos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.bar(prob_bmp.keys(), prob_bmp.values(), width=1, color='blue')
    ax1.set_title(f'Histograma BMP (H = {entropia_bmp:.2f})')
    ax1.set_xlabel('Valor del Byte (0-255)')
    ax1.set_ylabel('Probabilidad p(i)')

    ax2.bar(prob_jpg.keys(), prob_jpg.values(), width=1, color='green')
    ax2.set_title(f'Histograma JPG (H = {entropia_jpg:.2f})')
    ax2.set_xlabel('Valor del Byte (0-255)')

    plt.tight_layout()
    plt.show()

imagen_bmp=r"./imagenes/blackbuck.bmp"
imagen_jpg=r"./imagenes/blackbuck.jpg"
analizar_imagenes(imagen_bmp,imagen_jpg)