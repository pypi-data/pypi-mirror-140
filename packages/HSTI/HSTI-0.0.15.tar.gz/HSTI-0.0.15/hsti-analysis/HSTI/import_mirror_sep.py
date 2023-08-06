import numpy as np
import os

def form_mirror_sep_axis(path):

    impath = path + 'images/capture/'
    number_of_bands = sum([ '.ppm' in s for s in os.listdir(impath)])
    t = np.arange(0,number_of_bands,1)

    p = np.poly1d(np.load(path + 'mirror_sep.npy'))
    mirror_sep = p(t)
    return mirror_sep*1e-6

def form_mirror_sep_axis_direct(path, number_of_bands):

    t = np.arange(0,number_of_bands,1)

    p = np.poly1d(np.load(path))
    mirror_sep = p(t)
    return mirror_sep*1e-6
