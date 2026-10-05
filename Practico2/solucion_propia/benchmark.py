import os
import time
import subprocess
import math

# Rutas de ejecutables
PEA_EXE = r"C:\Program Files\PeaZip\pea.exe"
GZIP_EXE = r"C:\Program Files\Git\usr\bin\gzip.exe"
COMPRESSOR_PY = "compressor.py"

# Archivos de prueba
PRUEBAS_DIR = "pruebas"
ARCHIVOS = [
    "prueba_1_pequena.txt",
    "prueba_2_texto_natural.txt",
    "prueba_3_alta_repeticion.txt",
    "prueba_4_baja_repeticion.txt"
]

def format_time(ms):
    return f"{ms:.2f} ms"

def print_separator():
    print("-" * 80)

def main():
    print("Iniciando Benchmark de Compresores...")
    print_separator()

    for archivo in ARCHIVOS:
        ruta_original = os.path.join(PRUEBAS_DIR, archivo)
        if not os.path.exists(ruta_original):
            print(f"No se encontr: {ruta_original}")
            continue

        tamano_orig = os.path.getsize(ruta_original)
        print(f"Archivo: {archivo} (Tamano Original: {tamano_orig} bytes)")
        print_separator()

        # ----------------------------------------------------
        # 1. GZIP -6 (Baseline)
        # ----------------------------------------------------
        ruta_gz = ruta_original + ".gz"
        if os.path.exists(ruta_gz):
            os.remove(ruta_gz)
            
        t0 = time.perf_counter()
        subprocess.run([GZIP_EXE, "-k", "-6", ruta_original], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        
        tiempo_gzip_ms = (t1 - t0) * 1000
        tamano_gz = os.path.getsize(ruta_gz)
        ratio_gzip = tamano_orig / tamano_gz if tamano_gz > 0 else 1
        
        # ----------------------------------------------------
        # 2. TDI (Algoritmo Propio)
        # ----------------------------------------------------
        ruta_tdi = os.path.splitext(ruta_original)[0] + ".tdi"
        if os.path.exists(ruta_tdi):
            os.remove(ruta_tdi)
            
        t0 = time.perf_counter()
        subprocess.run(["python", COMPRESSOR_PY, ruta_original, ruta_tdi], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        
        tiempo_tdi_ms = (t1 - t0) * 1000
        tamano_tdi = os.path.getsize(ruta_tdi)
        ratio_tdi = tamano_orig / tamano_tdi if tamano_tdi > 0 else 1
        
        # Weissman Score TDI
        # W = 1 * (R / Rref) * [ log(Tref) / log(T) ]
        if tiempo_tdi_ms > 1 and tiempo_gzip_ms > 1:
            weissman_tdi = (ratio_tdi / ratio_gzip) * (math.log(tiempo_gzip_ms) / math.log(tiempo_tdi_ms))
        else:
            weissman_tdi = float('inf')

        # ----------------------------------------------------
        # 3. PeaZip (PEA PCOMPRESS2)
        # ----------------------------------------------------
        nombre_sin_ext = os.path.splitext(archivo)[0]
        ruta_pea_out = os.path.abspath(os.path.join(PRUEBAS_DIR, nombre_sin_ext))
        ruta_pea_final = ruta_pea_out + ".pea"
        if os.path.exists(ruta_pea_final):
            os.remove(ruta_pea_final)
            
        ruta_original_abs = os.path.abspath(ruta_original)
        
        # Comando: pea.exe PEA <output_sin_ext> 0 PCOMPRESS2 SHA256 SHA256 RIPEMD160 BATCH FROMCL <input>
        cmd_pea = [
            PEA_EXE, "PEA", ruta_pea_out, "0", "PCOMPRESS2", 
            "SHA256", "SHA256", "RIPEMD160", "BATCH", "FROMCL", ruta_original_abs
        ]
        
        t0 = time.perf_counter()
        subprocess.run(cmd_pea, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        
        tiempo_pea_ms = (t1 - t0) * 1000
        tamano_pea = os.path.getsize(ruta_pea_final) if os.path.exists(ruta_pea_final) else 0
        ratio_pea = tamano_orig / tamano_pea if tamano_pea > 0 else 1

        # Weissman Score PeaZip
        if tiempo_pea_ms > 1 and tiempo_gzip_ms > 1:
            weissman_pea = (ratio_pea / ratio_gzip) * (math.log(tiempo_gzip_ms) / math.log(tiempo_pea_ms))
        else:
            weissman_pea = float('inf')

        # Mostrar Resultados
        print(f"{'Compresor':<15} | {'Tamano (B)':<10} | {'Ratio':<10} | {'Ahorro %':<10} | {'Tiempo (ms)':<15} | {'Weissman':<10}")
        print("-" * 80)
        
        def print_stats(nombre, tamano, ratio, tiempo_ms, weissman):
            ahorro = (1 - (1/ratio))*100 if ratio > 0 else 0
            w_str = f"{weissman:.4f}" if isinstance(weissman, float) and weissman != float('inf') else "-"
            print(f"{nombre:<15} | {tamano:<10} | {ratio:<10.2f} | {ahorro:<10.2f} | {tiempo_ms:<15.2f} | {w_str:<10}")

        print_stats("GZIP (Base)", tamano_gz, ratio_gzip, tiempo_gzip_ms, "-")
        print_stats("TDI (Propio)", tamano_tdi, ratio_tdi, tiempo_tdi_ms, weissman_tdi)
        print_stats("PeaZip (PCOMP)", tamano_pea, ratio_pea, tiempo_pea_ms, weissman_pea)
        print_separator()
        print("\n")

if __name__ == "__main__":
    main()
