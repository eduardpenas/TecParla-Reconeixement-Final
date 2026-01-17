#! /usr/bin/env python3

import sys
import os
import argparse
import numpy as np
from tqdm import tqdm
from datetime import datetime as dt

# Fix path para encontrar módulos locales
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ramses.util import *
from ramses.mod import *

# Imports para evaluación dinámica
try:
    from ramses.gaussiano import Gauss
    from ramses.gmm import GMM, ModGMM
    from ramses.red_pt import ModPT
    from ramses.mlp import mlp_N
    import torch
except ImportError:
    pass 

def entrena(modelo, lotesEnt, lotesDev=None, nomMod=None, numEpo=1):
    print(f'--- Inicio entrenamiento: {numEpo} épocas ({dt.now():%H:%M:%S}) ---')
    
    for epo in range(numEpo):
        # 1. Fase de Entrenamiento
        if hasattr(modelo, 'inicEntr'):
            modelo.inicEntr()
            
        # Barra de progreso
        pbar = tqdm(lotesEnt, desc=f"Epo {epo+1}/{numEpo}", leave=False)
        for lote in pbar:
            # Batch Processing (Deep Learning) vs Single Item (GMM)
            if hasattr(modelo, 'batch_add'):
                modelo.batch_add(lote)
            else:
                for senal in lote:
                    modelo + senal 
            
            # Actualizar pesos
            if hasattr(modelo, 'recaMod'):
                modelo.recaMod()

        # 2. Fase de Evaluación
        if lotesDev:
            if hasattr(modelo, 'inicEval'): modelo.inicEval()
            for lote in lotesDev:
                if hasattr(modelo, 'batch_eval'):
                    modelo.batch_eval(lote)
                else:
                    for senal in lote:
                        if hasattr(modelo, 'addEval'): modelo.addEval(senal)
            
            if hasattr(modelo, 'recaEval'): modelo.recaEval()
            if hasattr(modelo, 'printEval'): modelo.printEval(epo)

        # 3. Guardado intermedio
        if nomMod:
            modelo.escrMod(nomMod)

    print(f'--- Fin entrenamiento ({dt.now():%H:%M:%S}) ---')

if __name__ == "__main__":
    # --- ARGPARSE: Mucho más robusto que docopt para strings complejos ---
    parser = argparse.ArgumentParser(description='Entrena modelo acústico Ramses')
    parser.add_argument('-e', '--numEpo', type=int, default=1, help='Número de épocas')
    parser.add_argument('-x', '--execPrev', type=str, help='Script de configuración previa')
    parser.add_argument('--lotesEnt', type=str, help='Nombre variable lotes entrenamiento')
    parser.add_argument('--lotesDev', type=str, help='Nombre variable lotes desarrollo')
    parser.add_argument('-M', '--modelo', type=str, help='Definición del modelo (Python string)')
    parser.add_argument('nomMod', type=str, help='Fichero de salida (.mod)')

    args = parser.parse_args()

    # 1. Ejecutar configuración previa en el entorno GLOBAL
    if args.execPrev:
        with open(args.execPrev) as f:
            exec(f.read(), globals())
        
    # 2. Obtener lotes del entorno global
    lotesEnt = eval(args.lotesEnt) if args.lotesEnt else []
    lotesDev = eval(args.lotesDev) if args.lotesDev else None
    
    # 3. Construir modelo
    if args.modelo:
        modelo = eval(args.modelo)
    elif 'modelo' in globals():
        modelo = globals()['modelo']
    else:
        sys.exit("Error: Debes especificar un modelo con -M o definir 'modelo' en execPrev.")

    # 4. Entrenar
    entrena(modelo, lotesEnt, lotesDev, args.nomMod, args.numEpo)