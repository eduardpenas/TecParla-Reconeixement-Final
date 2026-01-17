#! /usr/bin/env python3

import numpy as np
from tqdm import tqdm
import sys
import pickle
import os

# --- CORRECCIÓN: Imports separados línea por línea ---
from ramses.util import *
from ramses.prm import * from ramses.mar import * from ramses.mod import *
from ramses.euclidio import Euclidio
from ramses.gaussiano import Gauss
# -----------------------------------------------------

# Importamos nuestra nueva clase GMM de forma segura
try:
    from ramses.gmm import GMM
except ImportError:
    GMM = None 

def entrena(dirPrm, dirMar, lisUni, ficMod, *ficGui, ClsMod=Gauss, nmix=1, iteraciones=1):
    """
    Entrena el modelo acústico con soporte para iteraciones EM (GMM)
    """
    print(f"--- Iniciando Entrenamiento ({ClsMod.__name__}) ---")
    if ClsMod.__name__ == 'GMM':
        print(f"    Configuración: {nmix} gaussianas, {iteraciones} iteraciones.")

    # 1. Cargar datos en memoria (Cache) para acelerar las iteraciones
    print(">> Cargando datos de entrenamiento en memoria...")
    datos_cache = []
    
    lista_ficheros = leeLis(*ficGui)
    
    for señal in tqdm(lista_ficheros): 
        # leemos señal y marca
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)
        pathMar = pathName(dirMar, señal, 'mar')
        unidad = cogeTrn(pathMar)
        
        # Guardamos en la lista
        datos_cache.append((prm, unidad))

    # 2. Inicializamos el modelo
    if ClsMod.__name__ == 'GMM':
        modelo = ClsMod(lisMod=lisUni, nmix=nmix)
    else:
        modelo = ClsMod(lisMod=lisUni)

    # 3. Bucle de Entrenamiento (Iteraciones EM)
    for i in range(iteraciones):
        if iteraciones > 1:
            # Barra de progreso opcional o print simple
            pass 
        
        # a. Inicializar acumuladores (Paso previo al E)
        modelo.inicMod()

        # b. Acumular estadísticas (Paso E) usando memoria
        for prm, unidad in datos_cache:
            modelo += prm, unidad

        # c. Recalcular parámetros (Paso M)
        modelo.calcMod()

    # 4. Escribimos el modelo resultante
    print(f">> Guardando modelo en {ficMod}")
    modelo.escMod(ficMod)   

if __name__ == "__main__":
    from docopt import docopt
    
    usage=f"""
Entrena un modelo acústico para el reconocimento de las vocales

usage:
    {sys.argv[0]} [options] <guia> ...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

options:
    -p, --dirPrm PATH   Directorio con las señales parametrizadas [default: .]
    -m, --dirMar PATH   Directorio con el contenido del fonético de las señales [default: .]
    -l, --lisUni PATH   Fichero con la lista de unidades fométicas [default: Lis/vocales.lis]
    -M, --ficMod PATH   Fichero con el modelo resultante [default: Mod/vocales.mod]
    -e, --execPrev SCRIPT  script de ejecución previa 
    -C, --classMod CLASS   Clase que implementa el modelado acústico (Gauss, GMM) [default: Gauss]
    --nmix INT             Número de gaussianas (solo para GMM) [default: 1]
    --iter INT             Número de iteraciones EM (solo para GMM) [default: 10]
    """
    
    args = docopt(usage, version="tecparla2025")
    dirPrm = args["--dirPrm"]
    dirMar = args["--dirMar"]
    lisUni = args["--lisUni"]
    ficMod = args["--ficMod"]
    ficGui = args["<guia>"]
    
    # Gestionar argumentos opcionales con defaults seguros
    nmix = int(args["--nmix"]) if args["--nmix"] else 1
    iteraciones = int(args["--iter"]) if args["--iter"] else 10

    if args["--execPrev"]: exec(open(args["--execPrev"]).read())
    
    cls_name = args["--classMod"]
    
    # Lógica de selección de clase
    if cls_name == 'GMM':
        if GMM is None:
            sys.exit("Error Crítico: No se encuentra ramses/gmm.py o tiene errores.")
        clsMod = GMM
    elif cls_name:
        clsMod = eval(cls_name)
    else:
        clsMod = Gauss
    
    # Optimización: 1 iteración si no es GMM
    if cls_name != 'GMM':
        iteraciones = 1

    entrena(dirPrm, dirMar, lisUni, ficMod, *ficGui, ClsMod=clsMod, nmix=nmix, iteraciones=iteraciones)