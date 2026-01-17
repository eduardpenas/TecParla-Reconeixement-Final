import os
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
SRC_DIR = "ramses"
DATA_DIR = "."
CMD_PYTHON = "python3"
# Añadir al path para importar módulos
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + os.pathsep + os.path.abspath(SRC_DIR)

def run_pipeline(orden, eps, run_name):
    """Ejecuta el pipeline completo y devuelve la exactitud"""
    print(f"--- Ejecutando Pipeline: Orden={orden}, Eps={eps} ---")
    prm_dir = os.path.join(DATA_DIR, "Prm", run_name)
    mod_dir = os.path.join(DATA_DIR, "Mod", run_name)
    rec_dir = os.path.join(DATA_DIR, "Rec", run_name)
    res_file = os.path.join(DATA_DIR, "Res", run_name + ".res")
    
    # Crear carpetas
    for d in [prm_dir, mod_dir, rec_dir, os.path.dirname(res_file)]:
        os.makedirs(d, exist_ok=True)

    train_gui = os.path.join(DATA_DIR, "Gui", "train.gui")
    devel_gui = os.path.join(DATA_DIR, "Gui", "devel.gui")
    vocales_lis = os.path.join(DATA_DIR, "Lis", "vocales.lis")
    vocales_mod = os.path.join(mod_dir, "vocales.mod")
    sen_dir = os.path.join(DATA_DIR, "Sen")

    # 1. Crear script ME.py temporal
    exec_prev = os.path.join(prm_dir, "ME.py")
    with open(exec_prev, "w") as f:
        f.write(f"import numpy as np\nfrom maxima_entropia import maximaEntropia\n")
        f.write(f"orden={orden}\neps={eps}\n")
        f.write(f"def ME(x):\n    return np.log(eps + maximaEntropia(x, orden))\n")
    
    # Comandos
    cmds = [
        [CMD_PYTHON, os.path.join(SRC_DIR, "parametriza.py"), "-s", sen_dir, "-p", prm_dir, "-f", "ME", "-e", exec_prev, train_gui, devel_gui],
        [CMD_PYTHON, os.path.join(SRC_DIR, "entrena.py"), "-p", prm_dir, "-m", sen_dir, "-l", vocales_lis, "-M", vocales_mod, train_gui],
        [CMD_PYTHON, os.path.join(SRC_DIR, "reconoce.py"), "-r", rec_dir, "-p", prm_dir, "-M", vocales_mod, devel_gui]
    ]

    for cmd in cmds:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Evaluación
    cmd_eval = [CMD_PYTHON, os.path.join(SRC_DIR, "evalua.py"), "-r", rec_dir, "-m", sen_dir, devel_gui]
    result = subprocess.run(cmd_eval, capture_output=True, text=True, check=True)
    
    match = re.search(r"exact\s*=\s*([\d.]+)%", result.stdout)
    return float(match.group(1)) if match else 0.0

def load_prm_file(filepath):
    try: return np.loadtxt(filepath)
    except: return np.load(filepath)

