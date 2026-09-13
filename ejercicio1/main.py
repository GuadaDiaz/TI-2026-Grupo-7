import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

def analizar_archivos(ruta_wav: str, ruta_mp3: str):
    # a) Validación estricta
    if not (os.path.isfile(ruta_wav) and ruta_wav.lower().endswith('.wav')):
        raise ValueError("Invalid WAV file path or extension.")
    if not (os.path.isfile(ruta_mp3) and ruta_mp3.lower().endswith('.mp3')):
        raise ValueError("Invalid MP3 file path or extension.")

    # b) Análisis de Cabecera WAV (Lectura de bytes crudos)
    with open(ruta_wav, 'rb') as f:
        cabecera = f.read(44) # La cabecera estándar RIFF/WAVE ocupa 44 bytes
        
        # Desempaquetar usando el módulo struct (Little-endian "<")
        chunk_id = struct.unpack('<4s', cabecera[0:4])[0].decode('ascii')
        chunk_size = struct.unpack('<I', cabecera[4:8])[0]
        format_wave = struct.unpack('<4s', cabecera[8:12])[0].decode('ascii')
        sample_rate = struct.unpack('<I', cabecera[24:28])[0]
        num_channels = struct.unpack('<H', cabecera[22:24])[0]
        bit_per_sample = struct.unpack('H', cabecera[34:36])[0]
        
        print(f"--- Análisis de la cabecera WAV ---")
        print(f"Chunk ID: {chunk_id}")
        print(f"Formato de audio: {format_wave}")
        print(f"Tamaño del archivo: {chunk_size + 8} bytes")
        print(f"Número de canales: {num_channels}")
        print(f"Frecuencia de muestreo: {sample_rate} Hz")
        print(f"Alineación de bloque: {num_channels*(bit_per_sample/8)} ")
        print(f"Tasa de bytes: {sample_rate*num_channels*(bit_per_sample/8)} bytes\n")

    # c) Distribución de Probabilidades (Lectura vectorizada con Numpy)
    # np.fromfile lee el archivo completo directamente en un array de C
    bytes_wav = np.fromfile(ruta_wav, dtype=np.uint8)
    bytes_mp3 = np.fromfile(ruta_mp3, dtype=np.uint8)

    # np.bincount cuenta las frecuencias absolutas de valores entre 0 y 255
    freq_wav = np.bincount(bytes_wav, minlength=256)
    freq_mp3 = np.bincount(bytes_mp3, minlength=256)

    # Convertir a frecuencias relativas (p_i)
    p_wav = freq_wav / len(bytes_wav)
    p_mp3 = freq_mp3 / len(bytes_mp3)

    # e) Cálculo de Entropía empírica (Base 2 para medir en bits)
    # Se filtran los p_i = 0 para evitar log(0)
    ent_wav = entropy(p_wav[p_wav > 0], base=2)
    ent_mp3 = entropy(p_mp3[p_mp3 > 0], base=2)
    
    print(f"--- Análisis de la entropía ---")
    print(f"WAV Entropy: {ent_wav:.4f} bits/byte")
    print(f"MP3 Entropy: {ent_mp3:.4f} bits/byte\n")

    # d) Histogramas
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x_axis = np.arange(256)
    
    axes[0].bar(x_axis, p_wav, color='blue', alpha=0.7)
    axes[0].set_title('Distribución de bytes WAV (alta redundancia)')
    axes[0].set_xlabel('Valor del byte (0-255)')
    axes[0].set_ylabel('Probabilidad')

    axes[1].bar(x_axis, p_mp3, color='red', alpha=0.7)
    axes[1].set_title('Distribución de bytes MP3 (entropía maximizada)')
    axes[1].set_xlabel('Valor del byte (0-255)')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Ejecución
    analizar_archivos('pistas/pista_uno.wav', 'pistas/pista_dos.mp3')