#! /usr/bin/env python3

import sys
import os
import numpy as np
from tqdm import tqdm

# --- FIX PATH: Para que encuentre el paquete 'ramses' ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# --------------------------------------------------------

from ramses.util import *
from ramses.mar import * # Importante para cogeTrn

def evalua(dirRec, dirMar, *ficGui):
    """
    Evalúa los resultados del reconocimiento.
    Calcula la matriz de confusión y el porcentaje de exactitud.
    """
    vocales = ['a', 'e', 'i', 'o', 'u']
    mapa_vocales = {v: i for i, v in enumerate(vocales)}
    matriz = np.zeros((5, 5), dtype=int)
    
    total = 0
    aciertos = 0
    
    lista_ficheros = leeLis(*ficGui)
    
    print(f"Evaluando {len(lista_ficheros)} señales...")
    
    for señal in tqdm(lista_ficheros):
        # 1. Leer Ground Truth (Etiqueta Real)
        pathMar = pathName(dirMar, señal, 'mar')
        if not os.path.exists(pathMar): 
            continue
            
        try:
            real = cogeTrn(pathMar).lower()
        except:
            continue
        
        # 2. Leer Predicción (Etiqueta Reconocida)
        pathRec = pathName(dirRec, señal, 'rec')
        if not os.path.exists(pathRec): 
            # Si no hay fichero, cuenta como error
            total += 1
            continue
            
        try:
            with open(pathRec, 'r') as f:
                reconocido = f.read().strip().lower()
        except:
            total += 1
            continue
            
        # 3. Actualizar estadísticas
        if real in mapa_vocales and reconocido in mapa_vocales:
            idx_real = mapa_vocales[real]
            idx_rec = mapa_vocales[reconocido]
            matriz[idx_real, idx_rec] += 1
            
            if real == reconocido:
                aciertos += 1
            total += 1

    # Mostrar Resultados
    print("\n" + "="*45)
    print("MATRIZ DE CONFUSIÓN (Filas=Real, Cols=Rec)")
    print("="*45)
    print("\t" + "\t".join(vocales))
    print("-" * 45)
    for i, v_real in enumerate(vocales):
        row_str = f"{v_real}\t" + "\t".join([str(matriz[i, j]) for j in range(5)])
        print(row_str)
    print("-" * 45)
        
    exactitud = (aciertos / total * 100) if total > 0 else 0.0
    print(f"Exactitud Global = {exactitud:.2f}%")

if __name__ == "__main__":
    from docopt import docopt
    
    usage=f"""
Evalúa el reconocimiento de vocales

usage:
    {sys.argv[0]} [options] <guia> ...

options:
    -r, --dirRec PATH   Directorio con los resultados del reconocimiento [default: .]
    -m, --dirMar PATH   Directorio con las marcas correctas (Ground Truth) [default: .]
    """
    args = docopt(usage, version="ramses-eval-v2")
    
    evalua(args["--dirRec"], args["--dirMar"], *args["<guia>"]) 