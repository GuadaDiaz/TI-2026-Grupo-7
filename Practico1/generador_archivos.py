import os
import zipfile
import urllib.request

def build_exact_size_datasets():
    print("Fetching raw data from Project Gutenberg...")
    url = "https://www.gutenberg.org/files/2000/2000-0.txt"
    raw_text = urllib.request.urlopen(url).read()

    zip_filename = 'archivo_comprimido.zip'
    txt_filename = 'texto_puro.txt'

    # 1. Comprimir el texto original completo
    temp_filename = 'temp_raw.txt'
    with open(temp_filename, 'wb') as f:
        f.write(raw_text)
        
    with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(temp_filename, arcname='data.txt')
    
    os.remove(temp_filename)
    
    # 2. Capturar el tamaño exacto del ZIP generado
    target_size = os.path.getsize(zip_filename)
    
    # 3. Truncar el texto puro al tamaño exacto del ZIP
    with open(txt_filename, 'wb') as f:
        f.write(raw_text[:target_size])
        
    print(f"[+] ZIP exact size: {target_size} bytes")
    print(f"[+] TXT exact size: {os.path.getsize(txt_filename)} bytes")
    print("Both files are now perfectly matched for IC comparison.")

if __name__ == "__main__":
    build_exact_size_datasets()