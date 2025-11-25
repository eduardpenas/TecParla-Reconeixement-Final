import numpy as np

from util import *
from prm import *

def reconoce(dirRec, dirPrm, ficMod, *guiSen):
    modelos = np.load(ficMod, allow_pickle=True).item()

    for señal in leeLis(*guiSen):
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)
        minDis = np.inf
        for modelo in modelos:
            distancia = sum(abs(prm - modelos[modelo])**2)
            if distancia < minDis:
                minDis = distancia
                reconocida = modelo
        pathRec = pathName(dirRec, señal, 'rec')
        chkPathName(pathRec)
        with open(pathRec, "wt") as fpRec:
            fpRec.write(f'LBO: ,,,{reconocida}')
