import numpy as np
import os
import concurrent.futures as cf

def save_img(img, path):
    with open(path, 'a') as f:
        f.write(f'P3 {img.shape[1]} {img.shape[0]} 255\n')
        for j in range(img.shape[0]):
            for k in range(img.shape[1]):
                f.write(f'{img[j,k]} {img[j,k]} {img[j,k]}\n')
        f.close()

def export_data_cube(data_cube, folder_name):
    """
    ########## HSTI_export ##########
    This function takes an HSTI numpy array and exports it as individual .ppm
    images to a folder given by folder_name.
    """

    os.mkdir(os.getcwd() + '/' + folder_name)
    os.mkdir(os.getcwd() + '/' + folder_name + '/images')
    os.mkdir(os.getcwd() + '/' + folder_name + '/images/capture')
    path = os.getcwd() + '/' + folder_name + '/images/capture'
    data_cube = np.rot90(data_cube, 3)
    img_size = [data_cube.shape[0], data_cube.shape[1]]
    NoB = data_cube.shape[2]

    data_cube_16bit = (65535.9*(data_cube - np.min(data_cube))/(np.max(data_cube) - np.min(data_cube))).astype(np.uint16)

    img_lst, path_lst = [], []
    for i in range(NoB):
        img_lst.append(data_cube_16bit[:,:,i])
        step = i*10
        path_lst.append(f'{path}/step{step}.ppm')

    with cf.ProcessPoolExecutor() as executor:
        results = executor.map(save_img, img_lst, path_lst)
