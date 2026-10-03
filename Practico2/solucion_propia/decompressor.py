import sys
import pickle
from compressor import recolectar_estadistica_markov, construir_arbol_y_codigos

def descomprimir(archivo_entrada, archivo_salida):
    print(f"Descomprimiendo {archivo_entrada}...")
    
    with open(archivo_entrada, 'rb') as f_in:
        # 1. Leer la cabecera que guardamos
        cabecera = pickle.load(f_in)
        primer_byte = cabecera["primer_byte"]
        longitud_original = cabecera["longitud_original"]
        estadisticas = cabecera["estadisticas"]
        
        if longitud_original == 0:
            open(archivo_salida, 'wb').close()
            print("Archivo original estaba vacío. Listo!")
            return
            
        # 2. Reconstruir los árboles de Huffman
        # Necesitamos armar una tabla de búsqueda a la inversa: en vez de "letra" -> "010", queremos "010" -> "letra"
        # decodificador_markov[letra_anterior]["010"] = letra_actual
        decodificador_markov = {}
        
        for byte_ant, frecuencias_siguientes in estadisticas.items():
            codigos_binarios = construir_arbol_y_codigos(frecuencias_siguientes)
            
            # Invertimos el diccionario para este contexto
            # Si {'A': '0', 'B': '10'}, lo pasamos a {'0': 'A', '10': 'B'}
            dict_invertido = {codigo: simbolo for simbolo, codigo in codigos_binarios.items()}
            decodificador_markov[byte_ant] = dict_invertido
            
        # 3. Preparar la lectura de bits y la escritura
        with open(archivo_salida, 'wb') as f_out:
            # Escribimos el primer byte (que iba gratis en la cabecera)
            f_out.write(bytes([primer_byte]))
            
            # Mantenemos registro de cuánto nos falta decodificar (le restamos el primer byte)
            faltan_decodificar = longitud_original - 1
            contexto_actual = primer_byte
            
            buffer_bits = ""
            
            # Leemos el resto del archivo (los bits puros) byte a byte
            byte = f_in.read(1)
            while byte and faltan_decodificar > 0:
                # Convertimos el byte que acabamos de leer de disco a un string de 8 ceros y unos
                # Ej: el byte 5 lo convierte a "00000101"
                bits = f"{ord(byte):08b}"
                
                # Vamos analizando bit por bit
                for bit in bits:
                    buffer_bits += bit
                    
                    # Chequeamos si la secuencia de bits que venimos juntando forma
                    # una hoja válida en el árbol de nuestro contexto actual
                    if buffer_bits in decodificador_markov[contexto_actual]:
                        # ¡Encontramos la letra!
                        byte_descubierto = decodificador_markov[contexto_actual][buffer_bits]
                        f_out.write(bytes([byte_descubierto]))
                        
                        # Actualizamos el contexto para la próxima letra
                        contexto_actual = byte_descubierto
                        # Vaciamos el buffer
                        buffer_bits = ""
                        
                        faltan_decodificar -= 1
                        # Si ya decodificamos todas las letras, cortamos.
                        # Esto es clave porque el último byte podía tener ceros de "relleno"
                        # que no son parte del mensaje original.
                        if faltan_decodificar == 0:
                            break
                
                # Leemos el siguiente byte del archivo comprimido
                byte = f_in.read(1)
                
    print(f"Listo! Archivo recuperado como {archivo_salida}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python decompressor.py <archivo_entrada.tdi> <archivo_salida_recuperado.txt>")
        sys.exit(1)
        
    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2]
    
    descomprimir(archivo_entrada, archivo_salida)
