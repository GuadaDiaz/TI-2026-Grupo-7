import os
import sys
import time
import heapq
import pickle
import hashlib
from collections import defaultdict, Counter

# Identificación del formato .tdi. El descompresor verifica la "firma" (magic bytes)
# y la versión antes de leer la cabecera, así detecta archivos que no son .tdi.
MAGIC = b"TDMH"        # TDI - Markov + Huffman
VERSION = 1
ORDEN_MARKOV = 1

class NodoHuffman:
    """Clase para representar un nodo del árbol de Huffman"""
    def __init__(self, simbolo, frecuencia):
        self.simbolo = simbolo
        self.frecuencia = frecuencia
        self.izq = None
        self.der = None

    # Necesitamos decirle a Python cómo comparar dos nodos para poder ordenarlos
    # de menor a mayor frecuencia en nuestra lista (el "heap")
    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia

def construir_arbol_y_codigos(frecuencias):
    """
    Recibe un diccionario {byte: cantidad} y devuelve un diccionario {byte: "codigo_binario"}
    """
    # Si solo hay un símbolo posible, le damos un código fijo (ej. "0")
    if len(frecuencias) == 1:
        simbolo = list(frecuencias.keys())[0]
        return {simbolo: "0"}

    # 1. Creamos un nodo por cada símbolo y los metemos en una lista
    lista_nodos = [NodoHuffman(simbolo, freq) for simbolo, freq in frecuencias.items()]

    # Transformamos la lista en una "cola de prioridad" (heap) para que los nodos de menor frecuencia queden siempre arriba de todo, listos para sacar.
    heapq.heapify(lista_nodos)

    # 2. Agrupar subárboles hasta que quede 1 solo nodo (la raíz del árbol)
    while len(lista_nodos) > 1:
        # Sacamos los dos nodos menos probables
        nodo1 = heapq.heappop(lista_nodos)
        nodo2 = heapq.heappop(lista_nodos)

        # Creamos un "nodo padre" sin símbolo (None) cuya frecuencia es la suma de los dos hijos.
        padre = NodoHuffman(None, nodo1.frecuencia + nodo2.frecuencia)
        padre.izq = nodo1
        padre.der = nodo2

        # Volvemos a meter al padre en la bolsa para que compita con los demás
        heapq.heappush(lista_nodos, padre)

    # El último nodo que queda en la bolsa es la raíz del árbol completo
    raiz = lista_nodos[0]

    # 3. Recorrer el árbol para generar los "0" y "1"
    codigos_binarios = {}

    def generar_codigos_recursivo(nodo, prefijo_actual):
        if nodo is not None:
            # Si tiene un símbolo real, se llegó a una hoja. Guardamos el código.
            if nodo.simbolo is not None:
                codigos_binarios[nodo.simbolo] = prefijo_actual
            # Si no, seguimos bajando: agregamos "0" a la izquierda y "1" a la derecha
            generar_codigos_recursivo(nodo.izq, prefijo_actual + "0")
            generar_codigos_recursivo(nodo.der, prefijo_actual + "1")

    generar_codigos_recursivo(raiz, "")

    return codigos_binarios

def recolectar_estadistica_markov(datos):
    """
    Paso 1: Contar las transiciones de Markov de Orden 1 sobre los bytes del archivo.
    Devuelve un diccionario donde la clave es el "byte anterior" y
    el valor es un contador (Counter) con las frecuencias del "byte actual".
    """
    # Usamos defaultdict para inicializar automáticamente los contadores
    # transiciones[byte_anterior][byte_actual] = cantidad
    transiciones = defaultdict(Counter)

    # Recorremos los datos desde el segundo byte (índice 1) hasta el final.
    # Si el archivo tiene 0 o 1 bytes no hay transiciones.
    for i in range(1, len(datos)):
        byte_anterior = datos[i-1]
        byte_actual = datos[i]

        # Sumamos 1 a la cuenta de esa transición específica
        transiciones[byte_anterior][byte_actual] += 1

    return transiciones

def codificar(datos, codigos_markov):
    """
    Paso 3: Recorre los datos y concatena el código de cada byte según su contexto
    (el byte anterior). Devuelve los bits empaquetados en bytes (bytearray).
    """
    salida = bytearray()
    bits_comprimidos = ""

    for i in range(1, len(datos)):
        byte_anterior = datos[i-1]
        byte_actual = datos[i]

        # Buscamos el código para la letra actual, dándole el contexto (letra anterior)
        bits_comprimidos += codigos_markov[byte_anterior][byte_actual]

        # Cada vez que juntamos al menos 8 bits, los pasamos a un byte real
        # para que el string de bits no crezca indefinidamente.
        while len(bits_comprimidos) >= 8:
            salida.append(int(bits_comprimidos[:8], 2))
            bits_comprimidos = bits_comprimidos[8:]

    # Si sobraron bits al final (ej: quedaron 3 bits colgados), les agregamos ceros
    # a la derecha (padding) para completar un byte. El descompresor sabe dónde
    # cortar porque conoce la longitud original.
    if len(bits_comprimidos) > 0:
        salida.append(int(bits_comprimidos.ljust(8, '0'), 2))

    return salida

