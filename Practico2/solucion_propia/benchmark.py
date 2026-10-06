import os
import sys
import time
import math
import gzip
import shutil
import hashlib
import functools
import platform
import statistics
import subprocess
from datetime import datetime

from decompressor import leer_cabecera

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSOR_PY = os.path.join(BASE_DIR, "compressor.py")
DECOMPRESSOR_PY = os.path.join(BASE_DIR, "decompressor.py")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
PEA_DIR = os.path.join(TESTS_DIR, "archivos_comprimidos_pea")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

ARCHIVOS = [
    "prueba_1_pequena.txt",
    "prueba_2_texto_natural.txt",
    "prueba_3_alta_repeticion.txt",
    "prueba_4_baja_repeticion.txt"
]
# La prueba 1 sirve para explicar el algoritmo y ver el costo de cabecera:
# según la consigna no se usa para el ranking temporal (Weissman).
ARCHIVOS_RENDIMIENTO = ARCHIVOS[1:]

# Cantidad de corridas por archivo; se informa la mediana de los tiempos
NUM_RUNS = 3

# gzip: metadatos fijos del formato con -n (10 B de cabecera + 8 B de trailer CRC32/tamaño)
H_GZIP = 18

# =======================================================================
# PEAZIP (solución externa): se ejecuta pea.exe, el motor de PeaZip para el formato PEA
# =======================================================================
# Misma configuración que usa la interfaz gráfica de PeaZip para el formato PEA (verificado
# comparando byte a byte las cabeceras de los .pea): compresión PCOMPRESS2 (flujo zlib nivel 6,
# equivalente a Deflate 6), control de volumen SHA3_256, de objeto CRC32 y de stream RIPEMD160,
# sin cifrado. Sintaxis: pea PEA <salida> <tam_volumen> <compresión> <ctrl_volumen> <ctrl_objeto>
# <ctrl_stream> <modo> FROMCL <archivos>
PEAZIP_PARAMETROS = ["0", "PCOMPRESS2", "SHA3_256", "CRC32", "RIPEMD160", "HIDDEN"]

# Copia del último .pea generado por cada prueba (evidencia de la solución externa)
GUARDAR_PEA = True

def buscar_gzip():
    """Busca el ejecutable de gzip (en Windows lo provee Git for Windows)."""
    candidatos = [
        shutil.which("gzip"),
        r"C:\Program Files\Git\usr\bin\gzip.exe",
        r"C:\Program Files (x86)\Git\usr\bin\gzip.exe",
    ]
    for ruta in candidatos:
        if ruta and os.path.isfile(ruta):
            return ruta
    return None

GZIP_EXE = buscar_gzip()

def buscar_peazip():
    """Busca pea.exe, el motor de línea de comandos que se instala junto con PeaZip."""
    candidatos = [
        shutil.which("pea"),
        r"C:\Program Files\PeaZip\pea.exe",
        r"C:\Program Files (x86)\PeaZip\pea.exe",
    ]
    for ruta in candidatos:
        if ruta and os.path.isfile(ruta):
            return ruta
    return None

PEA_EXE = buscar_peazip()

@functools.lru_cache(maxsize=None)
def version_peazip():
    """Versión de PeaZip, leída de los metadatos de peazip.exe (Windows)."""
    exe = os.path.join(os.path.dirname(PEA_EXE), "peazip.exe")
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-Command", f"(Get-Item '{exe}').VersionInfo.ProductVersion"],
                           capture_output=True, text=True, timeout=30)
        return p.stdout.strip() or "desconocida"
    except (OSError, subprocess.SubprocessError):
        return "desconocida"

def format_ms(ms):
    return "-" if ms is None else f"{ms:.2f}"

def format_num(valor, decimales=2, sufijo=""):
    return "-" if valor is None else f"{valor:.{decimales}f}{sufijo}"

def calcular_hash_sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def borrar(*rutas):
    for p in rutas:
        if os.path.exists(p):
            os.remove(p)

