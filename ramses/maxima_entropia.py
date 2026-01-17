# Archivo: src/maxima_entropia.py
import numpy as np
from scipy.fft import fft
from scipy.linalg import toeplitz, inv
from scipy.signal import lfilter

def maximaEntropia(x, orden):
    """
    Implementación del estimador espectral de Máxima Entropía
    basado en la predicción lineal (Yule-Walker).
    """
    N = len(x)
    
    # 1. Calcular autocorrelación (Rxx) y vector de proyección (Prs)
    # Según apuntes: usamos correlate mode='full'
    corr = np.correlate(x, x, mode='full')[N - 1 : N + orden]
    
    Rxx = toeplitz(corr[: -1]) # Matriz de Toeplitz
    Prs = corr[1: ]            # Vector de proyección
    
    # 2. Obtener coeficientes del predictor óptimo (ak = Rxx^-1 * Prs)
    hlp = inv(Rxx) @ Prs
    
    # 3. Construir filtro reconstructor (Hre)
    # Denominador = 1 seguido de -ak
    nume = [1]
    deno = np.concatenate(([1], -hlp))
    
    # 4. Respuesta impulsional del filtro reconstructor
    delta = np.zeros(N)
    delta[0] = 1
    hrec = lfilter(nume, deno, delta)
    
    # 5. Ajuste de potencia (sigma_x / sigma_hrec)
    hrec *= np.std(x) / np.std(hrec)
    
    # 6. Estimación del espectro: |FFT(hrec)|^2
    return np.abs(fft(hrec)) ** 2