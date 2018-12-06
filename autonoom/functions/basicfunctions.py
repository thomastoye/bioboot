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


#######################################################
#lidardata : array of 682 data points from lidar
#realsensedata : array of 1280 (vb from detectShoresFrom3DImage)
#generaldirection : direction in degrees that boat should go (from GPS and compasdata)
#
#returns direction in degrees and speed value between -255 and +255
########################################################


def determinedirection(lidardata, realsensedata,generaldirection):
    lidardata[lidardata < 1500] = 5500        #everything under 1500 is on boat self

    if rdata < 3000:            #almost colision imediate action needed
        return generaldirection,0

    if generaldirection < -25 | generaldirection > 25:   # turn no navigation possible
        return  generaldirection,0

    realsensedata = realsensedata[140:-140]     # only tihs part is usefull

    dirp = np.argmax(realsensedata)             #max value is best choice
    dirp = dirp -500
    dirp = dirp* 33.28                          # convert to degrees
    return dirp,255


##############################################
# direction in degress
# speed value between -255 en +255
#
#returns json format for motor driver


def topwm(direction, speed):
    dif  = direction *2.8
    left = speed + dif
    right = speed - dif
    if left > 255:
        right = right - left + 255
        left = 255

    if left < -255:
        right = right - left - 255
        left = -255

    if right > 255:
        left = left - right + 255
        right = 255

    if right < -255:
        left = left - rigt - 255
        right = -255

    return "{\"left\":%d,\"right\":%d}"


def readPsController():
    dir = 0
    speed = 0
    return dir, speed


