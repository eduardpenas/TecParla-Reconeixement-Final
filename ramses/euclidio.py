import numpy as np
from ramses.mod import Modelo
from ramses.util import *

class Euclidio(Modelo):
    def __init__(self, pathMod=None, lisMod=None ):
        if pathMod != None:
            self.leeMod(pathMod)
        elif lisMod != None:
            self.unidades = leeLis(lisMod)
            self.media = {unidad:0 for unidad in self.unidades}

        else:
            raise("hay que indicar el fichero con los modelos o la lista de unidades.")
    
    def leeMod(self, pathMod):
        self.media = np.load(pathMod, allow_pickle=True).item()
        self.unidades = self.media.keys()

    def escMod(self, pathMod):
        chkPathName(pathMod)
        with open(pathMod, "wb") as fpMod:
            np.save(fpMod, self.media, allow_pickle=True)

    def inicMod(self):
        self.numUni = {unidad:0 for unidad in self.unidades}
        self.total = {unidad:0 for unidad in self.unidades}

    def __add__(self, prm_unidad):
        prm, unidad = prm_unidad
        self.numUni[unidad] += 1
        self.total[unidad] += prm
        return self
    
    def calcMod(self):
        for unidad in self.unidades:
            self.media[unidad] = self.total[unidad] / self.numUni[unidad]

    def __call__(self,prm):
        distMin = np.inf
        for unidad in self.unidades:
            dist = sum(abs(prm - self.media[unidad])**2)
            if dist < distMin:
                reconocida = unidad
                distMin = dist
        return reconocida