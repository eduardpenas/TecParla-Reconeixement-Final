from util import *
from mar import *

def evalua (dirRec, dirMar, *guiSen):
    matCnf = {}
    lisPal = {"a", "e", "i", "o", "u"} 

    for sen in leeLis(*guiSen):
        pathRec = pathName(dirRec, sen, "rec")
        rec = cogeTrn(pathRec)
        pathMar = pathName(dirMar, sen, "mar")
        mar = cogeTrn(pathMar)

        if mar not in matCnf:
            matCnf[mar] = {rec:1}
        elif rec not in matCnf[mar]:
            matCnf[mar][rec] = 1
        else:
            matCnf[mar][rec] += 1

        lisPal |= {mar, rec}
    
    for rec in sorted(lisPal):
        print(f'\t{rec}', end='')
    print()
    for mar in sorted(lisPal):
        print(f'{mar}', end='')
        for rec in sorted(lisPal):
            if mar in matCnf and rec in matCnf[mar]:
                conf = matCnf [mar][rec]
            else:   
                conf = 0
            print(f'\t{conf}',end='')
        print()     
