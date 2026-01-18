import numpy as np
from maxima_entropia import maximaEntropia
orden=8
eps=0.1
def ME(x):
    # Devolvemos el Logaritmo para blanquear la dinámica
    return np.log(eps + maximaEntropia(x, orden))
