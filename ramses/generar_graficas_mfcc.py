import os
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
SRC_DIR = "ramses"
DATA_DIR = "."
CMD_PYTHON = "python3"
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + os.pathsep + os.path.abspath(SRC_DIR)

def run_mfcc_pipeline(numcep, nfilt, run_name):
    """Ejecuta el pipeline usando MFCC con los parámetros dados"""
    print(f"--- Ejecutando MFCC: NumCep={numcep}, NFilt={nfilt} ---")
    
    # Directorios
    prm_dir = os.path.join(DATA_DIR, "Prm", run_name)
    mod_dir = os.path.join(DATA_DIR, "Mod", run_name)
    rec_dir = os.path.join(DATA_DIR, "Rec", run_name)
    res_file = os.path.join(DATA_DIR, "Res", run_name + ".res")
    
    for d in [prm_dir, mod_dir, rec_dir, os.path.dirname(res_file)]:
        os.makedirs(d, exist_ok=True)

    train_gui = os.path.join(DATA_DIR, "Gui", "train.gui")
    devel_gui = os.path.join(DATA_DIR, "Gui", "devel.gui")
    vocales_lis = os.path.join(DATA_DIR, "Lis", "vocales.lis")
    vocales_mod = os.path.join(mod_dir, "vocales.mod")
    sen_dir = os.path.join(DATA_DIR, "Sen")

    # 1. Crear script temporal de extracción MFCC
    exec_prev = os.path.join(prm_dir, "MFCC_extract.py")
    with open(exec_prev, "w") as f:
        f.write("import numpy as np\n")
        f.write("from python_speech_features import mfcc\n")
        f.write(f"numcep={numcep}\n")
        f.write(f"nfilt={nfilt}\n")
        f.write("def get_mfcc(x):\n")
        f.write("    # fs=8000 es el estandar de la base de datos TecParla\n")
        f.write("    # winlen=0.025 (25ms), winstep=0.01 (10ms)\n")
        f.write("    feat = mfcc(x, samplerate=8000, winlen=0.025, winstep=0.01, numcep=numcep, nfilt=nfilt)\n")
        f.write("    # IMPORTANTE: Ramses espera un vector por vocal, hacemos la media de los tramos\n")
        f.write("    return np.mean(feat, axis=0)\n")
    
    # 2. Ejecutar comandos (Parametriza, Entrena, Reconoce)
    cmds = [
        [CMD_PYTHON, os.path.join(SRC_DIR, "parametriza.py"), "-s", sen_dir, "-p", prm_dir, "-f", "get_mfcc", "-e", exec_prev, train_gui, devel_gui],
        [CMD_PYTHON, os.path.join(SRC_DIR, "entrena.py"), "-p", prm_dir, "-m", sen_dir, "-l", vocales_lis, "-M", vocales_mod, train_gui],
        [CMD_PYTHON, os.path.join(SRC_DIR, "reconoce.py"), "-r", rec_dir, "-p", prm_dir, "-M", vocales_mod, devel_gui]
    ]

    for cmd in cmds:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Evaluar
    cmd_eval = [CMD_PYTHON, os.path.join(SRC_DIR, "evalua.py"), "-r", rec_dir, "-m", sen_dir, devel_gui]
    result = subprocess.run(cmd_eval, capture_output=True, text=True, check=True)
    
    match = re.search(r"exact\s*=\s*([\d.]+)%", result.stdout)
    return float(match.group(1)) if match else 0.0

def experiment_numcep():
    """Optimizar número de coeficientes (con nfilt fijo a 26)"""
    print("\n=== EXPERIMENTO 1: Optimizando NumCep (NFilt=26) ===")
    nfilt_fixed = 26
    # Probamos valores típicos. El estándar suele ser 13.
    numceps = [8, 10, 12, 13, 14, 16, 18, 20]
    results = []

    for nc in numceps:
        # Nota: nfilt debe ser > numcep, si nc se acerca a 26 podría dar error si no ajustamos
        acc = run_mfcc_pipeline(nc, nfilt_fixed, f"mfcc_nc{nc}_nf{nfilt_fixed}")
        results.append(acc)
        print(f"  NumCep={nc} -> Exactitud={acc}%")

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.plot(numceps, results, marker='o', linewidth=2, color='purple')
    plt.title(f"Exactitud vs Número de Coeficientes MFCC (Filtros={nfilt_fixed})")
    plt.xlabel("Número de Coeficientes (numcep)")
    plt.ylabel("Exactitud (%)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(numceps)
    plt.savefig("mfcc_exactitud_vs_numcep.png")
    print(">>> Gráfica guardada: mfcc_exactitud_vs_numcep.png")
    
    # Retornar el mejor numcep para el siguiente paso
    best_idx = np.argmax(results)
    return numceps[best_idx]

def experiment_nfilt(best_numcep):
    """Optimizar número de filtros (con el mejor numcep hallado)"""
    print(f"\n=== EXPERIMENTO 2: Optimizando NFilt (NumCep={best_numcep}) ===")
    # Probamos densidad de filtros.
    # Cuidado: nfilt debe ser al menos numcep + 1 para evitar problemas de Nyquist/matemáticos
    start_filt = best_numcep + 2
    nfilts = [start_filt, 20, 24, 26, 30, 32, 40]
    nfilts = sorted(list(set([n for n in nfilts if n > best_numcep]))) # Filtrar validos y ordenar
    
    results = []

    for nf in nfilts:
        acc = run_mfcc_pipeline(best_numcep, nf, f"mfcc_nc{best_numcep}_nf{nf}")
        results.append(acc)
        print(f"  NFilt={nf} -> Exactitud={acc}%")

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.plot(nfilts, results, marker='s', linewidth=2, color='orange')
    plt.title(f"Exactitud vs Número de Filtros (Coeficientes={best_numcep})")
    plt.xlabel("Número de Filtros (nfilt)")
    plt.ylabel("Exactitud (%)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(nfilts)
    plt.savefig("mfcc_exactitud_vs_nfilt.png")
    print(">>> Gráfica guardada: mfcc_exactitud_vs_nfilt.png")

if __name__ == "__main__":
    # 1. Encontrar el mejor número de coeficientes
    best_nc = experiment_numcep()
    print(f"\nMejor configuración de coeficientes encontrada: {best_nc}")
    
    # 2. Con ese mejor número, optimizar los filtros
    experiment_nfilt(best_nc)
    
    print("\n--- Proceso MFCC completado ---")