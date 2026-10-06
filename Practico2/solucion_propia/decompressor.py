import io
import os
import sys
import time
import pickle
import hashlib
from compressor import construir_arbol_y_codigos, MAGIC, VERSION, ORDEN_MARKOV

class ErrorFormatoTDI(Exception):
    """El archivo no es un .tdi válido, la cabecera está dañada o faltan datos."""

class ErrorIntegridadTDI(Exception):
    """Los datos se decodificaron, pero el SHA-256 no coincide con el del original."""

def leer_cabecera(contenido):
    """
    Verifica la firma y la versión, lee la cabecera y controla que tenga la estructura esperada.
    Devuelve (cabecera, posicion_donde_empieza_el_payload).
    Lanza ErrorFormatoTDI si el archivo no cumple el formato.
    """
    # 1. Firma (magic bytes) + versión
    tam_firma = len(MAGIC) + 1
    if len(contenido) < tam_firma or contenido[:len(MAGIC)] != MAGIC:
        raise ErrorFormatoTDI("el archivo no tiene formato .tdi (firma inválida)")
    version = contenido[len(MAGIC)]
    if version != VERSION:
        raise ErrorFormatoTDI(f"versión de formato {version} no soportada (se esperaba {VERSION})")

    # 2. Cabecera serializada
    # Nota: pickle solo debe usarse con archivos de confianza; la firma evita abrir por error
    # archivos de otro tipo, pero no protege contra un archivo armado con mala intención.
    flujo = io.BytesIO(contenido)
    flujo.seek(tam_firma)
    try:
        cabecera = pickle.load(flujo)
    except Exception:
        raise ErrorFormatoTDI("cabecera inválida o truncada") from None

    # 3. Estructura y tipos de cada campo
    campos = {"primer_byte", "longitud_original", "sha256", "estadisticas"}
    if not isinstance(cabecera, dict) or set(cabecera) != campos:
        raise ErrorFormatoTDI("cabecera inválida: faltan campos o hay campos desconocidos")
    longitud = cabecera["longitud_original"]
    primer_byte = cabecera["primer_byte"]
    estadisticas = cabecera["estadisticas"]
    if not isinstance(longitud, int) or longitud < 0:
        raise ErrorFormatoTDI("cabecera inválida: longitud original incorrecta")
    if longitud > 0 and not (isinstance(primer_byte, int) and 0 <= primer_byte <= 255):
        raise ErrorFormatoTDI("cabecera inválida: primer byte incorrecto")
    if not (isinstance(cabecera["sha256"], bytes) and len(cabecera["sha256"]) == 32):
        raise ErrorFormatoTDI("cabecera inválida: hash SHA-256 incorrecto")
    if not isinstance(estadisticas, dict) or (longitud > 1 and not estadisticas):
        raise ErrorFormatoTDI("cabecera inválida: falta el modelo de Markov")
    for contexto, frecuencias in estadisticas.items():
        if not (isinstance(contexto, int) and 0 <= contexto <= 255 and isinstance(frecuencias, dict) and frecuencias):
            raise ErrorFormatoTDI("cabecera inválida: modelo de Markov mal formado")
        for simbolo, cantidad in frecuencias.items():
            if not (isinstance(simbolo, int) and 0 <= simbolo <= 255 and isinstance(cantidad, int) and cantidad > 0):
                raise ErrorFormatoTDI("cabecera inválida: modelo de Markov mal formado")

    return cabecera, flujo.tell()

def decodificar(cabecera, payload):
    """
    Reconstruye los bytes originales a partir de la cabecera y del flujo de bits (payload).
    Lanza ErrorFormatoTDI si los datos no alcanzan, sobran o no corresponden a ningún código.
    """
    longitud_original = cabecera["longitud_original"]
    salida = bytearray()
    if longitud_original == 0:
        if payload:
            raise ErrorFormatoTDI("el archivo original estaba vacío pero hay datos de más")
        return salida

    # 1. Reconstruir los árboles de Huffman
    # Necesitamos armar una tabla de búsqueda a la inversa: en vez de "letra" -> "010", queremos "010" -> "letra"
    # decodificador_markov[letra_anterior]["010"] = letra_actual
    decodificador_markov = {}
    longitud_maxima = {}
    for byte_ant, frecuencias_siguientes in cabecera["estadisticas"].items():
        codigos_binarios = construir_arbol_y_codigos(frecuencias_siguientes)

        # Invertimos el diccionario para este contexto
        # Si {'A': '0', 'B': '10'}, lo pasamos a {'0': 'A', '10': 'B'}
        decodificador_markov[byte_ant] = {codigo: simbolo for simbolo, codigo in codigos_binarios.items()}
        # Si el buffer supera el código más largo del contexto, los datos están corruptos
        longitud_maxima[byte_ant] = max(len(codigo) for codigo in codigos_binarios.values())

    # 2. El primer byte iba "gratis" en la cabecera
    primer_byte = cabecera["primer_byte"]
    salida.append(primer_byte)

    # Mantenemos registro de cuánto nos falta decodificar (le restamos el primer byte)
    faltan_decodificar = longitud_original - 1
    contexto_actual = primer_byte
    buffer_bits = ""
    bytes_usados = 0

    # 3. Recorremos el payload byte a byte y cada byte bit a bit
    for byte in payload:
        # Si ya decodificamos todas las letras, cortamos.
        # Esto es clave porque el último byte podía tener ceros de "relleno"
        # que no son parte del mensaje original.
        if faltan_decodificar == 0:
            break
        bytes_usados += 1

        # Convertimos el byte a un string de 8 ceros y unos. Ej: el byte 5 -> "00000101"
        for bit in f"{byte:08b}":
            buffer_bits += bit

            tabla = decodificador_markov.get(contexto_actual)
            if tabla is None:
                raise ErrorFormatoTDI(f"datos corruptos: el contexto {contexto_actual} no existe en el modelo")

            # Chequeamos si la secuencia de bits que venimos juntando forma
            # una hoja válida en el árbol de nuestro contexto actual
            if buffer_bits in tabla:
                # ¡Encontramos la letra!
                byte_descubierto = tabla[buffer_bits]
                salida.append(byte_descubierto)

                # Actualizamos el contexto para la próxima letra y vaciamos el buffer
                contexto_actual = byte_descubierto
                buffer_bits = ""

                faltan_decodificar -= 1
                if faltan_decodificar == 0:
                    break
            elif len(buffer_bits) > longitud_maxima[contexto_actual]:
                raise ErrorFormatoTDI("datos corruptos: secuencia de bits que no corresponde a ningún código")

    # 4. Controles de datos insuficientes o sobrantes
    if faltan_decodificar > 0:
        raise ErrorFormatoTDI(f"datos insuficientes: se recuperaron {len(salida)} de {longitud_original} bytes "
                              "(archivo truncado o dañado)")
    if bytes_usados < len(payload):
        raise ErrorFormatoTDI(f"el archivo tiene {len(payload) - bytes_usados} bytes de más después de los datos "
                              "(archivo dañado)")

    return salida

