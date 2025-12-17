#! /usr/bin/env python3

import numpy as np
from tqdm import tqdm

from ramses.util import * 
from ramses.prm import * 


def reconoce(dirRec, dirPrm, ficMod, *guiSen):
    """
    Reconoce la unidad cuyo modelo se ajusta mejor
    """
    modelos = np.load(ficMod, allow_pickle=True).item()

    for señal in tqdm(leeLis(*guiSen), ascii="·|/-\\#"):
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)

        minDist = np.inf 
        for modelo in modelos:
            distancia = sum(abs(prm -modelos[modelo])**2)
            if distancia < minDist:
                minDist = distancia
                reconocida = modelo 

        pathRec = pathName(dirRec, señal, '.rec')
        chkPathName(pathRec)
        with open(pathRec, 'wt') as fpRec: 
            fpRec.write(f'LBO:,,,{reconocida}\n')  

if __name__ == "__main__":
    from docopt import docopt
    import sys

    usage=f"""
Reconoce una base de datos de señales parametrizadas 

usage:
    {sys.argv[0]} [options] <guia> ...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

options:
    -r, --dirRec PATH  Directorio con los ficheros del resultado [default: .]
    -p, --dirPrm PATH  Directorio con las señales parametrizadas [default: .]
    -M, --ficMod PATH  Fichero con el modelo resultante [default: Mod/vocales.mod]
"""
    
    args = docopt(usage, version="tecparla2025")
    dirRec = args["--dirRec"]
    dirPrm = args["--dirPrm"]
    ficMod = args["--ficMod"]
    guiSen = args["<guia>"]
    reconoce(dirRec, dirPrm, ficMod, *guiSen)



    
