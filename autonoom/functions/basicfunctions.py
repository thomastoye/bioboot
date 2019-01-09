import numpy as np
from scipy import ndimage as ndi
import urllib
from urllib.request import urlopen
import json
from geographiclib.geodesic import Geodesic


################################
#
#input gray scale image black to white 1280*720
# returns 1D array representing depth
#
################################

def detectShoresFrom3DImage(img):
    img[img < 400] = 65535           # filter out infinity


    #filter out water troug horizon based model can use improvement
    for i in range(450, 719):
        k = 22000 - (i - 450) * 256 / 2.7
        r = img[i, :][img[i, :] < (25000 - (i - 450) * 256 / 2.9)] = 65535

    blur = ndi.gaussian_filter(img, sigma=20)        #filtering out noise
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

    if lidardata < 3000:            #almost colision imediate action needed
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


def topwm(direction, speed,controller=False):
    if controller==False:
        dif = direction * 2.8
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
            left = left - right - 255
            right = -255


    else:
        if speed < -255:
            speed = -255
        elif speed > 255:
            speed = 255

        direction_abs = abs(direction)

        if direction_abs == 1:
            if direction > 0 :
                left = 255
                right = -255
            else:
                left = -255
                right = 255
        else:
            #calculate speed for motor that has to be lowered in speed to turn in specified direction
            speed_abs=abs(speed)
            m_lower_speed = -((speed_abs*2)*direction_abs-speed_abs)

            if direction > 0 :
                left = speed_abs
                right = m_lower_speed
            else:
                left = m_lower_speed
                right = speed_abs

        if speed < 0 :
           left = -left
           right = -right
    return "{\"left\":\"%i\"," %left +"\"right\":\"%i\"}" %right

def readPsController():
    dir = 0
    speed = 0
    return dir, speed

def getcurrentgps():
    data = urllib.request.urlopen('http://172.217.17.67:80').read().decode('utf-8')
    jo = json.load(data)
    return jo


def calcdirection(lat1,lon1,lat2,lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1,lon1,lat2,lon2)
    dir = g['azi1']
    if dir <0:
        dir = dir + 360
    return dir

def calcdistance(lat1,lon1,lat2,lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12']


