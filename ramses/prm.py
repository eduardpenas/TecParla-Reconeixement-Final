#! /usr/bin/env python3

import numpy as np 

def escrPrm(pathPrm, prm):
    """
    Escribe la señal parametrizada
    """
    with open(pathPrm, 'wb') as fpPrm:
        np.save(fpPrm,prm)


def leePrm(pathPrm): 
    """
    Devuelve señal parametrizada
    """
    with open(pathPrm, 'rb') as fpPrm:
        return np.load(fpPrm)
    


    
