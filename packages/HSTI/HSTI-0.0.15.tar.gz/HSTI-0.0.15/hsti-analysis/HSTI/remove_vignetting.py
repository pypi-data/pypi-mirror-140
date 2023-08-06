import numpy as np
import pkg_resources

def remove_vignette(img_cube):

    #Image must have dimensions 1024x768. This function does not calculate
    #vignette based on the image itself. It asumes that the image is taken using
    #a specific camera and applies a predetermined vignetting correction.
    #This function can both be used on single images as well as entire cubes

    resource_package = __name__
    resource_path = '/'.join(('data_files', 'vignetting_profile.txt'))  # Do not use os.path.join()
    path = pkg_resources.resource_stream(resource_package, resource_path)
    vignette = np.loadtxt(path)

    vignette_cube = np.zeros_like(img_cube)

    if len(img_cube.shape) == 3:
        vignette_cube = vignette
        vignette_cube = vignette_cube[:,:,np.newaxis]
        vignette_cube = np.repeat(vignette_cube, img_cube.shape[2], axis = 2)
        devignetted_cube = img_cube/vignette_cube
    elif len(img_cube.shape) == 2:
        devignetted_cube = img_cube/vignette

    return devignetted_cube
