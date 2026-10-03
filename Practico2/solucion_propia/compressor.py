import sys
import heapq
import pickle
from collections import defaultdict, Counter

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

def recolectar_estadistica_markov(ruta_archivo):
    """
    Paso 1: Leer el archivo y contar las transiciones de Markov de Orden 1.
    Devuelve un diccionario donde la clave es el "byte anterior" y 
    el valor es un contador (Counter) con las frecuencias del "byte actual".
    """
    # Usamos defaultdict para inicializar automáticamente los contadores
    # transiciones[byte_anterior][byte_actual] = cantidad
    transiciones = defaultdict(Counter)
    
    with open(ruta_archivo, 'rb') as f:
        datos = f.read()
        
    if not datos:
        return transiciones # Archivo vacío
        
    # Recorremos los datos desde el segundo byte (índice 1) hasta el final
    for i in range(1, len(datos)):
        byte_anterior = datos[i-1]
        byte_actual = datos[i]
        
        # Sumamos 1 a la cuenta de esa transición específica
        transiciones[byte_anterior][byte_actual] += 1
        
    return transiciones

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python compressor.py <archivo_entrada> <archivo_salida.tdi>")
        sys.exit(1)
        
    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2]
    
    print(f"Comprimiendo {archivo_entrada}...")
    
    # 1. Recolectar estadísticas
    estadisticas = recolectar_estadistica_markov(archivo_entrada)
    print(f"Estadísticas recolectadas para {len(estadisticas)} contextos (bytes anteriores) diferentes.\n")

    # -------------------------------------------------------------------------------------------
    
    # 2. Armar los árboles de Huffman para cada contexto
        # Diccionario final que guardará los códigos de cada letra, dependiendo de la letra anterior
        # codigos_markov[byte_anterior][byte_actual] = "0101"
    codigos_markov = {}
    
    for byte_ant, frecuencias_siguientes in estadisticas.items():
        # Para cada "contexto" (byte_ant), construimos su propio arbolito
        codigos_binarios = construir_arbol_y_codigos(frecuencias_siguientes)
        codigos_markov[byte_ant] = codigos_binarios
            
    # 3. Escribimos la cabecera y los datos comprimidos
    print("Escribiendo archivo comprimido...")
    
    with open(archivo_entrada, 'rb') as f_in, open(archivo_salida, 'wb') as f_out:
        datos = f_in.read()
        
        # Primero guardamos la estadística (las frecuencias) para que el descompresor pueda armar los mismos árboles
        # También le pasamos el primer byte (ya que no tiene contexto) y la longitud total original.
        if len(datos) > 0:
            primer_byte = datos[0]
            longitud_original = len(datos)
        else:
            primer_byte = None
            longitud_original = 0
            
        cabecera = {
            "primer_byte": primer_byte,
            "longitud_original": longitud_original,
            "estadisticas": estadisticas
        }
        
        # Usamos pickle para convertir el diccionario de Python directamente a bytes y guardarlo
        pickle.dump(cabecera, f_out)
        
        # Si el archivo está vacío, terminamos acá
        if longitud_original <= 1:
            print("\nListo! Archivo comprimido generado.")
            sys.exit(0)
            
        # Segunda pasada: Codificación
        bits_comprimidos = ""
        
        for i in range(1, len(datos)):
            byte_anterior = datos[i-1]
            byte_actual = datos[i]
            
            # Buscamos el código para la letra actual, dándole el contexto (letra anterior)
            codigo = codigos_markov[byte_anterior][byte_actual]
            bits_comprimidos += codigo
            
            # Para evitar que el string de bits se vuelva infinito y ocupe toda la RAM,
            # lo vamos bajando a disco cada vez que juntamos al menos 8 bits.
            while len(bits_comprimidos) >= 8:
                # Agarramos los primeros 8 "ceros y unos"
                byte_str = bits_comprimidos[:8]
                # Lo convertimos a un número real (byte) de base 2
                byte_val = int(byte_str, 2)
                # Lo escribimos en el archivo de salida
                f_out.write(bytes([byte_val]))
                # Borramos los 8 bits que ya escribimos
                bits_comprimidos = bits_comprimidos[8:]
                
        # Si sobraron bits al final (ej: quedaron 3 bits colgados), les agregamos ceros
        # a la derecha (padding) para completar un byte y escribirlo.
        if len(bits_comprimidos) > 0:
            bits_comprimidos = bits_comprimidos.ljust(8, '0')
            byte_val = int(bits_comprimidos, 2)
            f_out.write(bytes([byte_val]))

    print(f"Listo! Archivo guardado como {archivo_salida}")
