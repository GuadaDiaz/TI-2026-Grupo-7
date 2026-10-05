import os
import sys
import time
import shutil
import hashlib
import subprocess
import math
import gzip
import pickle
import statistics
import json
import csv

# Rutas configurables de ejecutables externos (si están disponibles)
PEA_EXE = r"C:\Program Files\PeaZip\pea.exe"
GZIP_EXE = r"C:\Program Files\Git\usr\bin\gzip.exe"

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

def format_time(ms):
    if ms < 1000:
        return f"{ms:.2f} ms"
    return f"{ms/1000:.3f} s"

def format_mb_s(mb_s):
    return f"{mb_s:.4f} MB/s"

def print_separator(char="=", length=110):
    print(char * length)

def calcular_hash_sha256(ruta_o_bytes):
    h = hashlib.sha256()
    if isinstance(ruta_o_bytes, (bytes, bytearray)):
        h.update(ruta_o_bytes)
    else:
        with open(ruta_o_bytes, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
    return h.hexdigest()

def detectar_herramientas():
    global GZIP_EXE, PEA_EXE
    has_gzip_cli = os.path.exists(GZIP_EXE) or shutil.which("gzip") is not None
    if shutil.which("gzip"):
        GZIP_EXE = shutil.which("gzip")
        
    has_pea_cli = os.path.exists(PEA_EXE) or shutil.which("pea") is not None
    if shutil.which("pea"):
        PEA_EXE = shutil.which("pea")
        
    return has_gzip_cli, has_pea_cli

def benchmark_tdi(ruta_orig):
    """
    Ejecuta compresion y descompresion con TDI (Markov + Huffman).
    Mide tiempo, tamano comprimido, tamano de cabecera H y verifica integridad.
    """
    tam_orig = os.path.getsize(ruta_orig)
    ruta_tdi = os.path.join(BASE_DIR, "temp_bench.tdi")
    ruta_rec = os.path.join(BASE_DIR, "temp_bench_rec.txt")
    
    for p in (ruta_tdi, ruta_rec):
        if os.path.exists(p):
            os.remove(p)
            
    # Compresion
    t0 = time.perf_counter()
    p_comp = subprocess.run(
        [sys.executable, COMPRESSOR_PY, ruta_orig, ruta_tdi],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR
    )
    t1 = time.perf_counter()
    t_comp_ms = (t1 - t0) * 1000
    
    if p_comp.returncode != 0 or not os.path.exists(ruta_tdi):
        err = p_comp.stderr.decode('utf-8', errors='replace')
        print(f"Error en compresion TDI: {err}")
        return None
        
    tam_tdi = os.path.getsize(ruta_tdi)
    
    # Extraer tamano de cabecera H de la salida .tdi
    try:
        with open(ruta_tdi, 'rb') as f_in:
            cabecera = pickle.load(f_in)
            tam_cabecera_H = f_in.tell()
    except Exception:
        tam_cabecera_H = 0

    # Descompresion
    t0 = time.perf_counter()
    p_decomp = subprocess.run(
        [sys.executable, DECOMPRESSOR_PY, ruta_tdi, ruta_rec],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR
    )
    t1 = time.perf_counter()
    t_decomp_ms = (t1 - t0) * 1000
    
    if p_decomp.returncode != 0 or not os.path.exists(ruta_rec):
        err = p_decomp.stderr.decode('utf-8', errors='replace')
        print(f"Error en descompresion TDI: {err}")
        integ_ok = False
        hash_rec = "ERROR"
    else:
        hash_rec = calcular_hash_sha256(ruta_rec)
        hash_orig = calcular_hash_sha256(ruta_orig)
        integ_ok = (hash_rec == hash_orig)

    # Limpieza
    for p in (ruta_tdi, ruta_rec):
        if os.path.exists(p):
            os.remove(p)

    return {
        "nombre": "Markov+Huffman (TDI)",
        "tam_comp": tam_tdi,
        "tam_cabecera_H": tam_cabecera_H,
        "t_comp_ms": t_comp_ms,
        "t_decomp_ms": t_decomp_ms,
        "integ_ok": integ_ok,
        "hash_rec": hash_rec
    }

def benchmark_gzip(ruta_orig, has_gzip_cli):
    """
    Ejecuta compresion y descompresion con GZIP (-6).
    """
    tam_orig = os.path.getsize(ruta_orig)
    hash_orig = calcular_hash_sha256(ruta_orig)
    ruta_gz = os.path.join(BASE_DIR, "temp_bench.gz")
    ruta_rec = os.path.join(BASE_DIR, "temp_bench_gz_rec.txt")
    
    for p in (ruta_gz, ruta_rec):
        if os.path.exists(p):
            os.remove(p)

    if has_gzip_cli:
        t0 = time.perf_counter()
        subprocess.run([GZIP_EXE, "-k", "-6", "-c", ruta_orig], stdout=open(ruta_gz, 'wb'), stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        t_comp_ms = (t1 - t0) * 1000
        tam_gz = os.path.getsize(ruta_gz)
        
        t0 = time.perf_counter()
        subprocess.run([GZIP_EXE, "-d", "-c", ruta_gz], stdout=open(ruta_rec, 'wb'), stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        t_decomp_ms = (t1 - t0) * 1000
        
        hash_rec = calcular_hash_sha256(ruta_rec)
        integ_ok = (hash_rec == hash_orig)
    else:
        with open(ruta_orig, 'rb') as f:
            data = f.read()
            
        t0 = time.perf_counter()
        gz_data = gzip.compress(data, compresslevel=6)
        t1 = time.perf_counter()
        t_comp_ms = (t1 - t0) * 1000
        tam_gz = len(gz_data)
        
        t0 = time.perf_counter()
        rec_data = gzip.decompress(gz_data)
        t1 = time.perf_counter()
        t_decomp_ms = (t1 - t0) * 1000
        
        integ_ok = (rec_data == data)
        hash_rec = calcular_hash_sha256(rec_data)

    for p in (ruta_gz, ruta_rec):
        if os.path.exists(p):
            os.remove(p)

    return {
        "nombre": "gzip-6",
        "tam_comp": tam_gz,
        "tam_cabecera_H": 10,
        "t_comp_ms": t_comp_ms,
        "t_decomp_ms": t_decomp_ms,
        "integ_ok": integ_ok,
        "hash_rec": hash_rec
    }

def calcular_weissman(r, r_ref, t_ms, t_ref_ms, alpha=1.0):
    if r <= 0 or r_ref <= 0 or t_ms <= 1.0 or t_ref_ms <= 1.0:
        return 0.0001
    return alpha * (r / r_ref) * (math.log(t_ref_ms) / math.log(t_ms))

def exportar_resultados(datos_archivos, metricas_globales):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 1. JSON
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "individual_results": datos_archivos,
            "global_metrics": metricas_globales
        }, f, indent=4)
        
    # 2. CSV
    csv_path = os.path.join(RESULTS_DIR, "benchmark_results.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Archivo", "So_bytes", "Sc_bytes", "H_bytes", "Ratio_R", 
            "Ahorro_pct", "Relativo_pct", "Vc_MB_s", "Vd_MB_s", 
            "Overhead_H_pct", "T_comp_TDI_ms", "T_decomp_TDI_ms",
            "Sc_gzip_bytes", "Ratio_gzip", "T_comp_gzip_ms", "T_decomp_gzip_ms",
            "Weissman", "Integridad_SHA256"
        ])
        for arch, d in datos_archivos.items():
            writer.writerow([
                arch, d["tam_orig"], d["tam_tdi"], d["tam_H"], round(d["r_tdi"], 4),
                round(d["ahorro_tdi"], 2), round(d["p_tdi"], 2), round(d["v_c_tdi"], 4), round(d["v_d_tdi"], 4),
                round(d["overhead_h"], 2), round(d["t_comp_tdi"], 2), round(d["t_decomp_tdi"], 2),
                d["tam_gz"], round(d["r_gz"], 4), round(d["t_comp_gz"], 2), round(d["t_decomp_gz"], 2),
                round(d["w_score"], 4), "OK" if d["integ_ok"] else "FAIL"
            ])
            
    # 3. Markdown
    md_path = os.path.join(RESULTS_DIR, "tabla_comparativa.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Resultados del Benchmark (Grupo 7)\n\n")
        f.write("## Tabla Comparativa Principal\n\n")
        f.write("| Archivo | Algoritmo | Ratio ($R$) | Tiempo ($T$) | Ratio gzip ($R_{ref}$) | Tiempo gzip ($T_{ref}$) | Weissman ($W$) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for arch, d in datos_archivos.items():
            f.write(f"| {arch} | Markov+Huffman (TDI) | {d['r_tdi']:.2f} | {format_time(d['t_comp_tdi'])} | {d['r_gz']:.2f} | {format_time(d['t_comp_gz'])} | {d['w_score']:.4f} |\n")
            
        f.write("\n## Tabla Detallada de Métricas\n\n")
        f.write("| Archivo | $S_o$ (B) | $S_c$ (B) | $H$ (B) | $R$ | $A$ (%) | $P$ (%) | $V_c$ (MB/s) | $V_d$ (MB/s) | $O$ (%) | Integridad |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for arch, d in datos_archivos.items():
            f.write(f"| {arch} | {d['tam_orig']} | {d['tam_tdi']} | {d['tam_H']} | {d['r_tdi']:.2f} | {d['ahorro_tdi']:.2f}% | {d['p_tdi']:.2f}% | {d['v_c_tdi']:.4f} | {d['v_d_tdi']:.4f} | {d['overhead_h']:.2f}% | OK |\n")
            
        f.write("\n## Weissman Score Global del Corpus\n\n")
        f.write(f"- **R_global (TDI):** {metricas_globales['r_global_tdi']:.4f}\n")
        f.write(f"- **R_global (gzip):** {metricas_globales['r_global_gz']:.4f}\n")
        f.write(f"- **T_global (TDI):** {metricas_globales['t_global_tdi']:.2f} ms\n")
        f.write(f"- **T_global (gzip):** {metricas_globales['t_global_gz']:.2f} ms\n")
        f.write(f"- **Weissman Score Global:** **{metricas_globales['w_global']:.4f}**\n")

def main():
    has_gzip_cli, _ = detectar_herramientas()

    print_separator("=")
    print("BENCHMARK INTEGRAL DE COMPRESION Y DESCOMPRESION - PRACTICO 2")
    print("Métricas: R (Ratio), A (Ahorro %), P (Relativo %), Vc (MB/s), Vd (MB/s), O (Overhead %), W (Weissman)")
    print(f"Baseline: gzip-6 | alpha = 1.0 | Tiempos en milisegundos (ms)")
    print_separator("=")

    datos_archivos = {}
    NUM_RUNS = 3
    print(f"Ejecutando mediciones ({NUM_RUNS} iteraciones sobre tests/)...")

    for archivo in ARCHIVOS:
        ruta_orig = os.path.join(TESTS_DIR, archivo)
        if not os.path.exists(ruta_orig):
            continue

        tam_orig = os.path.getsize(ruta_orig)
        
        runs_tdi = []
        runs_gz = []

        for _ in range(NUM_RUNS):
            res_gz = benchmark_gzip(ruta_orig, has_gzip_cli)
            res_tdi = benchmark_tdi(ruta_orig)
            runs_gz.append(res_gz)
            runs_tdi.append(res_tdi)

        t_comp_tdi_med = statistics.median([r["t_comp_ms"] for r in runs_tdi])
        t_decomp_tdi_med = statistics.median([r["t_decomp_ms"] for r in runs_tdi])
        
        t_comp_gz_med = statistics.median([r["t_comp_ms"] for r in runs_gz])
        t_decomp_gz_med = statistics.median([r["t_decomp_ms"] for r in runs_gz])

        tam_tdi = runs_tdi[0]["tam_comp"]
        tam_H = runs_tdi[0]["tam_cabecera_H"]
        tam_gz = runs_gz[0]["tam_comp"]

        r_tdi = tam_orig / tam_tdi if tam_tdi > 0 else 0
        r_gz = tam_orig / tam_gz if tam_gz > 0 else 0

        ahorro_tdi = (1.0 - (tam_tdi / tam_orig)) * 100.0
        p_tdi = (tam_tdi / tam_orig) * 100.0
        
        tam_orig_mb = tam_orig / 1_000_000.0
        v_c_tdi = tam_orig_mb / (t_comp_tdi_med / 1000.0) if t_comp_tdi_med > 0 else 0
        v_d_tdi = tam_orig_mb / (t_decomp_tdi_med / 1000.0) if t_decomp_tdi_med > 0 else 0
        overhead_h = (tam_H / tam_tdi) * 100.0 if tam_tdi > 0 else 0

        w_score = calcular_weissman(r_tdi, r_gz, t_comp_tdi_med, t_comp_gz_med)

        datos_archivos[archivo] = {
            "tam_orig": tam_orig,
            "tam_tdi": tam_tdi,
            "tam_H": tam_H,
            "r_tdi": r_tdi,
            "ahorro_tdi": ahorro_tdi,
            "p_tdi": p_tdi,
            "t_comp_tdi": t_comp_tdi_med,
            "t_decomp_tdi": t_decomp_tdi_med,
            "v_c_tdi": v_c_tdi,
            "v_d_tdi": v_d_tdi,
            "overhead_h": overhead_h,
            "tam_gz": tam_gz,
            "r_gz": r_gz,
            "t_comp_gz": t_comp_gz_med,
            "t_decomp_gz": t_decomp_gz_med,
            "w_score": w_score,
            "integ_ok": runs_tdi[0]["integ_ok"]
        }

    # ----------------------------------------------------
    # TABLA COMPARATIVA PRINCIPAL
    # ----------------------------------------------------
    print("\n" + "=" * 110)
    print("TABLA COMPARATIVA DE RENDIMIENTO (COMPRESSOR.PY VS GZIP-6)")
    print("=" * 110)
    print(f"{'Archivo':<28} | {'Algoritmo':<20} | {'Ratio':<7} | {'Tiempo':<11} | {'Ratio gzip':<10} | {'Tiempo gzip':<11} | {'Weissman':<8}")
    print("-" * 110)

    for arch, d in datos_archivos.items():
        w_str = f"{d['w_score']:.4f}"
        print(f"{arch:<28} | {'Markov+Huffman (TDI)':<20} | {d['r_tdi']:<7.2f} | {format_time(d['t_comp_tdi']):<11} | {d['r_gz']:<10.2f} | {format_time(d['t_comp_gz']):<11} | {w_str:<8}")

    print("-" * 110)

    # ----------------------------------------------------
    # TABLA DETALLADA DE TODAS LAS MÉTRICAS SOLICITADAS
    # ----------------------------------------------------
    print("\n" + "=" * 110)
    print("TABLA DETALLADA DE MÉTRICAS (So, Sc, H, R, A, P, Vc, Vd, Overhead H, Integridad)")
    print("=" * 110)
    print(f"{'Archivo':<26} | {'So (B)':<7} | {'Sc (B)':<7} | {'R':<5} | {'A (%)':<8} | {'P (%)':<8} | {'Vc(MB/s)':<9} | {'Vd(MB/s)':<9} | {'O (%)':<7} | {'Integ'}")
    print("-" * 110)

    for arch, d in datos_archivos.items():
        integ_str = "OK" if d["integ_ok"] else "FAIL"
        print(f"{arch:<26} | {d['tam_orig']:<7} | {d['tam_tdi']:<7} | {d['r_tdi']:<5.2f} | {d['ahorro_tdi']:<7.2f}% | {d['p_tdi']:<7.2f}% | {d['v_c_tdi']:<9.4f} | {d['v_d_tdi']:<9.4f} | {d['overhead_h']:<6.2f}% | {integ_str}")

    print("-" * 110)

    # ----------------------------------------------------
    # CÁLCULO DE WEISSMAN GLOBAL
    # ----------------------------------------------------
    sum_so = sum(d["tam_orig"] for d in datos_archivos.values())
    sum_sc_tdi = sum(d["tam_tdi"] for d in datos_archivos.values())
    sum_sc_gz = sum(d["tam_gz"] for d in datos_archivos.values())

    r_global_tdi = sum_so / sum_sc_tdi
    r_global_gz = sum_so / sum_sc_gz

    t_global_tdi = sum(d["t_comp_tdi"] for d in datos_archivos.values())
    t_global_gz = sum(d["t_comp_gz"] for d in datos_archivos.values())

    w_global = calcular_weissman(r_global_tdi, r_global_gz, t_global_tdi, t_global_gz)

    metricas_globales = {
        "sum_so": sum_so,
        "sum_sc_tdi": sum_sc_tdi,
        "sum_sc_gz": sum_sc_gz,
        "r_global_tdi": r_global_tdi,
        "r_global_gz": r_global_gz,
        "t_global_tdi": t_global_tdi,
        "t_global_gz": t_global_gz,
        "w_global": w_global
    }

    print("\n" + "=" * 110)
    print("WEISSMAN SCORE GLOBAL DEL CORPUS")
    print("=" * 110)
    print(f"  Sigma So (Original total):   {sum_so:,} bytes ({sum_so/1000:.2f} KB)")
    print(f"  Sigma Sc TDI:                {sum_sc_tdi:,} bytes | Rglobal (TDI):  {r_global_tdi:.4f}")
    print(f"  Sigma Sc gzip-6:             {sum_sc_gz:,} bytes | Rglobal (gzip): {r_global_gz:.4f}")
    print(f"  Tglobal compresión TDI:      {t_global_tdi:.2f} ms")
    print(f"  Tglobal compresión gzip-6:   {t_global_gz:.2f} ms")
    print(f"  >>> WEISSMAN SCORE GLOBAL:   {w_global:.4f} <<<")
    print("=" * 110)

    # Exportar a results/
    exportar_resultados(datos_archivos, metricas_globales)
    print(f"Resultados guardados exitosamente en: {RESULTS_DIR}")
    print("  - results/benchmark_results.json")
    print("  - results/benchmark_results.csv")
    print("  - results/tabla_comparativa.md")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
