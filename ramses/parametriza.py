#! /usr/bin/env python3

import soundfile as sf
import numpy as np 

from ramses.util import * 
from ramses.prm import *
from tqdm import tqdm

def parametriza(dirPrm, dirSen, *guiSen):
    """
    Lee las señales indicadas por 'dirSen', 'guiSen' y 'extSen', y escribe la señal
    parametrizada en el directorio 'dirPrm'.
    En la versión trivial, la señal parametrizada es igual a la señal temporal.
    """
    for nomSen in tqdm(leeLis(*guiSen)):
        pathSen = pathName(dirSen, nomSen, "wav")
        sen, fm = sf.read(pathSen)

        prm = np.array(sen)
        
        pathPrm = pathName(dirPrm, nomSen, ".prm")
        chkPathName(pathPrm)
        escrPrm(pathPrm, prm)

if __name__ == "__main__":
    from docopt import docopt

    usage="""
        Parametriza una bases de datos de señales de voz

        usage:
            parametriza.py [options] <guia> ...
            parametriza.py -h | --help
            parametriza.py --version

        options:
            -s, --dirSen DIRECTORI  directori de la señal d' entrada [default: .]
            -p, --dirPrm DIRECTORI  directori de la señal parametrizada [default: .]
        """
    args= docopt(usage, version="tecparla2025")
    dirSen = args["--dirSen"]
    dirPrm = args["--dirPrm"]
    guiSen = args["<guia>"]
    parametriza(dirPrm, dirSen, *guiSen)

 