def medir_subproceso(cmd, ruta_stdout=None):
    """Ejecuta cmd y devuelve (tiempo_ms, proceso). Si se indica, stdout se guarda en ruta_stdout."""
    if ruta_stdout:
        with open(ruta_stdout, 'wb') as f_out:
            t0 = time.perf_counter()
            p = subprocess.run(cmd, stdout=f_out, stderr=subprocess.PIPE)
            t1 = time.perf_counter()
    else:
        t0 = time.perf_counter()
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        t1 = time.perf_counter()
    return (t1 - t0) * 1000, p

def benchmark_tdi(ruta_orig, sha_orig):
    ruta_tdi = os.path.join(BASE_DIR, "temp_bench.tdi")
    ruta_rec = os.path.join(BASE_DIR, "temp_bench_rec.txt")
    try:
        t_comp_ms, p = medir_subproceso([sys.executable, COMPRESSOR_PY, ruta_orig, ruta_tdi])
        if p.returncode != 0:
            sys.exit(f"compressor.py falló con {os.path.basename(ruta_orig)}: {p.stderr.decode(errors='replace').strip()}")
        tam_tdi = os.path.getsize(ruta_tdi)
        with open(ruta_tdi, 'rb') as f_in:
            _, tam_cabecera_H = leer_cabecera(f_in.read())

        t_decomp_ms, p = medir_subproceso([sys.executable, DECOMPRESSOR_PY, ruta_tdi, ruta_rec])
        sha_rec = calcular_hash_sha256(ruta_rec) if p.returncode == 0 and os.path.exists(ruta_rec) else None

        return {"tam_comp": tam_tdi, "tam_H": tam_cabecera_H, "t_comp_ms": t_comp_ms, "t_decomp_ms": t_decomp_ms,
                "sha_rec": sha_rec, "integ_ok": sha_rec == sha_orig}
    finally:
        borrar(ruta_tdi, ruta_rec)

def benchmark_gzip(ruta_orig, sha_orig):
    """
    Baseline de la cátedra: gzip nivel 6 sin nombre ni timestamp (gzip -n -6).
    Se usa el ejecutable gzip como subproceso, igual que el compresor propio, para medir
    en el mismo entorno. Si no está instalado, se usa el módulo gzip de Python con mtime=0.
    """
    ruta_gz = os.path.join(BASE_DIR, "temp_bench.gz")
    ruta_rec = os.path.join(BASE_DIR, "temp_bench_gz_rec.txt")
    try:
        if GZIP_EXE:
            t_comp_ms, p = medir_subproceso([GZIP_EXE, "-n", "-6", "-c", ruta_orig], ruta_gz)
            if p.returncode != 0:
                sys.exit(f"gzip falló: {p.stderr.decode(errors='replace').strip()}")
            t_decomp_ms, p = medir_subproceso([GZIP_EXE, "-d", "-c", ruta_gz], ruta_rec)
        else:
            t0 = time.perf_counter()
            with open(ruta_orig, 'rb') as f_in, open(ruta_gz, 'wb') as f_out:
                f_out.write(gzip.compress(f_in.read(), compresslevel=6, mtime=0))
            t_comp_ms = (time.perf_counter() - t0) * 1000
            t0 = time.perf_counter()
            with open(ruta_gz, 'rb') as f_in, open(ruta_rec, 'wb') as f_out:
                f_out.write(gzip.decompress(f_in.read()))
            t_decomp_ms = (time.perf_counter() - t0) * 1000

        # Verificación real de integridad: se descomprime y se compara el SHA-256
        sha_rec = calcular_hash_sha256(ruta_rec) if os.path.exists(ruta_rec) else None
        return {"tam_comp": os.path.getsize(ruta_gz), "tam_H": H_GZIP, "t_comp_ms": t_comp_ms,
                "t_decomp_ms": t_decomp_ms, "sha_rec": sha_rec, "integ_ok": sha_rec == sha_orig}
    finally:
        borrar(ruta_gz, ruta_rec)

