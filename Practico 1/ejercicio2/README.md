# Ejercicio 2 — Entropía de imágenes (BMP vs. JPG)

Compara la entropía de una imagen sin comprimir (BMP) contra su versión comprimida (JPG), analiza la cabecera BMP y grafica los histogramas de bytes.

## Dependencias

Para la ejecución de este ejercicio es necesario instalar las siguientes dependencias externas:

- `matplotlib`, `pillow`

Todas están incluidas en el [`requirements.txt`](../requirements.txt) de la raíz
del repositorio. Para instalarlas:

```bash
pip install -r ../requirements.txt
```

## Ejecución

El script principal debe ejecutarse estando ubicado dentro de la carpeta `ejercicio2`.

```bash
cd ejercicio2
python main.py
```

El programa utilizará los archivos `imagenes/blackbuck.bmp` e `imagenes/blackbuck.jpg` ya incluidos.

**(Opcional)** Si deseas regenerar el JPG a partir del BMP:
```bash
python convetidor.py
```
