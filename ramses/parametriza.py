import soundfile as sf
import numpy as np
from util import *
from prm import *

def parametriza(dirPrm, dirSen, *guiSen):
    for nomSen in leeLis(*guiSen):
        pathSen = pathName(dirSen, nomSen, "wav")
        sen, fm = sf.read(pathSen)

        prm = np.array(sen)

        pathPrm = pathName(dirPrm, nomSen, "prm")
        chkPathName(pathPrm)
        escrPrm(pathPrm, prm)