def benchmark_peazip(ruta_orig, sha_orig, guardar_en=None):
    """
    Solución externa: comprime con pea.exe (formato PEA) y descomprime con UNPEA para verificar
    el SHA-256, igual que con las otras dos soluciones.
    pea.exe exige rutas absolutas y guarda en el .pea la ruta completa del archivo de entrada.
    """
    base = os.path.join(BASE_DIR, "temp_bench_pea")
    ruta_pea = base + ".pea"
    dir_ext = os.path.join(BASE_DIR, "temp_bench_pea_ext")
    try:
        borrar(ruta_pea)
        # UNPEA crea la carpeta de destino; si ya existe, extrae en otra con otro nombre
        shutil.rmtree(dir_ext, ignore_errors=True)

        t_comp_ms, p = medir_subproceso([PEA_EXE, "PEA", base, *PEAZIP_PARAMETROS, "FROMCL", os.path.abspath(ruta_orig)])
        if p.returncode != 0 or not os.path.exists(ruta_pea):
            sys.exit(f"pea.exe falló con {os.path.basename(ruta_orig)} (código {p.returncode})")
        tam_pea = os.path.getsize(ruta_pea)
        if guardar_en:
            shutil.copyfile(ruta_pea, guardar_en)

        t_decomp_ms, p = medir_subproceso([PEA_EXE, "UNPEA", ruta_pea, dir_ext,
                                           "RESETDATE", "SETATTR", "EXTRACT2DIR", "HIDDEN"])
        ruta_rec = os.path.join(dir_ext, os.path.basename(ruta_orig))
        sha_rec = calcular_hash_sha256(ruta_rec) if p.returncode == 0 and os.path.exists(ruta_rec) else None

        return {"tam_comp": tam_pea, "tam_H": None, "t_comp_ms": t_comp_ms, "t_decomp_ms": t_decomp_ms,
                "sha_rec": sha_rec, "integ_ok": sha_rec == sha_orig}
    finally:
        borrar(ruta_pea)
        shutil.rmtree(dir_ext, ignore_errors=True)

def calcular_metricas(tam_orig, tam_comp, t_comp_ms, t_decomp_ms=None, tam_H=None):
    """Métricas de la consigna. Throughput en MB/s con 1 MB = 10^6 bytes."""
    mb = tam_orig / 1_000_000
    return {
        "r": tam_orig / tam_comp,
        "ahorro": (1.0 - tam_comp / tam_orig) * 100,
        "relativo": tam_comp / tam_orig * 100,
        "vc": mb / (t_comp_ms / 1000) if t_comp_ms else None,
        "vd": mb / (t_decomp_ms / 1000) if t_decomp_ms else None,
        "O": tam_H / tam_comp * 100 if tam_H is not None else None,
    }

def calcular_weissman(r, r_ref, t_ms, t_ref_ms, alpha=1.0):
    """
    W = alpha * (R / Rref) * [log(Tref) / log(T)], con tiempos en milisegundos (consigna).
    No se aplica ningún piso a los tiempos. Si alguno es <= 1 ms el logaritmo es <= 0 y la
    fórmula deja de tener sentido: en ese caso se devuelve None.
    """
    if r <= 0 or r_ref <= 0 or t_ms <= 1 or t_ref_ms <= 1:
        return None
    return alpha * (r / r_ref) * (math.log(t_ref_ms) / math.log(t_ms))

