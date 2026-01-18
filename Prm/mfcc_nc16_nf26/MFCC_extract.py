import numpy as np
from python_speech_features import mfcc
numcep=16
nfilt=26
def get_mfcc(x):
    # fs=8000 es el estandar de la base de datos TecParla
    # winlen=0.025 (25ms), winstep=0.01 (10ms)
    feat = mfcc(x, samplerate=8000, winlen=0.025, winstep=0.01, numcep=numcep, nfilt=nfilt)
    # IMPORTANTE: Ramses espera un vector por vocal, hacemos la media de los tramos
    return np.mean(feat, axis=0)
