import os
import subprocess
import re
import itertools
import sys

# Configuración
SRC_DIR = "ramses"
# Asegurar que python encuentre el módulo local
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + os.pathsep + os.path.abspath(".")

def run_experiment(num_capas, neuronas, activacion_nombre, lr=1e-4, epochs=25):
    """
    Ejecuta un entrenamiento completo (entrena + reconoce + evalua).
    """
    run_name = f"mlp_L{num_capas}_N{neuronas}_{activacion_nombre}"
    print(f"\n>>> Probando Configuración: {run_name} (Adam, lr={lr})")
    
    mod_file = f"Mod/{run_name}.mod"
    rec_dir = f"Rec/{run_name}"
    
    # String para definir la activación en el código dinámico
    if activacion_nombre == "ReLU":
        act_str = "torch.nn.ReLU()"
    else:
        act_str = "torch.nn.Sigmoid()"
    
    # Crear archivo de configuración temporal para este experimento
    conf_file = f"conf/temp_{run_name}.py"
    os.makedirs("conf", exist_ok=True)
    
    # IMPORTANTE: Definimos la red dentro del string para pasarla a entorch
    model_str = (
        f"ModPT(ficLisUni='Lis/vocales.lis', "
        f"red=mlp_N(numCap={num_capas}, dimIni=18, dimInt={neuronas}, dimSal=5, clsAct={act_str}), "
        f"Optim=lambda p: torch.optim.Adam(p, lr={lr}))"
    )
    
    # Escribimos el script de configuración que cargará entrena.py
    with open(conf_file, "w") as f:
        f.write("import torch\n")
        f.write("from ramses.red_pt import ModPT, lotesPT, calcDimIni, calcDimSal\n")
        f.write("from ramses.mlp import mlp_N\n")
        f.write("dirPrm='Prm/mfcc_optimo'\n") # Usa tus MFCC optimos
        f.write("dirMar='Sen'\n")
        f.write("ficLisUni='Lis/vocales.lis'\n")
        f.write("guiTrain='Gui/train.gui'\n")
        f.write("guiDevel='Gui/devel.gui'\n")
        f.write("# Generación de lotes\n")
        f.write("lotesEnt = lotesPT(dirPrm, dirMar, ficLisUni, guiTrain)\n")
        f.write("lotesDev = lotesPT(dirPrm, dirMar, ficLisUni, guiDevel)\n")

    # 1. ENTRENAMIENTO
    cmd_train = [
        "python3", "ramses/entrena.py",
        "-e", str(epochs),
        "--execPrev", conf_file,      # Carga imports y lotes
        "--lotesEnt", "lotesEnt",     # Nombre de variable en config
        "--lotesDev", "lotesDev",     # Nombre de variable en config
        "-M", model_str,              # Constructor del modelo
        mod_file
    ]
    
    try:
        # Ejecutamos ocultando output excesivo, solo mostramos errores graves
        subprocess.run(cmd_train, check=True) # stderr=subprocess.DEVNULL
    except subprocess.CalledProcessError:
        print(f"Error entrenando {run_name}")
        return 0.0

    # 2. RECONOCIMIENTO
    cmd_rec = [
        "python3", "ramses/reconoce.py",
        "-r", rec_dir,
        "-p", "Prm/mfcc_optimo",
        "-M", mod_file,
        "--classMod", "ModPT", # Forzamos uso de clase ModPT
        "Gui/devel.gui"
    ]
    subprocess.run(cmd_rec, check=True, stderr=subprocess.DEVNULL)
    
    # 3. EVALUACIÓN
    cmd_eval = ["python3", "ramses/evalua.py", "-r", rec_dir, "-m", "Sen", "Gui/devel.gui"]
    res = subprocess.run(cmd_eval, capture_output=True, text=True)
    
    # Extraer exactitud con regex
    match = re.search(r"exact\s*=\s*([\d.]+)%", res.stdout)
    acc = float(match.group(1)) if match else 0.0
    
    print(f"Result: {acc}%")
    return acc

