import numpy as np
from scipy import interpolate
import concurrent.futures as cf

def debend_single_band(selections, img, interp_spec, mirror_sep):
    interp_img = np.zeros_like(img)
    interp_img[selections[0]] = img[selections[0]]
    for i in range(len(selections) - 1):
        interp_img[selections[i+1]] = interp_spec[i+1](mirror_sep)
    return interp_img

def debend(cube, central_mirror_sep):
    N = 100
    f_length = 35e-3 #Focal length
    px_pitch = 17e-6 #Pixel pitch
    p_x = np.arange(cube.shape[1])
    p_y = np.arange(cube.shape[0])
    P_x, P_y = np.meshgrid(p_x, p_y)
    r = np.sqrt(((P_x - 430)**2 + (P_y - 505)**2)*px_pitch**2)
    theta = np.arctan(r/f_length)
    #Fitting parameters for use later
    [a, b] = [-1.24875814e-04,  2.37220232e-05]

    masks = []
    #THETA hold the angles of each boundary between each ring
    THETA = np.linspace(0, np.max(theta), N+1)
    THETA = np.delete(THETA, 0)
    #THETA = 0 is deleted because this will result in a circle with an area of 0
    # The innermost 'ring' is just a circle and this mask is therefore a special case
    masks.append(theta <= THETA[0])
    #The rest of the masks are generated
    for i in range(N-1):
        masks.append((theta > THETA[i]) & (theta <=THETA[i+1]))

    mirror_sep_axes = []
    mirror_sep_axes.append(central_mirror_sep)
    for i in range(N-1):
        correction = central_mirror_sep*(a * np.rad2deg(THETA[i+1])**2 + b * np.rad2deg(THETA[i+1]))
        mirror_sep_axes.append(central_mirror_sep + correction)

    interpolated_cube = np.zeros_like(cube)
    interpolated_spectra = []
    for i in range(N):
        interpolated_spectra.append(interpolate.interp1d(mirror_sep_axes[i], cube[masks[i], :], fill_value = 'extrapolate'))

    mask_lst, img_lst, interp_spec_lst, mirror_sep_lst = [], [], [], []
    for i in range(cube.shape[2]):
        mask_lst.append(masks)
        img_lst.append(cube[:,:,i])
        interp_spec_lst.append(interpolated_spectra)
        mirror_sep_lst.append(mirror_sep_axes[0][i])

    with cf.ThreadPoolExecutor() as executor:
        results = executor.map(debend_single_band, mask_lst, img_lst, interp_spec_lst, mirror_sep_lst)

    debent = np.zeros_like(cube)
    for i, result in enumerate(results):
        debent[:,:,i] = result

    return debent
