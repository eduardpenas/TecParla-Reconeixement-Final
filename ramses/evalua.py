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
            total += matCnf[mar][rec] if mar in matCnf and rec in matCnf[mar] else 0
            if mar == rec:
                cor += matCnf[mar][rec] if mar in matCnf and rec in matCnf[mar] else 0
    print(f'exact = {cor/total:.2%}')

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

    




