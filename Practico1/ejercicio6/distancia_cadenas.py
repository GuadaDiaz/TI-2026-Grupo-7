# ==========================================================
# MEDICIÓN DE DISTANCIA ENTRE CADENAS
# Distancia de Hamming y Distancia de Levenshtein
# ==========================================================


# ----------------------------------------------------------
# DISTANCIA DE HAMMING
# ----------------------------------------------------------

def distancia_hamming(cadena1, cadena2):

    # La distancia de Hamming solamente se puede calcular
    # correctamente entre cadenas de igual longitud.
    if len(cadena1) != len(cadena2):
        return None

    distancia = 0

    for i in range(len(cadena1)):
        if cadena1[i] != cadena2[i]:
            distancia += 1

    return distancia


# ----------------------------------------------------------
# DISTANCIA DE LEVENSHTEIN
# ----------------------------------------------------------

def distancia_levenshtein(cadena1, cadena2):

    filas = len(cadena1) + 1
    columnas = len(cadena2) + 1

    # Crear matriz de distancias
    matriz = [[0 for j in range(columnas)] for i in range(filas)]

    # Distancia de transformar una cadena en una cadena vacía
    for i in range(filas):
        matriz[i][0] = i

    # Distancia de transformar una cadena vacía en otra cadena
    for j in range(columnas):
        matriz[0][j] = j

    # Calcular la matriz
    for i in range(1, filas):
        for j in range(1, columnas):

            if cadena1[i - 1] == cadena2[j - 1]:
                costo = 0
            else:
                costo = 1

            insercion = matriz[i][j - 1] + 1
            eliminacion = matriz[i - 1][j] + 1
            sustitucion = matriz[i - 1][j - 1] + costo

            matriz[i][j] = min(
                insercion,
                eliminacion,
                sustitucion
            )

    return matriz[filas - 1][columnas - 1]


# ----------------------------------------------------------
# HEURÍSTICA DE COMPARACIÓN
# ----------------------------------------------------------

def comparar_cadenas(cadena1, cadena2):

    distancia = distancia_levenshtein(cadena1, cadena2)

    longitud_maxima = max(len(cadena1), len(cadena2))

    # Evitar división por cero
    if longitud_maxima == 0:
        similitud = 100
    else:
        similitud = (1 - distancia / longitud_maxima) * 100

    return distancia, similitud


# ----------------------------------------------------------
# PROGRAMA PRINCIPAL
# ----------------------------------------------------------

print("===================================================")
print("       MEDICIÓN DE DISTANCIA ENTRE CADENAS")
print("===================================================")

cadena1 = input("\nIngrese la primera cadena: ")
cadena2 = input("Ingrese la segunda cadena: ")


# ----------------------------------------------------------
# HAMMING
# ----------------------------------------------------------

hamming = distancia_hamming(cadena1, cadena2)

print("\n---------------------------------------------------")
print("DISTANCIA DE HAMMING")
print("---------------------------------------------------")

if hamming is None:
    print("No se puede calcular la Distancia de Hamming.")
    print("Las cadenas tienen distinta longitud.")
else:
    print(f"Distancia de Hamming: {hamming}")


# ----------------------------------------------------------
# LEVENSHTEIN
# ----------------------------------------------------------

levenshtein = distancia_levenshtein(cadena1, cadena2)

print("\n---------------------------------------------------")
print("DISTANCIA DE LEVENSHTEIN")
print("---------------------------------------------------")

print(f"Distancia de Levenshtein: {levenshtein}")


# ----------------------------------------------------------
# SIMILITUD
# ----------------------------------------------------------

distancia, similitud = comparar_cadenas(cadena1, cadena2)

print("\n---------------------------------------------------")
print("HEURÍSTICA DE COMPARACIÓN")
print("---------------------------------------------------")

print(f"Distancia de edición: {distancia}")
print(f"Similitud aproximada: {similitud:.2f}%")

if similitud >= 90:
    print("Resultado: las cadenas son MUY similares.")
elif similitud >= 70:
    print("Resultado: las cadenas son similares.")
elif similitud >= 50:
    print("Resultado: las cadenas tienen similitud moderada.")
else:
    print("Resultado: las cadenas son poco similares.")

print("\n===================================================")
