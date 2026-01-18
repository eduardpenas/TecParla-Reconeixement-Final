import numpy as np
from maxima_entropia import maximaEntropia
orden=20
eps=0.1
def ME(x):
    return np.log(eps + maximaEntropia(x, orden))
