# This contains code to calculate the autospectral density of a signal

import numpy as np
from scipy.fftpack import fft

def autospec(x,fs):

    