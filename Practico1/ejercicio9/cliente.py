#cliente.py
#   Fase 1: envia tramas binarias de distinta longitud, calcula el BER 
#           empirico de cada una, analiza como converge al aumentar N, 
#           y transmite un mensaje de texto para mostrar el efecto visual 
#           del ruido.
#
#   Fase 2: con el p estimado en la Fase 1 (tratado como la "probabilidad
#           teorica" configurada en el cliente) calcula la matriz del
#           canal, las probabilidades de la fuente, la Informacion Mutua
#           I(X;Y) de una transmision especifica y la Capacidad C del
#           canal, y compara ambos valores.
#

import socket
import struct
import random
import math
import statistics

# ==========================================================
# CONFIGURACION GENERAL
# ==========================================================
HOST = "127.0.0.1"
PUERTO = 5555


# ==========================================================
# PROTOCOLO DE COMUNICACION (identico al servidor)
# ==========================================================
def recibir_exactamente(sock, cantidad):
    datos = bytearray()
    while len(datos) < cantidad:
        bloque = sock.recv(cantidad - len(datos))
        if not bloque:
            raise ConnectionError("Conexion cerrada por el servidor.")
        datos.extend(bloque)
    return bytes(datos)

def recibir_mensaje(sock):
    encabezado = recibir_exactamente(sock, 4)
    longitud = struct.unpack("!I", encabezado)[0]
    datos = recibir_exactamente(sock, longitud)
    return datos.decode("ascii")

def enviar_mensaje(sock, mensaje):
    datos = mensaje.encode("ascii")
    encabezado = struct.pack("!I", len(datos))
    sock.sendall(encabezado + datos)

def transmitir(sock, trama):
    """Envia una trama binaria (string de '0'/'1') y devuelve la trama
    recibida luego de atravesar el canal ruidoso."""
    enviar_mensaje(sock, trama)
    return recibir_mensaje(sock)


# ==========================================================
# UTILIDADES: GENERACION DE TRAMAS, BER Y TEXTO <-> BINARIO
# ==========================================================
def generar_trama_aleatoria(n, rng):
    """Genera una trama de n bits equiprobables e independientes."""
    return "".join(rng.choice("01") for _ in range(n))

def calcular_ber(original, recibida):
    errores = sum(1 for a, b in zip(original, recibida) if a != b)
    ber = errores / len(original)
    return errores, ber

def texto_a_binario(texto):
    return "".join(format(b, "08b") for b in texto.encode("ascii", errors="replace"))

def binario_a_texto(binario):
    n = len(binario) // 8
    valores = [int(binario[i * 8:(i + 1) * 8], 2) for i in range(n)]
    # Los bytes que quedan fuera del rango imprimible se muestran en hex
    # entre corchetes para poder visualizar la corrupcion sin romper la salida.
    return "".join(chr(v) if 32 <= v <= 126 else f"[{v:02X}]" for v in valores)


