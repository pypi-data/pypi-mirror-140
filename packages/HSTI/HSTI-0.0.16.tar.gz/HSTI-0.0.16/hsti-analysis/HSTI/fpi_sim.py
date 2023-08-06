import numpy as np

def FPI_trans(mirror_sep,lam, temp):
    lam0 = 10.5e-6
    layer_thickness = np.array([0.5*lam0/refrac_Ge(lam0, temp), 0.25*lam0/refrac_ThF4(lam0),  0.25*lam0/refrac_Ge(lam0, temp), mirror_sep, 0.25*lam0/refrac_Ge(lam0, temp), 0.25*lam0/refrac_ThF4(lam0), 0.5*lam0/refrac_Ge(lam0, temp)])
    #layer_thickness = np.array([0.5*lam0/refrac_Ge(lam0, temp), 1682e-9,  0.25*lam0/refrac_Ge(lam0, temp), mirror_sep, 0.25*lam0/refrac_Ge(lam0, temp), 1682e-9, 0.5*lam0/refrac_Ge(lam0, temp)])
    stack_refractive_index = np.array([refrac_Ge(lam, temp), refrac_ThF4(lam), refrac_Ge(lam, temp), 1, refrac_Ge(lam, temp), refrac_ThF4(lam), refrac_Ge(lam, temp)])
    T = transfer_FPI(stack_refractive_index, layer_thickness, lam)
    reflectance = np.abs(T[1,0]/T[0,0])**2
    transmittance = abs(1/T[0,0])**2

    loss = 1 - transmittance - reflectance
    return transmittance, reflectance, loss

def refrac_ThF4(lam):
    # Handbook of Optical Constants of Solids II, 1998, page 1051
    lam = lam * 1e6
    n = 1.118 + 2.46 / lam - 2.98 / (lam**2)
    return n

def refrac_ZnSe(lam):
    # Handbook of Optical Constants of Solids II, page 737
    lam = lam * 1e6
    n = np.sqrt(4 + 1.9*lam**2/(lam**2 - 0.113))
    return n

def refrac_Ge(lam, temp):
    # Handbook of Optical Constants of Solids I, page 465
    lam = lam * 1e6
    A = -6.04e-3 * temp + 11.05128
    B = 9.295e-3 * temp + 4.00536
    C = -5.392e-4 * temp + 0.599034
    D = 4.151e-4 * temp + 0.09145
    E = 1.51408 * temp + 3426.5
    n = np.sqrt(A + (B * lam**2) / (lam**2 - C) + (D * lam**2) / (lam**2 - E))
    return n

def transfer_FPI(n, d, lam):
    T = interface(refrac_ZnSe(lam), n[0]) @ ac_phase(n[0], d[0], lam)
    for i in np.arange(1, len(n), 1):
        T = T @ interface(n[i-1], n[i]) @ ac_phase(n[i], d[i], lam)
    T = T @ interface(n[-1], refrac_ZnSe(lam))
    return T

def interface(n1, n2):
    #n1 is refractive index of leftmost film, while n2 is refracive index of rightmost film
    D = np.ones([2,2])
    D[0, 0] = 1 + n2 / n1
    D[0, 1] = 1 - n2 / n1
    D[1, 0] = 1 - n2 / n1
    D[1, 1] = 1 + n2 / n1
    D = 0.5 * D
    return D

def ac_phase(n, d, lam):
    P = np.array([[0+0j,0+0j], [0+0j,0+0j]])
    P[0,0] = np.exp(1j * n * 2 * np.pi * d / lam)
    P[1, 1] = np.exp(-1j * n * 2 * np.pi * d / lam)
    return P
