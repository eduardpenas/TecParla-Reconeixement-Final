import numpy as np
from util import *

class Modelo:
    def __init__(self, pathMod=None, lisMod=None):
        if pathMod != None:
            self.leeMod(pathMod)
        elif lisMod != None:
            self.unidades=leeLis(lisMod)
        else:
            raise("Hay que indicar el fichero del modelo o la lista de unidades")
    
    def leeMod(self, pathMod):
        pass

    def escMod(self, pathMod):
        pass

    def inicMod(self):
        pass

    def __add__(self, prm):
        return self
    
    def calcMod(self):
        pass

    def __call__(self,prm):
        return np.random.choice(["a", "e", "i", "o", "u"], 1)[0]
