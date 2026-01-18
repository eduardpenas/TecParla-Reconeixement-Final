import numpy as np
from maxima_entropia import maximaEntropia
orden=8
eps=0.1
def ME(x):
    # Aplicamos logaritmo para 'blanquear' la dinamica (dB-ish)
    return np.log(eps + maximaEntropia(x, orden))
