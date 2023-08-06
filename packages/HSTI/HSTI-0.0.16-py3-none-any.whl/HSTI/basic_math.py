import numpy as np
from scipy.ndimage import median_filter
from IPython.display import clear_output
import concurrent.futures as cf


def baseline(data_cube):
    gray_cube = np.mean(data_cube, axis = 2)
    gray_cube = gray_cube[:,:,np.newaxis]
    gray_cube = np.repeat(gray_cube, data_cube.shape[2], axis = 2)

    data_cube = data_cube - gray_cube

    return data_cube

def standardize(data_cube):
    std_cube = np.std(data_cube, axis = 2)
    std_cube[std_cube == 0] = 1
    std_cube = std_cube[:,:,np.newaxis]
    std_cube = np.repeat(std_cube, data_cube.shape[2], axis = 2)
    baselined_cube = baseline(data_cube)

    data_cube = baselined_cube/std_cube

    return data_cube

def normalize_cube(data_cube):
    min_cube = np.min(data_cube, axis = 2)
    min_cube = min_cube[:,:,np.newaxis]
    min_cube = np.repeat(min_cube, data_cube.shape[2], axis = 2)

    data_cube = data_cube - min_cube
    data_cube = data_cube/np.max(data_cube)

    return data_cube

def normalize_pixel(data_cube):
    min_cube = np.min(data_cube, axis = 2)
    min_cube = min_cube[:,:,np.newaxis]
    min_cube = np.repeat(min_cube, data_cube.shape[2], axis = 2)

    data_cube = data_cube - min_cube

    max_cube = np.max(data_cube, axis = 2)
    max_cube = max_cube[:,:,np.newaxis]
    max_cube = np.repeat(max_cube, data_cube.shape[2], axis = 2)

    data_cube = data_cube/max_cube

    return data_cube

def sbtrct_first_band(data_cube):
    first_cube = data_cube[:,:,0]
    first_cube = first_cube[:,:,np.newaxis]
    first_cube = np.repeat(first_cube, data_cube.shape[2], axis = 2)

    data_cube = data_cube - first_cube

    return data_cube


def median_filter_cube(data_cube, kernel_size):
    band_lst = []
    for i in range(data_cube.shape[2]):
        band_lst.append(data_cube[:,:,i])
    kernel_size_lst = np.ones(len(band_lst), dtype = int)*kernel_size
    with cf.ThreadPoolExecutor() as executor:
        results = executor.map(median_filter, band_lst, kernel_size_lst)
    filtered_cube = np.zeros_like(data_cube)
    for i, result in enumerate(results):
        filtered_cube[:,:,i] = result
    return filtered_cube

def targeted_median_filter(input_array, px_idx, kernel_size):
    if input_array.shape != px_idx.shape:
        print("Arrays must be the same shape. px_idx must be a true/false numpy array")
        return
    if type(input_array[0,0]) is not np.float64:
         input_array = input_array.astype(float)
    kernel = np.ones([kernel_size*2 + 1, kernel_size*2 + 1], dtype = float)
    kernel[kernel_size, kernel_size] = np.nan
    padded_array = np.pad(input_array, kernel_size, 'constant', constant_values = np.nan)

    for i in range(input_array.shape[0]):
        for j in range(input_array.shape[1]):
            if px_idx[i,j] == True:
                # print(f'i: {i}, j: {j}, previous value: {input_array[i,j]}, new value: {temp}')
                input_array[i,j] = np.nanmedian(padded_array[i:i+2*kernel_size+1,j:j+2*kernel_size+1]*kernel)
    return input_array
