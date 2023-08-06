# This code contains functions that enable easy fourier analysis

import numpy as np
from scipy.fftpack import fft, ifft

def get_fft(waveform,fs,sides = "single"):
    
    # Following example at:
    # https://pythonnumericalmethods.berkeley.edu/notebooks/chapter24.04-FFT-in-Python.html
    # Retrieved Feb. 17, 2022

    waveform = np.asarray(waveform)

    # Take the fft
    X = fft(waveform)
    N = len(X)
    frequencies = np.linspace(0,1,N) * fs

    X = X / len(waveform)

    # If computing a single-sided spectrum
    if sides == "single":
        X = 2*X[0:int(fs/2)]
        frequencies = frequencies[0:int(fs/2)]
        

    return X, frequencies
