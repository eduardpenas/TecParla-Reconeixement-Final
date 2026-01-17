import os
import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURACIÓN ---
SRC_DIR = "ramses"
DATA_DIR = "."
CMD_PYTHON = "python3"
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + os.pathsep + os.path.abspath(SRC_DIR)

def run_gmm_pipeline(nmix, run_name):
    """Pipeline MFCC fijo + GMM variable"""
    print(f"--- Ejecutando GMM: Nmix={nmix} ---")
    
    prm_dir = os.path.join(DATA_DIR, "Prm", "mfcc_optimo") # Reutilizamos parametrización si existe
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

    # 1. Parametrización (Solo si no existe ya, usamos la optima MFCC 18, 20)
    # Si quieres asegurar, borra Prm/mfcc_optimo antes.
    exec_prev = os.path.join(prm_dir, "MFCC_opt.py")
    if not os.path.exists(exec_prev):
        with open(exec_prev, "w") as f:
            f.write("import numpy as np\nfrom python_speech_features import mfcc\n")
            f.write("def get_mfcc(x):\n")
            f.write("    feat = mfcc(x, samplerate=8000, winlen=0.025, winstep=0.01, numcep=18, nfilt=20)\n")
            f.write("    return np.mean(feat, axis=0)\n") # Importante: devuelve vector
            
        cmd_prm = [CMD_PYTHON, os.path.join(SRC_DIR, "parametriza.py"), "-s", sen_dir, "-p", prm_dir, "-f", "get_mfcc", "-e", exec_prev, train_gui, devel_gui]
        subprocess.run(cmd_prm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Entrenamiento GMM (Aquí pasamos el parametro nmix)
    cmd_train = [CMD_PYTHON, os.path.join(SRC_DIR, "entrena.py"), 
                 "-p", prm_dir, "-m", sen_dir, "-l", vocales_lis, "-M", vocales_mod, 
                 train_gui, "--nmix", str(nmix), "--iter", "20"]
    subprocess.run(cmd_train, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Reconocimiento
    cmd_rec = [CMD_PYTHON, os.path.join(SRC_DIR, "reconoce.py"), "-r", rec_dir, "-p", prm_dir, "-M", vocales_mod, devel_gui]
    subprocess.run(cmd_rec, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Evaluar
    cmd_eval = [CMD_PYTHON, os.path.join(SRC_DIR, "evalua.py"), "-r", rec_dir, "-m", sen_dir, devel_gui]
    result = subprocess.run(cmd_eval, capture_output=True, text=True, check=True)
    
    match = re.search(r"exact\s*=\s*([\d.]+)%", result.stdout)
    return float(match.group(1)) if match else 0.0

def experiment_nmix():
    print("\n=== EXPERIMENTO GMM: Optimizando Nmix ===")
    nmixes = [1, 2, 4, 8, 16, 32]
    results = []

    for nm in nmixes:
        acc = run_gmm_pipeline(nm, f"gmm_nmix{nm}")
        results.append(acc)
        print(f"  Gaussianas={nm} -> Exactitud={acc}%")

    plt.figure(figsize=(10, 6))
    plt.plot(nmixes, results, marker='D', linewidth=2, color='green')
    plt.title("Exactitud vs Número de Gaussianas (MFCC Optimo)")
    plt.xlabel("Número de Gaussianas por Mezcla")
    plt.ylabel("Exactitud (%)")
    plt.grid(True, linestyle='--')
    plt.xticks(nmixes)
    plt.savefig("gmm_exactitud_vs_nmix.png")
    print(">>> Gráfica guardada: gmm_exactitud_vs_nmix.png")

if __name__ == "__main__":
    experiment_nmix()