# ==========================================================
# FASE 1: TRANSMISION Y TASA DE ERROR EMPIRICA (BER)
# ==========================================================
def fase1(sock):
    print("\n" + "=" * 70)
    print(" FASE 1: TRANSMISION Y TASA DE ERROR EMPIRICA (BER)")
    print("=" * 70)

    rng = random.Random()  # generador aleatorio del cliente
    tamanos = [100, 10000, 1000000, 10000000]  # N bits por trama
    repeticiones = {100: 5, 10000: 5, 1000000: 5, 10000000: 5}  # intentos por cada N

    resultados = {}
    varianzas = {}

    for n in tamanos:
        bers = []
        for r in range(repeticiones[n]):
            trama = generar_trama_aleatoria(n, rng)
            recibida = transmitir(sock, trama)
            errores, ber = calcular_ber(trama, recibida)
            bers.append(ber)
            print(f"  N={n:>9} | intento {r + 1}/{repeticiones[n]} | "
                  f"errores={errores:>7} | BER={ber:.6f}")

        promedio = sum(bers) / len(bers)
        # Varianza muestral del BER entre repeticiones de un mismo tamano N
        varianza = statistics.variance(bers) if len(bers) > 1 else 0.0
        resultados[n] = promedio
        varianzas[n] = varianza
        print(f"  --> BER promedio para N={n}: {promedio:.6f} | "
              f"Varianza muestral entre intentos: {varianza:.3e}\n")

    print("Analisis de convergencia (Ley de los Grandes Numeros):")
    print("Con N=100 el BER empirico varia bastante entre intentos (pocos")
    print("bits => alta varianza del estimador). A medida que N crece, el")
    print("BER empirico se estabiliza y converge hacia un unico valor: la")
    print("probabilidad de error real del canal 'p'.")

    # Usamos la trama mas larga como mejor estimador de p (menor varianza)
    p_estimado = resultados[max(tamanos)]
    print(f"\n>> Estimacion final de p (a partir de N={max(tamanos)}): {p_estimado:.6f}")

    return p_estimado


def fase1_mensaje_texto(sock):
    print("\n" + "-" * 70)
    print(" Efecto visual del ruido sobre un mensaje de texto")
    print("-" * 70)

    frase = "Teoria de la Informacion - Canal Binario Simetrico UNSJ FCEFN 2026"
    binario = texto_a_binario(frase)
    recibido_binario = transmitir(sock, binario)
    recibido_texto = binario_a_texto(recibido_binario)

    _, ber = calcular_ber(binario, recibido_binario)
    print(f"Mensaje original : {frase}")
    print(f"Mensaje recibido : {recibido_texto}")
    print(f"Bits enviados: {len(binario)} | BER de este mensaje: {ber:.6f}")

    return frase, binario, recibido_binario


def fase1_mensaje_degenerado(sock, n_caracteres):
    """Mensaje MUY redundante (un caracter repetido), del mismo tamano en
    caracteres que el mensaje de texto de la Fase 1 (y por lo tanto de la
    misma longitud en bits una vez codificado). Sirve como contraejemplo en
    la Fase 2: al no ser una fuente equiprobable, deberia alejar a I(X;Y) de
    la Capacidad C de forma mucho mas marcada que un texto natural."""
    print("\n" + "-" * 70)
    print(" Mensaje degenerado (muy redundante) para contrastar en la Fase 2")
    print("-" * 70)

    frase = "A" * n_caracteres  # 'A' = 01000001 -> 6 ceros y 2 unos por caracter
    binario = texto_a_binario(frase)
    recibido_binario = transmitir(sock, binario)
    recibido_texto = binario_a_texto(recibido_binario)

    _, ber = calcular_ber(binario, recibido_binario)
    print(f"Mensaje original : {frase[:20]}... (x{len(frase)})")
    print(f"Mensaje recibido : {recibido_texto}")
    print(f"Bits enviados: {len(binario)} | BER de este mensaje: {ber:.6f}")

    return binario, recibido_binario


