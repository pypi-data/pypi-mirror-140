def baffled_circular_piston_directivity(radius,frequency,theta):
    c = 343
    k = 2*np.pi*frequency/c
    return 2*sp.jv(1,k*radius*np.sin(theta)) / (k*radius*np.sin(theta))