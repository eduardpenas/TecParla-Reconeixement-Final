import numpy as np
from ramses.mod import Modelo
from ramses.util import *
from scipy.stats import multivariate_normal

class Gauss(Modelo):
    def leeMod(self, pathMod):
        with open(pathMod, 'rb') as fpMod:
            self.media=np.load(fpMod, allow_pickle=True).item()
            self.var=np.load(fpMod, allow_pickle=True).item()
        self.unidades = self.media.keys()
        self.gauss = {}
        for unidad in self.unidades:
            self.gauss[unidad] = multivariate_normal(mean=self.media[unidad], cov=self.var[unidad], allow_singular=True)

    def escMod(self, pathMod):
        chkPathName(pathMod)
        with open(pathMod, 'wb') as fpMod:
            np.save(fpMod, self.media)
            np.save(fpMod, self.var)

    def inicMod(self):
        self.total={unidad:0 for unidad in self.unidades}
        self.total2={unidad:0 for unidad in self.unidades}
        self.numSen={unidad:0 for unidad in self.unidades}

    def __add__(self, prm_unidad):
        prm, unidad = prm_unidad
        self.total[unidad] += prm
        self.total2[unidad] += prm**2
        self.numSen[unidad] += 1
        return self
    
    def calcMod(self):
        self.media = {}
        self.var = {}
        for unidad in self.unidades:
            self.media[unidad] = self.total[unidad]/self.numSen[unidad]
            self.var[unidad] = self.total2[unidad]/self.numSen[unidad] - self.media[unidad]**2

    def __call__(self,prm):
        pdfMax = -np.inf
        for unidad in self.unidades:
            pdf = self.gauss[unidad].logpdf(prm)
            if pdf > pdfMax:
                pdfMax = pdf
                reconocida = unidad
        return reconocida
