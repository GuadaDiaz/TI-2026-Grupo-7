import json
import struct
import os
import random

def generar_datos_simulados():
    nombres = ["Guadalupe Diaz", "Manuel Ortega", "Joaquín Albornoz", "Raul Klenzi"]
    direcciones = ["Av Libertador 123", "Ignacio de la Roza 456", "Mendoza 789", "Córdoba 364"]
    
    return [{
        "nombre": random.choice(nombres),
        "direccion": random.choice(direcciones),
        "dni": random.randint(20000000, 50000000),
        "flags": [random.choice([True, False]) for _ in range(8)]
    } for _ in range(20)]

def almac_texto_binario():
    datos = generar_datos_simulados()
    ruta_json = "datos.json"
    ruta_bin = "datos.bin"

    # Inciso A: Almacenamiento en texto (Longitud variable)
    with open(ruta_json, "w", encoding="utf-8") as f:
        # Convertir booleanos a strings según la consigna
        datos_texto = [
            {**d, "flags": ["True" if b else "False" for b in d["flags"]]} 
            for d in datos
        ]
        json.dump(datos_texto, f, indent=2)

    # Inciso B: Almacenamiento Binario Optimizado (Longitud fija)
    with open(ruta_bin, "wb") as f:
        for d in datos:
            # Bitwise Packing: 8 booleanos -> 1 byte
            byte_flags = 0
            for i, bit in enumerate(d["flags"]):
                if bit:
                    byte_flags |= (1 << i) # Desplaza un 1 a la posición i y aplica OR
            
            # Estructura fija: Nombre (30 bytes), Direccion (50 bytes), DNI (4 bytes uint), Flags (1 byte)
            nombre_bytes = d["nombre"].encode('utf-8').ljust(30, b'\0')[:30]
            dir_bytes = d["direccion"].encode('utf-8').ljust(50, b'\0')[:50]
            
            # Formato '30s 50s I B' de struct equivale a 30 bytes, 50 bytes, un entero sin signo y 1 byte.
            registro_binario = struct.pack('30s 50s I B', nombre_bytes, dir_bytes, d["dni"], byte_flags)
            f.write(registro_binario)

    # Inciso C: Comparación de tamaños
    print(f"Tamaño archivo de texto (JSON): {os.path.getsize(ruta_json)} bytes")
    print(f"Tamaño archivo binario (Struct): {os.path.getsize(ruta_bin)} bytes")

if __name__ == "__main__":
    almac_texto_binario()