def descripcion_baseline():
    if GZIP_EXE:
        version = subprocess.run([GZIP_EXE, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
        return f"`gzip -n -6` ({version}), ejecutado como subproceso"
    return "módulo `gzip` de Python, nivel 6, `mtime=0` (no se encontró el ejecutable gzip)"

def descripcion_externa():
    if PEA_EXE:
        return (f"PeaZip {version_peazip()}, `pea.exe PEA <salida> {' '.join(PEAZIP_PARAMETROS)} FROMCL <archivo>` "
                "(formato PEA, PCOMPRESS2 = zlib nivel 6, control de volumen SHA3_256, de objeto CRC32 y de stream "
                "RIPEMD160, sin cifrado), ejecutado como subproceso; descompresión con `pea.exe UNPEA`")
    return r"PeaZip no encontrado (se busca pea.exe en C:\Program Files\PeaZip): sus filas se omiten"

def exportar_md_detallado(datos, globales):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    md_path = os.path.join(RESULTS_DIR, "tabla_comparativa.md")

    # Exportar Markdown (ideal para Github y lectura fácil)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Resultados del Benchmark (Grupo 7)\n\n")
        f.write(f"Generado por `benchmark.py` el {datetime.now():%Y-%m-%d %H:%M}.\n\n")

        f.write("## Protocolo de medición\n\n")
        f.write("- **Corpus:** archivos de `tests/` (corpus común de la cátedra); SHA-256 en la tabla de integridad.\n")
        f.write(f"- **Corridas:** {NUM_RUNS} por archivo y solución; se informa la **mediana** de los tiempos.\n")
        f.write("- **Tiempos:** en milisegundos, medidos con `time.perf_counter()`. Las tres soluciones se "
                "ejecutan como subprocesos, por lo que todos los tiempos incluyen el arranque del proceso.\n")
        f.write(f"- **Baseline:** {descripcion_baseline()}.\n")
        f.write(f"- **Solución externa:** {descripcion_externa()}.\n")
        f.write("- **Weissman:** $W = \\alpha \\cdot (R / R_{ref}) \\cdot [\\log(T_{ref}) / \\log(T)]$, con "
                "$\\alpha = 1$, tiempos de compresión en ms y referencia gzip-6. Sin pisos ni ajustes de tiempo. "
                "La prueba 1 no se usa para el ranking temporal.\n")
        f.write("- **Weissman global (oficial):** sobre las pruebas 2 a 4. $R_{global} = \\sum S_o / \\sum S_c$ y "
                "$T_{global}$ = mediana del tiempo total de compresión del corpus.\n")
        f.write(f"- **Entorno:** {platform.platform()}, Python {platform.python_version()}, "
                f"CPU: {platform.processor() or 'no informado'}.\n\n")

        f.write("## Tabla resumen (formato de la consigna)\n\n")
        f.write("| Archivo | Algoritmo | Ratio | Tiempo | Ratio gzip | Tiempo gzip | Weissman |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for arch, d in datos.items():
            g = d["GZIP"]
            for nombre, clave in (("Markov O(1) + Huffman (TDI)", "TDI"), ("PeaZip (PEA)", "PEA")):
                s = d.get(clave)
                if s is None:
                    continue
                f.write(f"| {arch} | {nombre} | {s['m']['r']:.2f} | {s['t_comp_ms']:.2f} ms | {g['m']['r']:.2f} | "
                        f"{g['t_comp_ms']:.2f} ms | {texto_weissman(arch, s)} |\n")

        f.write("\n## Tabla detallada de métricas\n\n")
        f.write("| Archivo | Solución | $S_o$ (B) | $S_c$ (B) | $H$ (B) | $O$ (%) | $R$ | Ahorro (%) | Tamaño relativo (%) "
                "| $T_{comp}$ (ms) | $T_{descomp}$ (ms) | $V_c$ (MB/s) | $V_d$ (MB/s) | Weissman | Integridad |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for arch, d in datos.items():
            for nombre, clave in (("**Python TDI**", "TDI"), ("**GZIP (Ref)**", "GZIP"), ("**PeaZip**", "PEA")):
                s = d.get(clave)
                if s is None:
                    continue
                m = s["m"]
                f.write(f"| {arch if clave == 'TDI' else ''} | {nombre} | {d['tam_orig']} | {s['tam_comp']} | "
                        f"{'-' if s['tam_H'] is None else s['tam_H']} | {format_num(m['O'])} | {m['r']:.2f} | {m['ahorro']:.2f} | "
                        f"{m['relativo']:.2f} | {format_ms(s['t_comp_ms'])} | {format_ms(s.get('t_decomp_ms'))} | "
                        f"{format_num(m['vc'], 4)} | {format_num(m['vd'], 4)} | {texto_weissman(arch, s)} | "
                        f"{texto_integridad(s)} |\n")

        f.write("\n## Weissman global (pruebas 2 a 4)\n\n")
        f.write("| Solución | $\\sum S_o$ (B) | $\\sum S_c$ (B) | $R_{global}$ | $T_{global}$ (ms) | $W$ global |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for nombre, g in globales.items():
            f.write(f"| {nombre} | {g['so']} | {g['sc']} | {g['r']:.3f} | {g['t']:.2f} | {format_num(g['w'], 4)} |\n")

        f.write("\n## Integridad (SHA-256)\n\n")
        claves = [c for c in ("TDI", "GZIP", "PEA") if all(c in d for d in datos.values())]
        nombres = {"TDI": "Reconstruido TDI", "GZIP": "Reconstruido gzip", "PEA": "Reconstruido PeaZip"}
        f.write("| Archivo | SHA-256 original | " + " | ".join(nombres[c] for c in claves) + " |\n")
        f.write("| :--- | :--- |" + " :---: |" * len(claves) + "\n")
        for arch, d in datos.items():
            f.write(f"| {arch} | `{d['sha_orig']}` | "
                    + " | ".join("idéntico" if d[c]["integ_ok"] else "DISTINTO" for c in claves) + " |\n")

        f.write("\n> **Notas:** $H$ de gzip son los 18 B fijos del formato (10 B de cabecera + 8 B de trailer). ")
        if any("PEA" in d for d in datos.values()):
            largos = [d["largo_ruta"] for d in datos.values()]
            f.write(f"El formato PEA guarda dentro del archivo la ruta absoluta de la entrada (entre {min(largos)} y "
                    f"{max(largos)} B en esta medición): forma parte de su tamaño comprimido y depende de la carpeta "
                    "donde esté el repositorio. Por eso no se informa su $H$.")
        f.write("\n")
    return md_path

def texto_weissman(arch, s):
    if arch not in ARCHIVOS_RENDIMIENTO:
        return "n/a (prueba 1)"
    return format_num(s["w"], 4) if s["w"] is not None else "n/d (T <= 1 ms)"

def texto_integridad(s):
    return "OK (SHA-256)" if s["integ_ok"] else "FALLA"

def main():
    print("Ejecutando mediciones detalladas...")
    print(f"Baseline: {descripcion_baseline()}")
    print(f"Solución externa: {descripcion_externa()}")
    datos = {}
    soluciones = ("TDI", "GZIP", "PEA") if PEA_EXE else ("TDI", "GZIP")
    tiempos_por_corrida = {clave: [0.0] * NUM_RUNS for clave in soluciones}
    if PEA_EXE and GUARDAR_PEA:
        os.makedirs(PEA_DIR, exist_ok=True)
    
    for archivo in ARCHIVOS:
        ruta_orig = os.path.join(TESTS_DIR, archivo)
        if not os.path.exists(ruta_orig):
            print(f"  (no se encontró {archivo}, se omite)")
            continue
            
        tam_orig = os.path.getsize(ruta_orig)
        sha_orig = calcular_hash_sha256(ruta_orig)
        runs = {clave: [] for clave in soluciones}
        
        for i in range(NUM_RUNS):
            runs["TDI"].append(benchmark_tdi(ruta_orig, sha_orig))
            runs["GZIP"].append(benchmark_gzip(ruta_orig, sha_orig))
            if PEA_EXE:
                # En la última corrida se guarda una copia del .pea como evidencia
                ultima = GUARDAR_PEA and i == NUM_RUNS - 1
                guardar_en = os.path.join(PEA_DIR, os.path.splitext(archivo)[0] + ".pea") if ultima else None
                runs["PEA"].append(benchmark_peazip(ruta_orig, sha_orig, guardar_en))
                
        if archivo in ARCHIVOS_RENDIMIENTO:
            for clave in soluciones:
                for i, r in enumerate(runs[clave]):
                    tiempos_por_corrida[clave][i] += r["t_comp_ms"]
                    
        resultado = {"tam_orig": tam_orig, "sha_orig": sha_orig,
                     "largo_ruta": len(os.path.abspath(ruta_orig).encode("utf-8"))}
        for clave in soluciones:
            corridas = runs[clave]
            s = {
                "tam_comp": corridas[0]["tam_comp"],
                "tam_H": corridas[0]["tam_H"],
                "t_comp_ms": statistics.median(r["t_comp_ms"] for r in corridas),
                "t_decomp_ms": statistics.median(r["t_decomp_ms"] for r in corridas),
                "integ_ok": all(r["integ_ok"] for r in corridas),
            }
            s["m"] = calcular_metricas(tam_orig, s["tam_comp"], s["t_comp_ms"], s["t_decomp_ms"], s["tam_H"])
            resultado[clave] = s
            
        # Weissman por archivo (informativo); gzip-6 es la referencia, por definición W = 1
        g = resultado["GZIP"]
        for clave in soluciones:
            s = resultado[clave]
            s["w"] = calcular_weissman(s["m"]["r"], g["m"]["r"], s["t_comp_ms"], g["t_comp_ms"])
        datos[archivo] = resultado
        
    # Weissman global (oficial) sobre el corpus de rendimiento
    rend = [a for a in ARCHIVOS_RENDIMIENTO if a in datos]
    so_total = sum(datos[a]["tam_orig"] for a in rend)
    globales = {}
    for nombre, clave in (("Python TDI", "TDI"), ("GZIP (Ref)", "GZIP"), ("PeaZip", "PEA")):
        if clave not in soluciones:
            continue
        sc_total = sum(datos[a][clave]["tam_comp"] for a in rend)
        t_global = statistics.median(tiempos_por_corrida[clave])
        globales[nombre] = {"so": so_total, "sc": sc_total, "r": so_total / sc_total, "t": t_global}
    ref = globales["GZIP (Ref)"]
    for g in globales.values():
        g["w"] = calcular_weissman(g["r"], ref["r"], g["t"], ref["t"])
        
    # Imprimir mini resumen en consola
    print(f"\n{'Archivo':<28} | {'Solucion':<12} | {'Ratio':>7} | {'T comp (ms)':>11} | {'Integridad':<12} | Weissman")
    print("-" * 94)
    for arch, d in datos.items():
        for nombre, clave in (("Python TDI", "TDI"), ("GZIP (Ref)", "GZIP"), ("PeaZip", "PEA")):
            s = d.get(clave)
            if s is None:
                continue
            print(f"{arch if clave == 'TDI' else '':<28} | {nombre:<12} | {s['m']['r']:>7.2f} | {s['t_comp_ms']:>11.2f} | "
                  f"{texto_integridad(s):<12} | {texto_weissman(arch, s)}")
        print("-" * 94)
    print("\nWeissman global (pruebas 2 a 4):")
    for nombre, g in globales.items():
        print(f"  {nombre:<12} R_global = {g['r']:.3f}  T_global = {g['t']:.2f} ms  W = {format_num(g['w'], 4)}")
        
    md_path = exportar_md_detallado(datos, globales)
    print(f"\nLas métricas detalladas (throughput, cabeceras, overhead, Weissman, SHA-256, etc.)")
    print(f"fueron exportadas en Markdown a '{md_path}'.")

if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    main()
