import numpy as np
from python_speech_features import mfcc
def get_mfcc(x):
    feat = mfcc(x, samplerate=8000, winlen=0.025, winstep=0.01, numcep=18, nfilt=20)
    return feat
