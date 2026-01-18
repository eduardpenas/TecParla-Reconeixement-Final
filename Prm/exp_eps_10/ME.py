import numpy as np
from maxima_entropia import maximaEntropia
orden=8
eps=10
def ME(x):
    return np.log(eps + maximaEntropia(x, orden))