def generar_todo_sh(best_cfg, lr):
    """Genera el script final de entrega"""
    c, n, a = best_cfg
    act_str = "torch.nn.ReLU()" if a == "ReLU" else "torch.nn.Sigmoid()"
    
    content = f"""#!/bin/bash
# SCRIPT FINAL OPTIMIZADO (RAMSES)
# Configuracion Ganadora: MLP {c} capas, {n} neuronas, {a}, Adam lr={lr}

# 1. Parametrizacion (Si no existe, se crea)
if [ ! -d "Prm/mfcc_optimo" ]; then
    echo "Generando MFCC..."
    # Aqui iria tu comando de parametrizacion si fuera necesario
    # python3 ramses/parametriza.py ... 
fi

# 2. Configuración Python para entrena.py
cat <<EOT > conf/final_config.py
import torch
from ramses.red_pt import ModPT, lotesPT
from ramses.mlp import mlp_N
dirPrm='Prm/mfcc_optimo'
dirMar='Sen'
ficLisUni='Lis/vocales.lis'
guiTrain='Gui/train.gui'
guiDevel='Gui/devel.gui'
lotesEnt = lotesPT(dirPrm, dirMar, ficLisUni, guiTrain)
lotesDev = lotesPT(dirPrm, dirMar, ficLisUni, guiDevel)
EOT

# 3. Entrenamiento
echo "Entrenando Modelo Final..."
python3 ramses/entrena.py \\
    -e 35 \\
    --execPrev conf/final_config.py \\
    --lotesEnt lotesEnt \\
    --lotesDev lotesDev \\
    -M "ModPT(ficLisUni='Lis/vocales.lis', red=mlp_N(numCap={c}, dimIni=18, dimInt={n}, dimSal=5, clsAct={act_str}), Optim=lambda p: torch.optim.Adam(p, lr={lr}))" \\
    Mod/modelo_final.mod

# 4. Reconocimiento
echo "Reconociendo..."
python3 ramses/reconoce.py \\
    -r Rec/final \\
    -p Prm/mfcc_optimo \\
    -M Mod/modelo_final.mod \\
    --classMod ModPT \\
    Gui/devel.gui

# 5. Evaluación
echo "Evaluando..."
python3 ramses/evalua.py -r Rec/final -m Sen Gui/devel.gui
"""
    with open("ramses/todo.sh", "w") as f:
        f.write(content)
    os.chmod("ramses/todo.sh", 0o755)
    print("\n>>> Script ramses/todo.sh generado con éxito.")

def main():
    # --- ESPACIO DE BÚSQUEDA ---
    # Probaremos topologías comunes para este tipo de tareas
    capas_opts = [2, 3, 4]        # 2=Lineal, 3=1 oculta, 4=2 ocultas
    neuronas_opts = [64, 128, 256] # Tamaño capa oculta
    act_opts = ["ReLU", "Sigmoid"] # Tipos de activación
    
    lr = 1e-4 # Learning rate recomendado en el PDF para Adam
    
    best_acc = -1
    best_cfg = None
    
    print("=== OPTIMIZACIÓN DE RED NEURONAL (PyTorch) ===")
    
    for c, n, a in itertools.product(capas_opts, neuronas_opts, act_opts):
        acc = run_experiment(c, n, a, lr)
        
        if acc > best_acc:
            best_acc = acc
            best_cfg = (c, n, a)
            print(f"  -> ¡Nuevo mejor resultado!")
            
    print("\n" + "="*50)
    print(f"MEJOR RESULTADO: {best_acc}%")
    print(f"Configuración: {best_cfg[0]} capas, {best_cfg[1]} neuronas, {best_cfg[2]}")
    print("="*50)
    
    # Generar entregable
    generar_todo_sh(best_cfg, lr)

if __name__ == "__main__":
    main()