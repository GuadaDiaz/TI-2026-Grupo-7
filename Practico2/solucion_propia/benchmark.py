import os
import sys
import time
import hashlib
import subprocess
import math
import pickle
import statistics
import csv
import gzip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSOR_PY = os.path.join(BASE_DIR, "compressor.py")
DECOMPRESSOR_PY = os.path.join(BASE_DIR, "decompressor.py")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

ARCHIVOS = [
    "prueba_1_pequena.txt",
    "prueba_2_texto_natural.txt",
    "prueba_3_alta_repeticion.txt",
    "prueba_4_baja_repeticion.txt"
]

# =======================================================================
# COMPLETAR A MANO LUEGO DE USAR PEAZIP EN LA INTERFAZ GRÁFICA
# =======================================================================
PEAZIP_MANUAL_DATA = {
    "prueba_1_pequena.txt": {"tam_comp_bytes": 346, "t_comp_ms": 25},
    "prueba_2_texto_natural.txt": {"tam_comp_bytes": 2218, "t_comp_ms": 32},
    "prueba_3_alta_repeticion.txt": {"tam_comp_bytes": 972, "t_comp_ms": 28},
    "prueba_4_baja_repeticion.txt": {"tam_comp_bytes": 85527, "t_comp_ms": 29},
}

def format_time(ms):
    if ms < 1000: return f"{ms:.2f} ms"
    return f"{ms/1000:.3f} s"

