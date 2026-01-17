#! /usr/bin/env python3

import sys
import os
import numpy as np
from tqdm import tqdm
from collections import namedtuple

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ramses.util import *
from ramses.prm import *
from ramses.mod import *
from ramses.gaussiano import Gauss

try:
    from ramses.gmm import GMM
except ImportError: GMM = None

try:
    from ramses.red_pt import ModPT
    import torch
except ImportError: ModPT = None

def robust_load(path):
    try: return np.loadtxt(path)
    except: return np.load(path)

def reconoce(dirRec, dirPrm, ficMod, *ficGui, ClsMod=Gauss):
    print(f"--- Reconociendo con {ClsMod.__name__ if ClsMod else 'Desconocido'} ---")
    
    try:
        modelo_global = ClsMod(ficMod=ficMod)
    except Exception as e:
        print(f"Error CRÍTICO cargando modelo {ficMod}: {e}")
        return

    lista_ficheros = leeLis(*ficGui)
    count = 0
    SenalDummy = namedtuple('senal', ['sen', 'prm', 'trn'])

    for sen in tqdm(lista_ficheros):
        base_path = str(pathName(dirPrm, sen, 'prm'))
        candidates = [base_path, base_path + '.npy', os.path.join(dirPrm, sen + '.npy')]
        
        pathPrm = None
        for cand in candidates:
            if os.path.exists(cand):
                pathPrm = cand
                break
        
        if not pathPrm: continue

        try:
            arr = robust_load(pathPrm)
            
            if ClsMod.__name__ == 'ModPT':
                if arr.ndim > 1: arr = np.mean(arr, axis=0)
                prm_input = torch.tensor(arr, dtype=torch.float).reshape(1, 1, 1, -1)
                obj_input = SenalDummy(sen=sen, prm=prm_input, trn=None)
                best_vocal = modelo_global(obj_input)
            else:
                if hasattr(modelo_global, 'prob'):
                    scores = modelo_global.prob(arr)
                    best_vocal = max(scores, key=scores.get)
                elif hasattr(modelo_global, '__call__'):
                    res = modelo_global(arr)
                    if isinstance(res, dict): best_vocal = max(res, key=res.get)
                    else: best_vocal = res
                else:
                    best_vocal = '?'

        except Exception: continue
        
        pathRec = str(pathName(dirRec, sen, 'rec'))
        os.makedirs(os.path.dirname(pathRec), exist_ok=True)
        with open(pathRec, 'w') as f:
            f.write(f"{best_vocal}\n")
        count += 1
        
    print(f"Reconocidas {count} señales.")

if __name__ == "__main__":
    from docopt import docopt
    # Formato limpio para docopt
    usage="""Reconoce vocales usando un modelo entrenado

Usage:
  reconoce.py [options] <guia> ...

Options:
  -r PATH, --dirRec PATH    Directorio salida resultados [default: .]
  -p PATH, --dirPrm PATH    Directorio señales parametrizadas [default: .]
  -M PATH, --ficMod PATH    Fichero con el modelo [default: Mod/vocales.mod]
  -C CLASS, --classMod CLASS Clase de modelo [default: Gauss]
"""
    args = docopt(usage, version="ramses-rec-v4")
    
    cls_name = args["--classMod"]
    
    if cls_name == 'ModPT': ClsMod = ModPT
    elif cls_name == 'GMM': ClsMod = GMM
    else: 
        try: ClsMod = eval(cls_name)
        except: ClsMod = Gauss

    reconoce(args["--dirRec"], args["--dirPrm"], args["--ficMod"], *args["<guia>"], ClsMod=ClsMod)