def descomprimir(archivo_entrada, archivo_salida):
    """
    Descomprime archivo_entrada (.tdi) en archivo_salida y verifica el SHA-256.
    El archivo de salida solo se escribe si la decodificación y la verificación terminan bien.
    Devuelve un diccionario con los datos para el informe en pantalla.
    """
    t0 = time.perf_counter()

    with open(archivo_entrada, 'rb') as f_in:
        contenido = f_in.read()

    cabecera, inicio_payload = leer_cabecera(contenido)
    datos = decodificar(cabecera, contenido[inicio_payload:])

    # Validación de integridad: SHA256(original) = SHA256(reconstruido)
    sha_reconstruido = hashlib.sha256(datos).digest()
    if sha_reconstruido != cabecera["sha256"]:
        raise ErrorIntegridadTDI(f"el SHA-256 del archivo reconstruido ({sha_reconstruido.hex()}) no coincide "
                                 f"con el del original ({cabecera['sha256'].hex()})")

    with open(archivo_salida, 'wb') as f_out:
        f_out.write(datos)

    t_ms = (time.perf_counter() - t0) * 1000

    return {
        "entrada": archivo_entrada,
        "salida": archivo_salida,
        "tam_comprimido": len(contenido),
        "tam_cabecera": inicio_payload,
        "tam_reconstruido": len(datos),
        "contextos": len(cabecera["estadisticas"]),
        "tiempo_ms": t_ms,
        "sha256": sha_reconstruido.hex(),
    }

def imprimir_informe(r):
    tam_o, tam_c = r["tam_reconstruido"], r["tam_comprimido"]
    print("=== Descompresor TDI: Markov orden 1 + Huffman estático por contexto ===")
    print(f"Archivo de entrada:       {r['entrada']}")
    print(f"Archivo de salida:        {r['salida']}")
    print(f"Parámetros:               orden {ORDEN_MARKOV} | {r['contextos']} contextos | "
          f"formato {MAGIC.decode()} v{VERSION} | cabecera {r['tam_cabecera']} B")
    print(f"Tamaño comprimido:        {tam_c} B")
    print(f"Tamaño reconstruido:      {tam_o} B")
    if tam_o > 0:
        print(f"Ratio de compresión:      {tam_o / tam_c:.3f}")
        print(f"Ahorro de espacio:        {(1 - tam_c / tam_o) * 100:.2f} %")
    else:
        print("Ratio de compresión:      n/a (archivo vacío)")
        print("Ahorro de espacio:        n/a (archivo vacío)")
    print(f"Tiempo de descompresión:  {r['tiempo_ms']:.2f} ms")
    print(f"Integridad SHA-256:       OK ({r['sha256']})")

def salir_con_error(mensaje, codigo):
    print(f"Error: {mensaje}", file=sys.stderr)
    sys.exit(codigo)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python decompressor.py <archivo_entrada.tdi> <archivo_salida_recuperado.txt>", file=sys.stderr)
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2]

    if not os.path.exists(archivo_entrada):
        salir_con_error(f"no existe el archivo '{archivo_entrada}'", 2)
    if not os.path.isfile(archivo_entrada):
        salir_con_error(f"'{archivo_entrada}' no es un archivo", 2)
    if os.path.abspath(archivo_entrada) == os.path.abspath(archivo_salida):
        salir_con_error("el archivo de salida no puede ser el mismo que el de entrada", 2)

    try:
        resultado = descomprimir(archivo_entrada, archivo_salida)
    except ErrorFormatoTDI as e:
        salir_con_error(f"{e}. No se generó '{archivo_salida}'.", 3)
    except ErrorIntegridadTDI as e:
        salir_con_error(f"falla de integridad: {e}. No se generó '{archivo_salida}'.", 4)
    except OSError as e:
        salir_con_error(f"no se pudo leer o escribir '{e.filename}': {e.strerror}", 2)

    imprimir_informe(resultado)
