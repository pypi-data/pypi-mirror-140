# This contains code that enables decibel math

import numpy as np

"""
summation = add_decibels(dB, coherent = False)

Take multiple decibel values and add them together. Incoherence is assumed but can be switched to coherence.

Input:
    dB = list or numpy array of decibel values
    coherent = boolean, whether the decibel values are coherent with each other

Output:
    summation = the sum total of the decibel values in the input
"""

def add_decibels(dB,coherent = False):
   
    dB = np.asarray(dB)

    if coherent:
        summation = 20 * np.log10(sum(10**(dB/20)))
    else:
        summation = 10 * np.log10(sum(10**(dB/10)))

    return summation

def dB_to_pressure(dB,reference,squared = True):

    dB = np.asarray(dB)

    if squared:
        value = reference * 10**(dB/20)
    else:
        value = reference * 10**(dB/10)

    return value
