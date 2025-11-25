import numpy as np

from util import *
from prm import *

def reconoce(dirRec, dirPrm, ficMod, *guiSen):
    modelos = np.load(ficMod, allow_pickle= True).item()

    for señal in leeLis(*guiSen): 
        pathName = pathName(dirPrm, señal, "prm")
        prm = leePrm(pathPrm)
        minDis = np.inf()
        for modelo in modelos: 
            distancia = 