def comprimir(archivo_entrada, archivo_salida):
    """
    Comprime archivo_entrada y escribe archivo_salida (.tdi).
    Devuelve un diccionario con los datos para el informe en pantalla.
    """
    t0 = time.perf_counter()

    # El archivo se lee una sola vez, en modo binario, para conservar los bytes exactos
    with open(archivo_entrada, 'rb') as f_in:
        datos = f_in.read()

    # 1. Recolectar estadísticas
    estadisticas = recolectar_estadistica_markov(datos)

    # La cabecera guarda todo lo necesario para descomprimir sin el archivo original:
    #  - primer_byte: no tiene contexto, va "gratis" en la cabecera
    #  - longitud_original: indica dónde terminan los datos (descarta el padding)
    #  - sha256: hash del original, para verificar la integridad al descomprimir
    #  - estadisticas: frecuencias de Markov, para reconstruir los mismos árboles.
    #    Se guardan como diccionarios comunes (no defaultdict/Counter): mismo contenido
    #    y mismo orden, pero la serialización es más chica.
    cabecera = {
        "primer_byte": datos[0] if datos else None,
        "longitud_original": len(datos),
        "sha256": hashlib.sha256(datos).digest(),
        "estadisticas": {byte_ant: dict(frec) for byte_ant, frec in estadisticas.items()},
    }
    cabecera_bytes = MAGIC + bytes([VERSION]) + pickle.dumps(cabecera)

    # 2. Armar los árboles de Huffman para cada contexto
        # Diccionario final que guardará los códigos de cada letra, dependiendo de la letra anterior
        # codigos_markov[byte_anterior][byte_actual] = "0101"
        # Se arman a partir de lo que va en la cabecera, igual que hará el descompresor.
    codigos_markov = {}
    for byte_ant, frecuencias_siguientes in cabecera["estadisticas"].items():
        # Para cada "contexto" (byte_ant), construimos su propio arbolito
        codigos_markov[byte_ant] = construir_arbol_y_codigos(frecuencias_siguientes)

    # 3. Codificar y escribir el archivo comprimido
    payload = codificar(datos, codigos_markov)
    with open(archivo_salida, 'wb') as f_out:
        f_out.write(cabecera_bytes)
        f_out.write(payload)

    t_ms = (time.perf_counter() - t0) * 1000

    return {
        "entrada": archivo_entrada,
        "salida": archivo_salida,
        "tam_original": len(datos),
        "tam_comprimido": len(cabecera_bytes) + len(payload),
        "tam_cabecera": len(cabecera_bytes),
        "contextos": len(estadisticas),
        "deterministas": sum(1 for frec in estadisticas.values() if len(frec) == 1),
        "tiempo_ms": t_ms,
        "sha256": cabecera["sha256"].hex(),
    }

def imprimir_informe(r):
    tam_o, tam_c = r["tam_original"], r["tam_comprimido"]
    print("=== Compresor TDI: Markov orden 1 + Huffman estático por contexto ===")
    print(f"Archivo de entrada:    {r['entrada']}")
    print(f"Archivo de salida:     {r['salida']}")
    print(f"Parámetros:            orden {ORDEN_MARKOV} | {r['contextos']} contextos "
          f"({r['deterministas']} deterministas) | formato {MAGIC.decode()} v{VERSION}")
    print(f"Tamaño original:       {tam_o} B")
    print(f"Tamaño comprimido:     {tam_c} B (cabecera {r['tam_cabecera']} B, "
          f"overhead {r['tam_cabecera'] / tam_c * 100:.2f} %)")
    if tam_o > 0:
        print(f"Ratio de compresión:   {tam_o / tam_c:.3f}")
        print(f"Ahorro de espacio:     {(1 - tam_c / tam_o) * 100:.2f} %")
    else:
        print("Ratio de compresión:   n/a (archivo vacío)")
        print("Ahorro de espacio:     n/a (archivo vacío)")
    print(f"Tiempo de compresión:  {r['tiempo_ms']:.2f} ms")
    print(f"SHA-256 del original:  {r['sha256']}")

def salir_con_error(mensaje, codigo):
    print(f"Error: {mensaje}", file=sys.stderr)
    sys.exit(codigo)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python compressor.py <archivo_entrada> <archivo_salida.tdi>", file=sys.stderr)
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2]

    # Errores básicos: archivo inexistente, carpeta en lugar de archivo, o pisar el original
    if not os.path.exists(archivo_entrada):
        salir_con_error(f"no existe el archivo de entrada '{archivo_entrada}'", 2)
    if not os.path.isfile(archivo_entrada):
        salir_con_error(f"'{archivo_entrada}' no es un archivo", 2)
    if os.path.abspath(archivo_entrada) == os.path.abspath(archivo_salida):
        salir_con_error("el archivo de salida no puede ser el mismo que el de entrada", 2)

    try:
        resultado = comprimir(archivo_entrada, archivo_salida)
    except OSError as e:
        salir_con_error(f"no se pudo leer o escribir '{e.filename}': {e.strerror}", 2)

    imprimir_informe(resultado)
