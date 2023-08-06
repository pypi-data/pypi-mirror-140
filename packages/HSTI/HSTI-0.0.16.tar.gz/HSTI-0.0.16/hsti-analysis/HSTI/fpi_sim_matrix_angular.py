import numpy as np
from IPython.display import clear_output
import concurrent.futures as cf

def fpi_trans_single_mirror_sep(m_sep, wavelength, temp, mirror_sep_diff, layer_t, fractions, angles, stack_refractive_index):
    transmittance_vec = np.zeros_like(wavelength)
    for idx, wvl in enumerate(wavelength):
        for m_diff, frac in zip(mirror_sep_diff, fractions):
            layer_t[3] = m_sep + m_diff
            T = transfer_FPI(stack_refractive_index[idx,:], layer_t, wvl, angles[idx,:])
            transmittance_vec[idx] += frac * abs(1/T[0,0])**2
    return transmittance_vec

def mirror_dist_diff(r, R):
    return -2* ( 0.5*(2*R - np.sqrt(4*R**2 - (2*r)**2)) )

def FPI_trans_matrix_ang(mirror_sep, lam, temperature, angle_in_deg):
    lam0 = 10.5e-6 #Central wavelength used for layer thicknesses
    diameter = 40e-3 #mirror diameter
    h_max = 150e-9 #Maximum height difference between mirror center and edges
    R = h_max/2 + (diameter**2)/(8*h_max) #radius of mirror curvature
    n_points = 9 #number of descrete, different mirror separations across the mirror due to curvature

    r_area = np.linspace(0,diameter/2,n_points) #radii used for area calculations
    r_eval = r_area + np.diff(r_area)[0]/2 #radii at which the mirror separation difference is calculated
    r_area = np.delete(r_area, 0)
    r_eval = np.delete(r_eval, -1)
    area = []
    sep_diff = []
    for i in range(n_points-1):
        sep_diff.append(mirror_dist_diff(r_eval[i],R))
        if i == 0:
            area.append(np.pi*r_area[i]**2)
        else:
            area.append(np.pi*(r_area[i]**2-r_area[i-1]**2))
    total_area = sum(area)
    fraction = area/total_area

    phys_layer_thick = np.array([0.5*lam0/refrac_Ge(lam0, temperature), 0.25*lam0/refrac_ThF4(lam0),  0.25*lam0/refrac_Ge(lam0, temperature), 0, 0.25*lam0/refrac_Ge(lam0, temperature), 0.25*lam0/refrac_ThF4(lam0), 0.5*lam0/refrac_Ge(lam0, temperature)])
    transmittance = np.zeros([len(mirror_sep), len(lam)])
    n_ThF4 = refrac_ThF4(lam)
    n_ZnSe = refrac_ZnSe(lam)
    n_Ge = refrac_Ge(lam, temperature)
    n_air = np.ones_like(lam)*1.0002726# air refractive index
    stack_refractive_index = [n_Ge, n_ThF4, n_Ge, n_air, n_Ge, n_ThF4, n_Ge]
    temp = np.concatenate(stack_refractive_index, axis = 0)
    stack_refractive_index = temp.reshape((len(lam), len(stack_refractive_index)), order = 'F')

    ang_lst = np.zeros([len(lam), stack_refractive_index.shape[1] + 4])
    temp = np.deg2rad(angle_in_deg)
    ang_lst[:,(0,-1)] = np.tile(np.deg2rad(angle_in_deg),(2,1)).T
    ang_lst[:,(1,-2)] = np.tile(np.arcsin(n_air*np.sin(ang_lst[:,0])/n_ZnSe),(2,1)).T
    ang_lst[:,(2,-3)] = np.tile(np.arcsin(n_ZnSe*np.sin(ang_lst[:,1])/stack_refractive_index[:,0]),(2,1)).T
    for i in range((stack_refractive_index.shape[1]-1)//2):
        ang_lst[:,(i+3, -(i+4))] = np.tile(np.arcsin(stack_refractive_index[:,i]*np.sin(ang_lst[:,i+2])/stack_refractive_index[:,i+1]),(2,1)).T #For the middle layer i+3 and (-(i+4)) will reference the same element, but this is no problem

    lam_lst, temperature_lst, diff_lst, layer_thickness_lst, fraction_lst, ang_lst_lst = [], [], [], [], [], []
    refractive_index_lst = []
    for i in range(len(mirror_sep)):
        lam_lst.append(lam)
        temperature_lst.append(temperature)
        diff_lst.append(sep_diff)
        layer_thickness_lst.append(phys_layer_thick)
        fraction_lst.append(fraction)
        ang_lst_lst.append(ang_lst)
        refractive_index_lst.append(stack_refractive_index)

    with cf.ProcessPoolExecutor() as executor:
        results = executor.map(fpi_trans_single_mirror_sep, mirror_sep, lam_lst, temperature_lst, diff_lst, layer_thickness_lst, fraction_lst, ang_lst_lst, refractive_index_lst)

    for i, result in enumerate(results):
        transmittance[i,:] = result

    return transmittance


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

def refrac_Ge(lam, temperature):
    # Handbook of Optical Constants of Solids I, page 465
    lam = lam * 1e6
    A = -6.04e-3 * temperature + 11.05128
    B = 9.295e-3 * temperature + 4.00536
    C = -5.392e-4 * temperature + 0.599034
    D = 4.151e-4 * temperature + 0.09145
    E = 1.51408 * temperature + 3426.5
    n = np.sqrt(A + (B * lam**2) / (lam**2 - C) + (D * lam**2) / (lam**2 - E))
    return n

def transfer_FPI(n, d, lam, list_of_angles):
    T_s = interface_s(refrac_ZnSe(lam), n[0], list_of_angles[1], list_of_angles[2]) @ ac_phase(n[0], d[0], lam, list_of_angles[2])
    for i in np.arange(1, len(n), 1):
        T_s = T_s @ interface_s(n[i-1], n[i], list_of_angles[i+1], list_of_angles[i+2]) @ ac_phase(n[i], d[i], lam, list_of_angles[i+2])
    T_s = T_s @ interface_s(n[-1], refrac_ZnSe(lam), list_of_angles[-3], list_of_angles[-2])
    T_p = interface_p(refrac_ZnSe(lam), n[0], list_of_angles[1], list_of_angles[2]) @ ac_phase(n[0], d[0], lam, list_of_angles[2])
    for i in np.arange(1, len(n), 1):
        T_p = T_p @ interface_p(n[i-1], n[i], list_of_angles[i+1], list_of_angles[i+2]) @ ac_phase(n[i], d[i], lam, list_of_angles[i+2])
    T_p = T_p @ interface_p(n[-1], refrac_ZnSe(lam), list_of_angles[-3], list_of_angles[-2])
    T = 0.5*(T_s + T_p)
    return T

def interface_s(n1, n2, angle1, angle2):
    #n1 is refractive index of leftmost film, while n2 is refracive index of rightmost film
    r_right_s = (n1*np.cos(angle1) - n2*np.cos(angle2))/(n1*np.cos(angle1) + n2*np.cos(angle2))
    r_left_s = (n2*np.cos(angle2) - n1*np.cos(angle1))/(n2*np.cos(angle2) + n1*np.cos(angle1))

    t_right_s = 2*n1*np.cos(angle1)/(n1*np.cos(angle1) + n2*np.cos(angle2))
    t_left_s = 2*n2*np.cos(angle2)/(n2*np.cos(angle2) + n1*np.cos(angle1))

    D = np.ones([2,2])
    D[0, 0] = 1
    D[0, 1] = -r_left_s
    D[1, 0] = r_right_s
    D[1, 1] = t_right_s*t_left_s - r_right_s*r_left_s
    D = D / t_right_s
    return D

def interface_p(n1, n2, angle1, angle2):
    #n1 is refractive index of leftmost film, while n2 is refracive index of rightmost film

    r_right_p = (n2*np.cos(angle1) - n1*np.cos(angle2))/(n2*np.cos(angle1) + n1*np.cos(angle2))
    r_left_p = (n1*np.cos(angle2) - n2*np.cos(angle1))/(n1*np.cos(angle2) + n2*np.cos(angle1))

    t_right_p = 2*n1*np.cos(angle1)/(n2*np.cos(angle1) + n1*np.cos(angle2))
    t_left_p = 2*n2*np.cos(angle2)/(n1*np.cos(angle2) + n2*np.cos(angle1))

    D = np.ones([2,2])
    D[0, 0] = 1
    D[0, 1] = -r_left_p
    D[1, 0] = r_right_p
    D[1, 1] = t_right_p*t_left_p - r_right_p*r_left_p
    D = D / t_right_p
    return D

def ac_phase(n, d, lam, angle):
    delta = 2*np.pi*n*d*np.cos(angle)/lam
    P = np.array([[0+0j,0+0j], [0+0j,0+0j]])
    P[0,0] = np.exp(1j * delta)
    P[1, 1] = np.exp(-1j * delta)
    return P
