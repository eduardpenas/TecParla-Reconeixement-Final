#! /usr/bin/env python3

import soundfile as sf
import numpy as np 

from ramses.util import * 
from ramses.prm import *
from tqdm import tqdm

def parametriza(dirPrm, dirSen, *guiSen, funkPrm="np.array"):
    """
    Lee las señales indicadas por 'dirSen', 'guiSen' y 'extSen', y escribe la señal
    parametrizada en el directorio 'dirPrm'.
    En la versión trivial, la señal parametrizada es igual a la señal temporal.
    """
    funkPrm = eval(funkPrm)
    for nomSen in tqdm(leeLis(*guiSen), ascii="·|-#"):
        pathSen = pathName(dirSen, nomSen, "wav")
        sen, fm = sf.read(pathSen)

        prm = funkPrm(sen)
        
        pathPrm = pathName(dirPrm, nomSen, ".prm")
        chkPathName(pathPrm)
        escrPrm(pathPrm, prm)

if __name__ == '__main__':
    from docopt import docopt
    import sys

    usage=f"""
        Parametriza una bases de datos de señales de voz

        usage:
            {sys.argv[0]} [options] <guia> ...
            {sys.argv[0]} -h | --help
            {sys.argv[0]} --version

        options:
            -s, --dirSen DIRECTORI  directori de la señal d' entrada [default: .]
            -p, --dirPrm DIRECTORI  directori de la señal parametrizada [default: .]
            -f, --funkPrm PYTHON  función que se usa para parametrizar las señales [default: np.array]
            -e, --execPrev SCRIPT  script de ejecución previa 
        """
    args= docopt(usage, version="tecparla2025")
    dirSen = args["--dirSen"]
    dirPrm = args["--dirPrm"]
    funkPrm = args["--funkPrm"]
    guiSen = args["<guia>"]
    exec(open(args["--execPrev"]).read())
    parametriza(dirPrm, dirSen, *guiSen, funkPrm=funkPrm)

 
