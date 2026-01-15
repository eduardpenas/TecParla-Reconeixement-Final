#! /usr/bin/env python3

import numpy as np
from tqdm import tqdm
import sys

from ramses.util import *
from ramses.prm import *
from ramses.mod import *
from ramses.euclidio import Euclidio
from ramses.gaussiano import Gauss

def reconoce(dirRec, dirPrm, ficMod, *guiSen, ClsMod=Gauss):
    """
    Reconoce la unidad cuyo modelo se ajusta mejor.
    Usa la clase ClsMod para instanciar el modelo.
    """
    # CORRECCIÓN 1: Usamos ClsMod para permitir diferentes tipos de modelos
    try:
        modelo = ClsMod(pathMod=ficMod)
    except ValueError as e:
        print(f"\nERROR CRÍTICO: El modelo en '{ficMod}' está corrupto (contiene NaNs o Infs).")
        print("Asegúrate de haber corregido el log(0) en la parametrización y haber re-entrenado.")
        sys.exit(1)

    for señal in tqdm(leeLis(*guiSen), ascii="·|/-\\#"):
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)

        # El objeto modelo es "callable" (se puede llamar como una función)
        reconocida = modelo(prm)

        pathRec = pathName(dirRec, señal, '.rec')
        chkPathName(pathRec)
        with open(pathRec, 'wt') as fpRec: 
            fpRec.write(f'LBO:,,,{reconocida}\n')  

if __name__ == "__main__":
    from docopt import docopt

    usage=f"""
Reconoce una base de datos de señales parametrizadas 

usage:
    {sys.argv[0]} [options] <guia> ...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

options:
    -r, --dirRec PATH      Directorio con los ficheros del resultado [default: .]
    -p, --dirPrm PATH      Directorio con las señales parametrizadas [default: .]
    -M, --ficMod PATH      Fichero con el modelo resultante [default: Mod/vocales.mod]
    -e, --execPrev SCRIPT  script de ejecución previa 
    -C, --classMod CLASS   Clase que implementa el modelado acústico [default: Gauss]
"""
    
    args = docopt(usage, version="tecparla 2025")
    dirRec = args["--dirRec"]
    dirPrm = args["--dirPrm"]
    ficMod = args["--ficMod"]
    guiSen = args["<guia>"]
    
    if args["--execPrev"]: 
        exec(open(args["--execPrev"]).read())
    
    # CORRECCIÓN 2: Lógica correcta para seleccionar la clase del modelo
    # Si el usuario no pone nada, usamos 'Gauss' por defecto.
    className = args["--classMod"] if args["--classMod"] else "Gauss"
    clsMod = eval(className)
    
    reconoce(dirRec, dirPrm, ficMod, *guiSen, ClsMod=clsMod)