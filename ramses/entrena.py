import numpy as np
from util import *
from prm import *
from mar import *

def entrena(dirPrm, dirMar, lisUni, ficMod, *ficGui):
    unidades = leeLis(lisUni)

    # Inicializamos el modelo
    modelo = {}

    # Inicializamos el entrenamiento
    total = {unidad : 0 for unidad in unidades}
    numUni = {unidad : 0 for unidad in unidades}

    # Bucle para todas las señales de entrenamiento
    for señal in leeLis(*ficGui):
        # Leemos la señal y el contenido del fichero de marcas
        pathPrm = pathName(dirPrm, señal, 'prm')
        prm = leePrm(pathPrm)
        pathMar = pathName(dirMar, señal, 'mar')
        unidad = cogeTrn(pathMar)

        # Actualizamos la información del entrenamiento
        total[unidad] += prm
        numUni[unidad] += 1

    # Recalculamos el modelo
    for unidad in unidades:
        modelo[unidad] = total[unidad]/numUni[unidad]

    # Escribimos el modelo resultante
    chkPathName(ficMod)
    with open (ficMod, "wb") as fpMod:
        np.save(fpMod, modelo)
