# Ejercicio 5 — Almacenamiento en texto vs. binario

Genera datos simulados (nombre, dirección, DNI, flags) y los guarda tanto en JSON (texto, longitud variable) como en binario empaquetado con `struct` (longitud fija), comparando el tamaño resultante de cada formato.

## Dependencias

Este ejercicio no requiere librerías externas. Utiliza únicamente la librería estándar de Python.

## Ejecución

El script debe ejecutarse estando ubicado dentro de la carpeta `ejercicio5`.

```bash
cd ejercicio5
python main.py
```

En cada ejecución, el programa sobrescribirá los archivos `datos.json` y `datos.bin` con una nueva tanda de datos generados aleatoriamente y mostrará la comparación en consola.
