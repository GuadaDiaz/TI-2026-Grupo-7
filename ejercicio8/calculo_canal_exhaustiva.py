import math


# ---------------------------------------------------------
# Función para calcular la entropía
# ---------------------------------------------------------
def entropia(probabilidades):
    H = 0.0

    for p in probabilidades:
        if p > 0:
            H -= p * math.log2(p)

    return H


# ---------------------------------------------------------
# INGRESO DE LA MATRIZ DEL CANAL
# ---------------------------------------------------------
print("==============================================")
print(" CÁLCULO DE CAPACIDAD DE CANAL")
print(" Canal binario -> cuaternario (2x4)")
print("==============================================\n")

print("Ingrese las probabilidades P(Y|X).")
print("La matriz tiene 2 filas y 4 columnas.\n")

while True:

    canal = []

    for i in range(2):
        while True:
            print(f"\nFila X={i}")

            fila = []

            for j in range(4):
                while True:
                    try:
                        p = float(input(f"P(Y={j}|X={i}): "))

                        if 0 <= p <= 1:
                            fila.append(p)
                            break
                        else:
                            print("Error: la probabilidad debe estar entre 0 y 1.")

                    except ValueError:
                        print("Error: ingrese un número válido.")

            # Validación de que la fila suma 1
            suma = sum(fila)

            if math.isclose(suma, 1.0, abs_tol=1e-9):
                canal.append(fila)
                break
            else:
                print("\nERROR: la suma de la fila no es igual a 1.")
                print(f"Suma obtenida: {suma:.10f}")
                print("Debe volver a ingresar esta fila.")

    break


# ---------------------------------------------------------
# MOSTRAR MATRIZ DEL CANAL
# ---------------------------------------------------------
print("\n==============================================")
print(" MATRIZ DEL CANAL P(Y|X)")
print("==============================================")

for fila in canal:
    print("[", "  ".join(f"{p:.4f}" for p in fila), "]")


# ---------------------------------------------------------
# BÚSQUEDA EXHAUSTIVA
# ---------------------------------------------------------

max_info_mutua = -1
mejor_px0 = 0
mejor_px1 = 0
mejor_py = []
mejor_hy = 0
mejor_hyx = 0


# P(X=0) toma valores 0.00, 0.01, ..., 1.00
for i in range(101):

    px0 = i / 100
    px1 = 1 - px0

    # -----------------------------------------------------
    # P(Y) mediante el Teorema de la Probabilidad Total
    #
    # P(Y=y) = P(X=0)P(Y=y|X=0)
    #        + P(X=1)P(Y=y|X=1)
    # -----------------------------------------------------

    py = []

    for y in range(4):

        prob_y = (
            px0 * canal[0][y]
            + px1 * canal[1][y]
        )

        py.append(prob_y)

    # -----------------------------------------------------
    # H(Y)
    # -----------------------------------------------------

    hy = entropia(py)

    # -----------------------------------------------------
    # H(Y|X)
    #
    # H(Y|X) = P(X=0) H(Y|X=0)
    #        + P(X=1) H(Y|X=1)
    # -----------------------------------------------------

    h_y_x0 = entropia(canal[0])
    h_y_x1 = entropia(canal[1])

    h_yx = (
        px0 * h_y_x0
        + px1 * h_y_x1
    )

    # -----------------------------------------------------
    # INFORMACIÓN MUTUA
    #
    # I(X;Y) = H(Y) - H(Y|X)
    # -----------------------------------------------------

    info_mutua = hy - h_yx

    # -----------------------------------------------------
    # MAXIMIZACIÓN
    # -----------------------------------------------------

    if info_mutua > max_info_mutua:

        max_info_mutua = info_mutua

        mejor_px0 = px0
        mejor_px1 = px1

        mejor_py = py.copy()
        mejor_hy = hy
        mejor_hyx = h_yx


# ---------------------------------------------------------
# RESULTADOS
# ---------------------------------------------------------

print("\n==============================================")
print(" RESULTADO DE LA BÚSQUEDA EXHAUSTIVA")
print("==============================================")

print(f"\nCapacidad del Canal:")
print(f"C = {max_info_mutua:.6f} bits/símbolo")

print("\nDistribución de entrada que maximiza el canal:")
print(f"P(X=0) = {mejor_px0:.2f}")
print(f"P(X=1) = {mejor_px1:.2f}")

print("\nProbabilidades de salida para la distribución óptima:")
for y in range(4):
    print(f"P(Y={y}) = {mejor_py[y]:.6f}")

print("\nEntropía de salida:")
print(f"H(Y) = {mejor_hy:.6f} bits")

print("\nEntropía condicional / ruido del canal:")
print(f"H(Y|X) = {mejor_hyx:.6f} bits")

print("\nInformación Mutua máxima:")
print(f"I(X;Y) = {max_info_mutua:.6f} bits/símbolo")

print("\n==============================================")
