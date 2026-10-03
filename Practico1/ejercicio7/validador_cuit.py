# Ejercicio 7 - Validacion del CUIT/CUIL Argentino mediante el algoritmo Modulo 11
# Item a): Fundamento
# El CUIT/CUIL tiene 11 digitos con la forma:
#   - AA        : tipo (20=hombre, 27=mujer, 30=empresa, etc.)
#   - XXXXXXXX  : numero de DNI (8 digitos)
#   - V         : digito verificador (checksum)
# ALGORITMO MÓDULO 11:
#   1. Tomar los primeros 10 digitos d[0..9]
#   2. Multiplicarlos por los pesos: [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
#   3. Sumar los productos (S = di x pi)
#   4. Calcular el resto: R = S mod 11
#   5. Dígito esperado:
#        R == 0  --> verificador = 0
#        R == 1  --> verificador = 9   (caso especial definido por AFIP)
#        R >= 2  --> verificador = 11 - R


# Ítem b): Funcion que solicita el CUIT/CUIL al usuario
def solicitar_cuit() -> str:
    """
    Solicita al usuario ingresar un número de CUIT/CUIL de 11 digitos.
    Acepta el formato con guiones (AA-XXXXXXXX-V) o sin ellos (AAAXXXXXXXXV).
    Retorna la cadena limpia de solo 11 digitos numericos.
    """
    while True:
        entrada = input("\nIngrese el CUIT/CUIL (11 digitos, con o sin guiones): ")

        # Eliminar guiones para normalizar la entrada
        cuit_limpio = entrada.replace("-", "").strip()

        # Validar que tenga exactamente 11 digitos y todos sean numericos
        if len(cuit_limpio) == 11 and cuit_limpio.isdigit():
            return cuit_limpio
        else:
            print("Formato invalido. Ingrese exactamente 11 digitos numericos.")


# Item c): Funcion que aplica el algoritmo
def calcular_digito_verificador(diez_digitos: str) -> int:
    """
    Aplica el algoritmo Módulo 11 para calcular el dígito verificador esperado.

    Parámetros:
        diez_digitos (str): cadena de exactamente 10 digitos (posiciones 0 a 9 del CUIT).

    Retorna:
        int: el dígito verificador calculado (0-9).
    """
    # Secuencia de pesos definida por AFIP para el algoritmo Modulo 11
    PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    # Paso 1: Multiplicar cada dígito por su peso correspondiente y sumar
    suma = sum(int(digito) * peso for digito, peso in zip(diez_digitos, PESOS))

    # Paso 2: Calcular el resto de dividir la suma por 11
    resto = suma % 11

    # Paso 3: Determinar el dígito verificador según las reglas del algoritmo
    if resto == 0:
        return 0
    elif resto == 1:
        return 9  # Caso especial definido por la normativa de AFIP
    else:
        return 11 - resto


# -----------------------------------------------------------------------------
# Ítem d): Función que valida el CUIT completo e informa el resultado
# -----------------------------------------------------------------------------
def validar_cuit(cuit: str) -> bool:
    """
    Valida si el CUIT/CUIL ingresado es correcto comparando el dígito
    verificador real (posición 11) con el calculado por Modulo 11.

    Muestra en pantalla un informe detallado del proceso de validación,
    demostrando cómo actúa como un Código de Detección de Errores.

    Parámetros:
        cuit (str): CUIT/CUIL de 11 digitos ya normalizado.

    Retorna:
        bool: True si es válido, False si es invalido.
    """
    # Separar los primeros 10 digitos del dígito verificador ingresado
    primeros_diez = cuit[:10]
    digito_ingresado = int(cuit[10])

    # Aplicar el algoritmo para obtener el verificador esperado
    digito_esperado = calcular_digito_verificador(primeros_diez)

    # --- Informe detallado ---
    PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(d) * p for d, p in zip(primeros_diez, PESOS))
    resto = suma % 11
    
    print("=" * 55)
    print(f"  CUIT/CUIL ingresado : {cuit[:2]}-{cuit[2:10]}-{cuit[10]}")
    print(f"  Primeros 10 digitos : {primeros_diez}")
    print(f"  Dígito verificador  : {digito_ingresado}")
    print("-" * 55)
    print(f"  {'SUMA'} = {suma}")
    print(f"  {'SUMA mod 11'} = {resto}")
    print(f"  {'Dígito esperado'} = {digito_esperado}")
    print("-" * 55)

    # Comparación del dígito ingresado vs el calculado
    es_valido = (digito_ingresado == digito_esperado)

    if es_valido:
        print("  RESULTADO: VALIDO")
        print("     El dígito verificador coincide con el calculado.")
        print("     El checksum no detectó alteraciones.")
    else:
        print("  RESULTADO: INVALIDO")
        print(f"     Se ingreso '{digito_ingresado}', pero el correcto es '{digito_esperado}'.")
        print("     El checksum detectó un error en la cadena.")

    print("=" * 55)
    return es_valido


def main():
    continuar = True
    while continuar:
        # Item b): Solicitar el CUIT al usuario
        cuit = solicitar_cuit()

        # Items c) y d): Validar e informar
        validar_cuit(cuit)

        # Preguntar si se desea validar otro
        respuesta = input("\n¿Desea validar otro CUIT/CUIL? (s/n): ").strip().lower()
        continuar = (respuesta == "s")

    print("\nFin del programa..")


if __name__ == "__main__":
    main()
