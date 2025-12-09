#! /usr/bin/env python3

import numpy as np
from tqdm import tqdm

from ramses.util import *
from ramses.prm import * 
from ramses.mar import * 

def entrena(dirPrm, dirMar, lisUni, ficMod, *ficGui):
    """
    Entrena el modelo acústico
    """
    unidades = leeLis(lisUni)

    # Inicializamos el modelo 
    modelo = {}

    # Inicializamos el entrenamiento 
    total = {unidad : 0 for unidad in unidades}
    numUni = {unidad : 0 for unidad in unidades}

    # Bucle para todas las señales de entrenamiento 
    for señal in tqdm(leeLis(*ficGui)): 
        # leemos la señal y el contenido del fichero de marcas
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)
        pathMar = pathName(dirMar, señal, 'mar')
        unidad =cogeTrn(pathMar)

        #Actualizamos la información del entrenamiento 
        total[unidad] += prm
        numUni[unidad] +=1 

    # Recalculamos el modelo 
    for unidad in unidades:
        modelo[unidad] = total[unidad] / numUni[unidad]

    # Escribimos el modelo representante
    chkPathName(ficMod)
    with open(ficMod, 'wb') as fpMod: 
        np.save(fpMod,modelo)    

if __name__ == "__main__":
    from docopt import docopt
    import sys

    usage=f"""
Entrena un modelo acústico para el reconocimento de las vocales

usage:
    {sys.argv[0]} [options] <guia> ...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

options:
    -p, --dirPrm PATH  Directorio con las señales parametrizadas [default: .]
    -m, --dirMar PATH  Directorio con el contenido del fonético de las señales [default: .]
    -l, --lisUni PATH  Fichero con la lista de unidades fométicas [default: Lis/vocales.lis]
    -M, --ficMod PATH  Fichero con el modelo resultante [default: Mod/vocales.mod]
"""
    
    args = docopt(usage, version="tecparla2025")
    dirPrm = args["--dirPrm"]
    dirMar = args["--dirMar"]
    lisUni = args["--lisUni"]
    ficMod = args["--ficMod"]
    ficGui = args["<guia>"]
    entrena(dirPrm, dirMar, lisUni, ficMod, *ficGui)



