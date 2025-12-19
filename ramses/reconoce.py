#! /usr/bin/env python3

import numpy as np
from tqdm import tqdm

from ramses.util import * 
from ramses.prm import * 
from ramses.mod import *
from ramses.euclidio import Euclidio
from ramses.gaussiano import Gauss


def reconoce(dirRec, dirPrm, ficMod, *guiSen, ClsMod=Gauss):
    """
    Reconoce la unidad cuyo modelo se ajusta mejor
    """
    modelo = Gauss(pathMod=ficMod)

    for señal in tqdm(leeLis(*guiSen), ascii="·|/-\\#"):
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)

        reconocida = modelo (prm)

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
    -e, --execPrev SCRIPT  script de ejecución previa 
    -C, --classMod CLASS  Clase que implementa el modelado acústico
"""
    
    args = docopt(usage, version="tecparla2025")
    dirRec = args["--dirRec"]
    dirPrm = args["--dirPrm"]
    ficMod = args["--ficMod"]
    guiSen = args["<guia>"]
    if args["--execPrev"]: exec(open(args["--execPrev"]).read())
    clsMod = eval(args["--classMod"]) if args ["--classMod"] in args else Modelo
    reconoce(dirRec, dirPrm, ficMod, *guiSen, ClsMod=clsMod)



    
