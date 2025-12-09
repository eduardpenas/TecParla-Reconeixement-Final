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
<<<<<<< HEAD
            fpRec.write(f'LBO:,,,{reconocida}\n') 


#################################################################################
# Invocación en línea de comandos
#################################################################################
if __name__ == '__main__':
    from docopt import docopt
    import sys
    Sinopsis = f"""
Reconoce una base de datos de señales parametrizadas

Usage:
    {sys.argv[0]} [options] <guiSen>...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

Opciones:
    -r PATH, --dirRec=PATH  Directorio con los ficheros del resultado [default: .]
    -p PATH, --dirPrm=PATH  Directorio con las señales parametrizadas [default: .]
    -m FILE, --ficMod=FILE  Fichero con los modelos acústicos [default: .]
    -l FILE, --lisMod=FILE  Fichero con la lista de unidades a reconocer

Argumentos:
    <guiSen>  Nombre del fichero guía con los nombres de las señales a reconocer.
              Pueden especificarse tantos ficheros guía como sea necesario.
"""
    args = docopt(Sinopsis, version=f'{sys.argv[0]}: Ramses v3.4 (2020)')
    dirRec = args['--dirRec']
    dirPrm = args['--dirPrm']
    ficMod = args['--ficMod']
    guiSen = args['<guiSen>']
    reconoce(dirRec, dirPrm, ficMod, *guiSen)  
=======
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



    
>>>>>>> 4b315c583d5d7a36b62f8a7b8834dc5e479ff2a9
