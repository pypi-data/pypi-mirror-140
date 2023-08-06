import cv2 as cv
import numpy as np
import os

def import_data_cube(path):
    """
    ########## HSTI_import ##########
    This function takes an HSTI numpy array and exports it as individual .ppm
    images to a folder given by folder_name.
    """

    impath = path + '/images/capture/'

    try:
        number_of_image_files = sum([ '.ppm' in s for s in os.listdir(impath)])

        steps = np.linspace(0,number_of_image_files*10-10,number_of_image_files)

        imgs = np.zeros((768,1024,len(steps)))

        for idx,i in enumerate(steps):
            imgs[:,:,idx] = cv.imread(impath+'step'+str(int(i)) + '.ppm',cv.IMREAD_ANYDEPTH)
        imgs = np.rot90(imgs,1)

        print('Hyperspectral image shape:')
        print(imgs.shape)

    except:
        print('Path should be directory containing the \'images\' directory.')

    return imgs

def import_image_acquisition_settings(path):

    f = open(path + "/output.txt", "r")
    i = 0
    line = []
    for x in f:
        if len(x.split(' ')) > 10:
            line = i
            break
        i += 1

    values  = np.loadtxt(path + '/output.txt',skiprows=line)

    sens_T      = np.round((np.mean(values[:,6])/1000),2)
    sens_T_bit  = np.round((np.mean(values[:,7])+np.mean(values[:,8])+np.mean(values[:,9]))/3000*-165.2+332.8,2)
    GSK         = np.mean(values[:,10])
    GFID        = np.mean(values[:,11])
    Gain        = np.mean(values[:,12])

    print('Sensor temperature: '+ str(sens_T))
    print('Sensor temperature bit: '+ str(sens_T_bit))
    print('GSK: ' + str(int(GSK)))
    print('GFID: ' + str(int(GFID)))
    print('Gain: ' + str(Gain))

    valdict = {
      'SENS_T': sens_T,
      'SENS_T_bit': sens_T_bit,
      'GSK': GSK,
      'GFID': GFID,
      'GAIN': Gain
    }

    return valdict
