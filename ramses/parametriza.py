import soundfile as sf
import numpy as np 

from util import * 
from prm import *

def parametriza(dirPrm, dirSen, *guiSen):
    """
    Lee las señales indicadas por 'dirSen', 'guiSen' y 'extSen', y escribe la señal
    parametrizada en el directorio 'dirPrm'.
    En la versión trivial, la señal parametrizada es igual a la señal temporal.
    """
    for nomSen in leeLis(*guiSen):
        pathSen = pathName(dirSen, nomSen, "wav")
        sen, fm = sf.read(pathSen)
        prm = np.array(sen)
        pathPrm = pathName(dirPrm, nomSen, ".prm")
        chkPathName(pathPrm)
        escrPrm(pathPrm, prm)



