# Ejercicio 8 — Capacidad de un canal binario→cuaternario (búsqueda exhaustiva)

Pide la matriz de transición P(Y|X) de un canal 2×4 y busca, probando P(X=0) de 0.00 a 1.00 en pasos de 0.01, la distribución de entrada que maximiza la Información Mutua I(X;Y), es decir la Capacidad del canal.

## Dependencias

Este ejercicio no requiere librerías externas. Utiliza únicamente la librería estándar de Python.

## Ejecución

El programa funciona de manera interactiva y te solicitará ingresar probabilidades. Debe ejecutarse estando ubicado en la carpeta `ejercicio8`.

```bash
cd ejercicio8
python calculo_canal_exhaustiva.py
```

Se te pedirá que ingreses las 8 probabilidades P(Y=j|X=i) por teclado. Ten en cuenta que cada fila ingresada debe sumar 1; si no lo hace, el script volverá a pedir los datos correspondientes a esa fila.
