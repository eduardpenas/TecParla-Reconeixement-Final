#! /usr/bin/env python3

from ramses.util import * 
from ramses.mar import * 
from tqdm import tqdm

from ramses.util import *
from ramses.mar import *  
from tqdm import tqdm
def evalua(dirRec, dirMar, *guiSen):
    """
    Calcula la tasa de exactitud en el reconocimiento 
    """
    matCnf = {}
    lisPal = set()
    for sen in tqdm(leeLis(*guiSen)):
        pathRec = pathName(dirRec, sen, '.rec')
        rec = cogeTrn(pathRec)
        pathMar = pathName(dirMar, sen, '.mar')
        mar = cogeTrn(pathMar)
        if not mar in matCnf:
            matCnf[mar] = {rec: 1}
        elif not rec in matCnf[mar]:
            matCnf[mar][rec] = 1
        else:
            matCnf[mar][rec] += 1
        lisPal |= {rec, mar}

    for rec in sorted(lisPal):
        print(f'\t{rec}', end='')
    print()
    for mar in sorted(lisPal):
        print(f'{mar}',end='')
        for rec in sorted(lisPal):
            if mar in matCnf and rec in matCnf[mar]:
                conf = matCnf[mar][rec]
            else : 
                conf = 0
            print(f'\t{conf}',end='')
        print()

    total = cor = 0
    for mar in lisPal:
        for rec in lisPal:
            total += matCnf[mar][rec]
            if mar == rec:
                cor += matCnf[mar][rec]
    print(f'exact = {cor/total:.2%}')

<<<<<<< HEAD
if __name__ == '__main__':
    from docopt import docopt
    import sys
    Sinopsis = f"""
Evalua el resultado de un reconocimiento
Usage:
    {sys.argv[0]} [options] <guiSen>...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

Opciones:
    -r PATH, --dirRec=PATH  Directorio con los ficheros del resultado [default: .]
    -a PATH, --dirMar=PATH  Directorio con los ficheros de marcas [default: .]
Argumentos:
    <guiSen> Nombre del fichero guía con los nombres de las señales reconocidas.
             Pueden especificarse tantos ficheros guía como sea necesario.
Evaluación:
    Siendo OK el número de unidades reconocidas correctamente y KO el de errores,
    el programa saca por pantalla la exactitud calculada como OK / (OK + KO)
"""
    args = docopt(Sinopsis, version=f'{sys.argv[0]}: Ramses v3.4 (2020)')
    dirRec = args['--dirRec']
    dirMar = args['--dirMar']
    guiSen = args['<guiSen>']
    evalua(dirRec, dirMar, *guiSen)
=======
if __name__ == "__main__":
    from docopt import docopt
    import sys

    usage=f"""


usage:
    {sys.argv[0]} [options] <guia> ...
    {sys.argv[0]} -h | --help
    {sys.argv[0]} --version

options:
    -r, --dirRec PATH  Directorio con los ficheros del resultado [default: .]
    -m, --dirMar PATH  Directorio con el contenido del fonético de las señales [default: .]
"""
    
    args = docopt(usage, version="tecparla2025")
    dirRec = args["--dirRec"]
    dirMar = args["--dirMar"]
    guiSen = args["<guia>"]
    evalua(dirRec, dirMar, *guiSen)

    




>>>>>>> 4b315c583d5d7a36b62f8a7b8834dc5e479ff2a9