def plot_vowel_models_orden_8():
    """Genera las gráficas infiriendo la vocal desde el nombre del archivo"""
    print("\nGenerando gráficas de modelos de vocales (Orden=8)...")
    
    # 1. Asegurar datos
    run_name = "modelo_vocales_final"
    run_pipeline(8, 0.1, run_name) 
    
    prm_dir = os.path.join(DATA_DIR, "Prm", run_name)
    train_gui = os.path.join(DATA_DIR, "Gui", "train.gui")
    
    vocal_data = {'a': [], 'e': [], 'i': [], 'o': [], 'u': []}
    
    # 2. Indexar ficheros en Prm para búsqueda rápida
    print(f"Indexando ficheros en {prm_dir}...")
    file_map = {}
    for root, dirs, files in os.walk(prm_dir):
        for f in files:
            # Clave: 'a000' -> Valor: '/ruta/completa/a000.npy' (o .prm)
            base = f.split('.')[0] 
            file_map[base] = os.path.join(root, f)
            
    print(f"Ficheros encontrados en Prm: {len(file_map)}")

    # 3. Leer train.gui e inferir etiquetas
    print(f"Procesando {train_gui}...")
    count = 0
    with open(train_gui, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Ejemplo linea: vocales/block00/a000
            filename = os.path.basename(line) # a000
            base_name = filename.split('.')[0] # a000
            
            # --- INFERENCIA DE ETIQUETA ---
            # La primera letra del archivo es la vocal
            vocal_char = base_name[0].lower()
            
            if vocal_char in vocal_data:
                # Buscamos el fichero parametrizado correspondiente
                if base_name in file_map:
                    try:
                        feat = load_prm_file(file_map[base_name])
                        if np.ndim(feat) > 0:
                            vocal_data[vocal_char].append(feat)
                            count += 1
                    except Exception as e:
                        pass # Ignorar errores de lectura puntuales

    print(f"Total vocales cargadas correctamente: {count}")
    
    if count == 0:
        print("ERROR CRÍTICO: No se han podido cargar datos. Verifica que Parametriza.py haya generado archivos.")
        return

    # 4. Graficar
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Modelos de las cinco vocales (Máxima Entropía, orden=8)', fontsize=16)
    
    colors = {'a': 'r', 'e': 'g', 'i': 'b', 'o': 'k', 'u': 'y'}
    vowels = ['a', 'e', 'i', 'o', 'u']
    
    # Asumimos Fs=8000Hz -> Nyquist=4000Hz
    # Si los vectores tienen N puntos, el eje X va de 0 a 4000
    sample_len = len(vocal_data['a'][0]) if len(vocal_data['a']) > 0 else 129
    freqs = np.linspace(0, 4000, sample_len)

    # Gráficas individuales
    for i, ax in enumerate(axes.flat[:5]):
        v = vowels[i]
        data = vocal_data[v]
        if len(data) > 0:
            # Calcular media ignorando diferencias pequeñas de longitud
            min_len = min(len(d) for d in data)
            data_trimmed = [d[:min_len] for d in data]
            model_mean = np.mean(np.array(data_trimmed), axis=0)
            
            # Ajustar eje de frecuencias al tamaño real
            freqs_v = np.linspace(0, 4000, len(model_mean))
            
            ax.plot(freqs_v, model_mean, color=colors[v], linewidth=2)
            ax.set_title(f'Vocal /{v}/')
            ax.set_ylabel('Amplitud (dB)')
            ax.grid(True, alpha=0.5)
            
            # Añadir a la comparativa
            axes.flat[5].plot(freqs_v, model_mean, color=colors[v], label=f'/{v}/')

    # Gráfica comparativa
    ax_comp = axes.flat[5]
    ax_comp.set_title('Comparación de los cinco modelos')
    ax_comp.legend()
    ax_comp.grid(True, alpha=0.5)
    ax_comp.set_xlabel('Frecuencia (Hz)')

    plt.tight_layout()
    plt.subplots_adjust(top=0.9) # Espacio para el título
    plt.savefig("modelos_vocales_orden_8.png")
    print("\n>>> GRÁFICA GUARDADA: modelos_vocales_orden_8.png")

# Funciones extra para los otros apartados
def plot_accuracy_vs_order():
    print("\nGenerando curva Exactitud vs Orden...")
    ordenes = list(range(2, 21, 2))
    accs = [run_pipeline(o, 0.1, f"exp_orden_{o}") for o in ordenes]
    
    plt.figure()
    plt.plot(ordenes, accs, marker='o', linewidth=2)
    plt.title("Exactitud vs Orden LPC (eps=0.1)")
    plt.xlabel("Orden")
    plt.ylabel("Exactitud (%)")
    plt.grid(True)
    plt.xticks(ordenes)
    plt.savefig("exactitud_vs_orden.png")
    print(">>> GRÁFICA GUARDADA: exactitud_vs_orden.png")

def table_accuracy_vs_eps():
    print("\nGenerando tabla Exactitud vs Eps...")
    eps_vals = [0.00001, 0.1, 1, 10, 100, 1000]
    print(f"| {'Epsilon':<10} | {'Exactitud':<10} |")
    print("|" + "-"*12 + "|" + "-"*12 + "|")
    
    for e in eps_vals:
        run_name = f"exp_eps_{e}".replace('.','_').replace('+','')
        acc = run_pipeline(8, e, run_name)
        print(f"| {e:<10} | {acc:<9.2f}% |")

if __name__ == "__main__":
    # Descomenta lo que necesites generar:
    
    # 1. Gráfica de vocales (Lo que pediste ahora)
    plot_vowel_models_orden_8()
    
    # 2. Gráfica de orden (Tarda un poco)
    # plot_accuracy_vs_order()
    
    # 3. Tabla de Epsilon
    # table_accuracy_vs_eps()
    
    print("\n--- Fin del proceso ---")