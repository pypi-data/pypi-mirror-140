# AcousticsPy

Welcome to the README file for `AcousticsPy`! This Python package contains many useful calculations for general acoustics use.

## Install

Installation is easy with `pip`:

```
$ pip install acousticspy
```

## Import

```
>>> import acousticspy as ap
```

## Getting Your Feet Wet

Here are some example functions that you can use:

```
>>> import acousticspy as ap
>>> ap.add_decibels([100,100])
103.01029995663981
>>> ap.dB_to_pressure(85,reference = 20e-6)
0.3556558820077846
>>> import numpy as np
>>> x = np.random.rand(100000)
>>> ap.get_oaspl(x) # Will vary slightly based on randomness of x
93.98937215182764
```

## Things That Are Planned to Be Included

This package is designed to provide a suite of acoustics-related calculations based on the courses taken as a graduate student in acoustics (physics) at Brigham Young University. Future topics that are planned for incorporation into this package are:

* Easy FFT Analysis
* Sound Power Calculations
* Fractional Octave Spectra
* Room Mode Calculations
* Impedance Translation
* Reflection and Transmission
