#! /usr/bin/env python3

import soundfile as sf
import numpy as np 
from tqdm import tqdm 
from ramses.util import * 
from ramses.prm import *

def parametriza(dirPrm, dirSen, *guiSen):
    """
    Lee las señales indicadas por 'dirSen', 'guiSen' y 'extSen', y escribe la señal
    parametrizada en el directorio 'dirPrm'.
    En la versión trivial, la señal parametrizada es igual a la señal temporal.
    """
    for nomSen in tqdm(leeLis(*guiSen),ascii='·|/-\\#'):
        pathSen = pathName(dirSen, nomSen, "wav")
        sen, fm = sf.read(pathSen)

        prm = np.array(sen)
        
        pathPrm = pathName(dirPrm, nomSen, ".prm")
        chkPathName(pathPrm)
        escrPrm(pathPrm, prm)


if __name__ =='__main__':
        from docopt import docopt
        import sys

        usage= f"""
                    Parametriza una base de datos de señal.
                    Usage:
                    /home/albino/TecParla/apuntes/ramses/parametriza.py [options] <guiSen>...
                    /home/albino/TecParla/apuntes/ramses/parametriza.py -h | --help
                    /home/albino/TecParla/apuntes/ramses/parametriza.py --version
                    Opciones:
                    -s PATH, --dirSen=PATH Directorio con las señales temporales [default: .]
                    -p PATH, --dirPrm=PATH Directorio con las señales parametrizadas [default: .]
                    Argumentos:
                    <guiSen> Nombre del fichero guía con los nombres de las señales a parametrizar.
                    Pueden especificarse tantos ficheros guía como sea necesario.
                    Parametrización trivial:
                    En la versión trivial del sistema, la parametrización simplemente copia la señal
                    temporal en la salida.
                    """
                
        args = docopt(usage, version ='tecparla.2025')
        dirSen =args["--dirSen"]
        dirPrm =args['--dirPrm']
        guiSen =args["<guiSen>"] #lista de cadenas
        parametriza(dirPrm,dirSen,*guiSen)