# ==========================================================
# FASE 2: MODELADO MATEMATICO Y CAPACIDAD DEL CANAL
# ==========================================================
def h2(p):
    """Entropia binaria H(p) en bits (0 si p es 0 o 1)."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def analizar_canal(p, trama_enviada, trama_recibida, etiqueta):
    print("\n" + "-" * 70)
    print(f" Analisis Fase 2 para: {etiqueta}")
    print("-" * 70)

    # --- Matriz del canal (probabilidades de transicion P(Y|X)) ---
    print("Matriz de canal (BSC):")
    print("          y=0      y=1")
    print(f"  x=0 |  {1 - p:.4f}   {p:.4f}")
    print(f"  x=1 |  {p:.4f}   {1 - p:.4f}")

    # --- Probabilidades de la fuente (frecuencia relativa en la trama enviada) ---
    n = len(trama_enviada)
    ceros = trama_enviada.count("0")
    unos = n - ceros
    p0 = ceros / n
    p1 = unos / n
    print(f"\nProbabilidades de la fuente (trama enviada, N={n}):")
    print(f"  P(0) = {p0:.4f}   P(1) = {p1:.4f}")

    # --- Distribucion de salida P(Y), a partir de la fuente y el canal ---
    py0 = p0 * (1 - p) + p1 * p
    py1 = p0 * p + p1 * (1 - p)

    # --- Entropias e Informacion Mutua de ESTA transmision ---
    Hy = h2(py0)   # H(Y): como Y es binaria, H(py0) = H(py1)
    Hyx = h2(p)    # H(Y|X) = H(p) (igual para x=0 y x=1 por ser canal simetrico)
    I = Hy - Hyx

    # --- Capacidad del canal: maximo de I(X;Y) sobre todas las P(X) ---
    # Para un BSC, el maximo de H(Y) es 1 bit (se logra con P(Y=0)=P(Y=1)=0.5,
    # lo cual ocurre cuando la fuente es equiprobable P(0)=P(1)=0.5).
    C = 1 - h2(p)

    print(f"\nH(Y)       = {Hy:.6f} bits")
    print(f"H(Y|X)     = {Hyx:.6f} bits   (= H(p), entropia propia del canal)")
    print(f"I(X;Y)     = {I:.6f} bits   <- informacion mutua de esta transmision")
    print(f"C = 1-H(p) = {C:.6f} bits   <- capacidad maxima del canal")

    diferencia_relativa = abs(C - I) / C if C > 0 else 0.0
    margen = 0.10  # 10%
    maximiza = diferencia_relativa <= margen
    print(f"Diferencia relativa (C-I)/C = {diferencia_relativa * 100:.2f}% "
          f"({'dentro' if maximiza else 'fuera'} del margen de {margen * 100:.0f}%)")

    return p0, p1, I, C, maximiza


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================
def main():
    with socket.create_connection((HOST, PUERTO)) as sock:
        p_estimado = fase1(sock)
        frase, binario_msg, recibido_msg = fase1_mensaje_texto(sock)
        binario_deg, recibido_deg = fase1_mensaje_degenerado(sock, len(frase))

        # Trama binaria aleatoria del MISMO tamano (en bits) que la
        # codificacion binaria del mensaje de texto, generada especificamente
        # para comparar en la Fase 2 en igualdad de condiciones (mismo N,
        # distinta distribucion de la fuente).
        rng_fase2 = random.Random()
        n_bits = len(binario_msg)
        binario_rand = generar_trama_aleatoria(n_bits, rng_fase2)
        recibido_rand = transmitir(sock, binario_rand)
        _, ber_rand = calcular_ber(binario_rand, recibido_rand)
        print("\n" + "-" * 70)
        print(" Trama aleatoria de comparacion (mismo tamano que el mensaje de texto)")
        print("-" * 70)
        print(f"Bits enviados: {n_bits} | BER de esta trama: {ber_rand:.6f}")

        print("\n" + "=" * 70)
        print(" FASE 2: MODELADO MATEMATICO Y CAPACIDAD DEL CANAL")
        print("=" * 70)
        print(f"Se utiliza p = {p_estimado:.6f} (estimado empiricamente en la Fase 1")
        print("con la trama de mayor tamano) como la probabilidad de error TEORICA")
        print("configurada en el cliente para el resto de los calculos.")
        print(f"\nLas tres transmisiones comparadas a continuacion tienen el mismo")
        print(f"tamano N={n_bits} bits (la longitud de la codificacion binaria del")
        print("mensaje de texto de la Fase 1), para que la comparacion de sus")
        print("distribuciones de fuente sea en igualdad de condiciones.")

        # 1) El mensaje de texto natural de la Fase 1 (fuente levemente sesgada:
        #    el ASCII de texto legible concentra algo mas de ceros que unos)
        analizar_canal(p_estimado, binario_msg, recibido_msg,
                       f"mensaje de texto de la Fase 1 (N={n_bits})")

        # 2) El mismo mensaje degenerado a puro caracter 'A' repetido, del
        #    mismo tamano (fuente muy sesgada y redundante, P(0) ~ 0.75)
        analizar_canal(p_estimado, binario_deg, recibido_deg,
                       f"mensaje degenerado 'AAAA...A' (N={n_bits})")

        # 3) Una trama binaria aleatoria del mismo tamano (fuente equiprobable
        #    e independiente, P(0) ~ P(1) ~ 0.5)
        analizar_canal(p_estimado, binario_rand, recibido_rand,
                       f"trama binaria aleatoria del mismo tamano (N={n_bits})")

        enviar_mensaje(sock, "SALIR")

    # ------------------------------------------------------------------
    # ANALISIS DE MAXIMIZACION (respuesta al ultimo punto de la Fase 2)
    #
    # Las tres transmisiones comparadas tienen EXACTAMENTE el mismo tamano N
    # (la longitud en bits de la codificacion del mensaje de texto), asi que
    # cualquier diferencia en I(X;Y) se debe unicamente a la distribucion de
    # la fuente P(X), no a que unas tengan mas bits que otras. Resultados de
    # una corrida tipica (p estimado ~ 0.061, C = 1 - H(p) ~ 0.669 bits,
    # margen aceptado = 10%):
    #
    #   Transmision (mismo N)                P(0)    I(X;Y)   Dif. vs C
    #   mensaje de texto de la Fase 1         0.566    0.659     1.47%   -> DENTRO del margen
    #   mensaje degenerado "AAAA...A"         0.750    0.525    21.52%   -> FUERA del margen
    #   trama binaria aleatoria (mismo N)    ~0.500    0.668     0.17%   -> DENTRO del margen
    #
    # - El MENSAJE DE TEXTO DE LA FASE 1 cae dentro del margen, pero
    #   no es una fuente "perfecta": el ASCII de un texto legible 
    #   nunca es exactamente equiprobable, por lo que P(0) queda
    #   un poco por encima de 0.5. Dado que el canal tiene una p baja
    #   (~0.06), un sesgo chico en la fuente no alcanza a mover a I(X;Y)
    #   fuera del margen de tolerancia.
    #
    # - El MENSAJE REDUNDANTE ("AAAA...A", el MISMO mensaje pero llevado al
    #   extremo de un unico caracter repetido, con P(0)~0.75). Al tener el 
    #   mismo N que el mensaje de texto pero una distribucion de probabilidades
    #   mas sesgada, su I(X;Y) queda muy por debajo de C, FUERA del margen de 10%.
    #
    # - La TRAMA BINARIA ALEATORIA DEL MISMO TAMANO (bits generados con
    #   random.choice, P(0)~P(1)~0.5) logra maximizar la capacidad:
    #   I(X;Y) practicamente coincide con C, confirmando que el maximo 
    #   de I(X;Y) respecto de P(X) se alcanza con una fuente equiprobable.
    #
    # - CONCLUSION: para que una trama de bits alcance la Capacidad C,
    #   debe tener sus simbolos 0 y 1 EQUIPROBABLES (P(0) = P(1) = 0.5) y
    #   estadisticamente INDEPENDIENTES entre si, tal como lo muestra la 
    #   trama aleatoria de comparacion.
    #   En la practica, un mensaje de texto real se acerca a esa condicion
    #   aplicandole antes una compresion o codificacion de fuente (por
    #   ejemplo Huffman u otro codigo optimo), que elimina su redundancia
    #   estadistica y aproxima la distribucion de bits resultante a la
    #   uniforme.
    # ------------------------------------------------------------------


if __name__ == "__main__":
    main()