def calcular_hash_sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def benchmark_tdi(ruta_orig):
    tam_orig = os.path.getsize(ruta_orig)
    ruta_tdi = os.path.join(BASE_DIR, "temp_bench.tdi")
    ruta_rec = os.path.join(BASE_DIR, "temp_bench_rec.txt")
    
    t0 = time.perf_counter()
    p_comp = subprocess.run([sys.executable, COMPRESSOR_PY, ruta_orig, ruta_tdi], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    t1 = time.perf_counter()
    t_comp_ms = (t1 - t0) * 1000
    
    tam_tdi = os.path.getsize(ruta_tdi) if os.path.exists(ruta_tdi) else 0
    
    try:
        with open(ruta_tdi, 'rb') as f_in:
            pickle.load(f_in)
            tam_cabecera_H = f_in.tell()
    except:
        tam_cabecera_H = 0

    t0 = time.perf_counter()
    p_decomp = subprocess.run([sys.executable, DECOMPRESSOR_PY, ruta_tdi, ruta_rec], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    t1 = time.perf_counter()
    t_decomp_ms = (t1 - t0) * 1000
    
    integ_ok = False
    if os.path.exists(ruta_rec):
        integ_ok = (calcular_hash_sha256(ruta_rec) == calcular_hash_sha256(ruta_orig))

    for p in (ruta_tdi, ruta_rec):
        if os.path.exists(p): os.remove(p)

    return {"tam_comp": tam_tdi, "tam_H": tam_cabecera_H, "t_comp_ms": t_comp_ms, "t_decomp_ms": t_decomp_ms, "integ_ok": integ_ok}

def benchmark_gzip(ruta_orig):
    ruta_gz = os.path.join(BASE_DIR, "temp_bench.gz")
    t0 = time.perf_counter()
    with open(ruta_orig, 'rb') as f_in, open(ruta_gz, 'wb') as f_out:
        f_out.write(gzip.compress(f_in.read(), compresslevel=6))
    t1 = time.perf_counter()
    
    t_comp_ms = (t1 - t0) * 1000
    tam_gz = os.path.getsize(ruta_gz) if os.path.exists(ruta_gz) else 0
    
    if os.path.exists(ruta_gz): os.remove(ruta_gz)
    return {"tam_comp": tam_gz, "t_comp_ms": t_comp_ms}

def calcular_weissman(r, r_ref, t_ms, t_ref_ms):
    t_ms = max(10.0, t_ms)
    t_ref_ms = max(10.0, t_ref_ms)
    if r <= 0 or r_ref <= 0: return 0.0
    return 1.0 * (r / r_ref) * (math.log(t_ref_ms) / math.log(t_ms))

def exportar_csv_detallado(datos):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "benchmark_resultados_detallados.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Encabezados con TODAS las métricas de la cátedra
        writer.writerow([
            "Archivo", "Algoritmo", "S_orig (B)", "S_comp (B)", "Cabecera H (B)", 
            "Ratio", "Ahorro %", "Relativo %", "Vc (MB/s)", "Vd (MB/s)", 
            "T_Comp (ms)", "T_Decomp (ms)", "Weissman", "Integridad"
        ])
        
        for arch, d in datos.items():
            # TDI
            integ_str = "OK" if d['TDI']['integ'] else "FAIL"
            writer.writerow([
                arch, "Python TDI", d['tam_orig'], d['TDI']['tam'], d['TDI']['H'],
                round(d['TDI']['r'], 4), round(d['TDI']['ahorro'], 2), round(d['TDI']['relativo'], 2),
                round(d['TDI']['vc'], 4), round(d['TDI']['vd'], 4),
                round(d['TDI']['t'], 2), round(d['TDI']['t_d'], 2), round(d['TDI']['w'], 4), integ_str
            ])
            # GZIP
            writer.writerow([
                arch, "GZIP", d['tam_orig'], d['GZIP']['tam'], 10,
                round(d['GZIP']['r'], 4), round(d['GZIP']['ahorro'], 2), round(d['GZIP']['relativo'], 2),
                round(d['GZIP']['vc'], 4), "-", round(d['GZIP']['t'], 2), "-", 1.0000, "OK"
            ])
            # PeaZip
            if d['PEA']['tam'] > 0:
                writer.writerow([
                    arch, "PeaZip", d['tam_orig'], d['PEA']['tam'], "-",
                    round(d['PEA']['r'], 4), round(d['PEA']['ahorro'], 2), round(d['PEA']['relativo'], 2),
                    round(d['PEA']['vc'], 4), "-", round(d['PEA']['t'], 2), "-", round(d['PEA']['w'], 4), "OK (GUI)"
                ])

def main():
    print("Ejecutando mediciones detalladas...")
    datos = {}
    NUM_RUNS = 3

    for archivo in ARCHIVOS:
        ruta_orig = os.path.join(TESTS_DIR, archivo)
        if not os.path.exists(ruta_orig): continue

        tam_orig = os.path.getsize(ruta_orig)
        runs_tdi, runs_gz = [], []

        for _ in range(NUM_RUNS):
            runs_tdi.append(benchmark_tdi(ruta_orig))
            runs_gz.append(benchmark_gzip(ruta_orig))

        # TDI metrics
        t_comp_tdi = statistics.median([r["t_comp_ms"] for r in runs_tdi])
        t_decomp_tdi = statistics.median([r["t_decomp_ms"] for r in runs_tdi])
        tam_tdi = runs_tdi[0]["tam_comp"]
        tam_H = runs_tdi[0]["tam_H"]
        integ_ok = runs_tdi[0]["integ_ok"]
        r_tdi = tam_orig / tam_tdi if tam_tdi > 0 else 0
        ahorro_tdi = (1.0 - (tam_tdi / tam_orig)) * 100 if tam_orig > 0 else 0
        rel_tdi = (tam_tdi / tam_orig) * 100 if tam_orig > 0 else 0
        vc_tdi = (tam_orig / 1000000.0) / (t_comp_tdi / 1000.0) if t_comp_tdi > 0 else 0
        vd_tdi = (tam_orig / 1000000.0) / (t_decomp_tdi / 1000.0) if t_decomp_tdi > 0 else 0

        # GZIP metrics
        t_comp_gz = statistics.median([r["t_comp_ms"] for r in runs_gz])
        tam_gz = runs_gz[0]["tam_comp"]
        r_gz = tam_orig / tam_gz if tam_gz > 0 else 0
        ahorro_gz = (1.0 - (tam_gz / tam_orig)) * 100 if tam_orig > 0 else 0
        rel_gz = (tam_gz / tam_orig) * 100 if tam_orig > 0 else 0
        vc_gz = (tam_orig / 1000000.0) / (t_comp_gz / 1000.0) if t_comp_gz > 0 else 0

        w_score_tdi = calcular_weissman(r_tdi, r_gz, t_comp_tdi, t_comp_gz)

        # PeaZip metrics
        pea_tam = PEAZIP_MANUAL_DATA[archivo]["tam_comp_bytes"]
        pea_t = PEAZIP_MANUAL_DATA[archivo]["t_comp_ms"]
        r_pea = tam_orig / pea_tam if pea_tam > 0 else 0
        ahorro_pea = (1.0 - (pea_tam / tam_orig)) * 100 if tam_orig > 0 else 0
        rel_pea = (pea_tam / tam_orig) * 100 if tam_orig > 0 else 0
        vc_pea = (tam_orig / 1000000.0) / (pea_t / 1000.0) if pea_t > 0 else 0
        w_score_pea = calcular_weissman(r_pea, r_gz, pea_t, t_comp_gz) if pea_tam > 0 else 0

        datos[archivo] = {
            "tam_orig": tam_orig,
            "TDI": {"tam": tam_tdi, "H": tam_H, "r": r_tdi, "t": t_comp_tdi, "t_d": t_decomp_tdi, "w": w_score_tdi, "integ": integ_ok, "ahorro": ahorro_tdi, "relativo": rel_tdi, "vc": vc_tdi, "vd": vd_tdi},
            "GZIP": {"tam": tam_gz, "r": r_gz, "t": t_comp_gz, "ahorro": ahorro_gz, "relativo": rel_gz, "vc": vc_gz},
            "PEA": {"tam": pea_tam, "r": r_pea, "t": pea_t, "w": w_score_pea, "ahorro": ahorro_pea, "relativo": rel_pea, "vc": vc_pea}
        }

    # Imprimir mini resumen en consola
    print(f"\n{'Archivo':<28} | {'Algoritmo':<15} | {'Integridad':<10} | {'Weissman':<8}")
    print("-" * 70)
    for arch, d in datos.items():
        print(f"{arch:<28} | {'Python TDI':<15} | {'OK' if d['TDI']['integ'] else 'FAIL':<10} | {d['TDI']['w']:.4f}")
        print(f"{'':<28} | {'GZIP (Baseline)':<15} | {'OK':<10} | 1.0000")
        if d['PEA']['r'] > 0:
            print(f"{'':<28} | {'PeaZip':<15} | {'OK (GUI)':<10} | {d['PEA']['w']:.4f}")
        print("-" * 70)
        
    exportar_csv_detallado(datos)
    print(f"\n¡Resultados listos! Las métricas detalladas (Throughput, Cabeceras, Ahorro, etc.)")
    print(f"fueron exportadas al archivo 'benchmark_resultados_detallados.csv' en la carpeta '{RESULTS_DIR}'.")

if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    main()
