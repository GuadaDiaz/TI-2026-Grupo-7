from PIL import Image
from pathlib import Path

def convertir(direccion: str):
    ruta = Path(direccion)
    
    if ruta.suffix.lower() != '.bmp':
        print("Error: El archivo de entrada debe tener extensión .bmp")
        return
    
    try:
        imagen = Image.open(ruta)
        imagen_rgb = imagen.convert('RGB') 
        
        carpeta_destino = Path('imagenes')
        carpeta_destino.mkdir(exist_ok=True)
        nombre = ruta.stem
        ruta_salida = carpeta_destino / f"{nombre}.jpg"
        
        imagen_rgb.save(ruta_salida, 'JPEG')
        print(f"Éxito: Imagen convertida y guardada en {ruta_salida}")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo original en la ruta '{direccion}'")
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar la imagen: {e}")

ruta_completa = r"./imagenes/blackbuck.bmp"

convertir(ruta_completa)