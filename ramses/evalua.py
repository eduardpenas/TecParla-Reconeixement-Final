#! /usr/bin/env python3

from ramses.util import * 
from ramses.mar import * 

def evalua(dirRec, dirMar, *guiSen):
    """
    Calcula la tasa de exactitud en el reconocimiento 
    """
    matCnf = {}
    lisPal = set()
    for sen in leeLis(*guiSen):
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
    print(f'exact = {cor/total}')
