import numpy as np
from scipy import ndimage as ndi


################################
#
#input gray scale image black to white 1280*720
# returns 1D array representing depth
#
################################

def detectShoresFrom3DImage(img):
    img[img < 3] = 255            # filter out infinity


    #filter out water troug horizon based model can use improvement
    for i in range(450, 719):
        k = 100 - (i - 450) * 1 / 2.7
        r = img[i, :][img[i, :] < (100 - (i - 450) * 1 / 3)] = 255

    blur = ndi.gaussian_filter(img, sigma=15)        #filtering out noise
    blurc = blur[400:719, :]                        #removing air

    d2 = np.amin(blurc, axis=0)                     #converting to 1d array

    return d2


