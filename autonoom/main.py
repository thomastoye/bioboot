import numpy as np
import sensors.Realsense
#import sensors.Lidar
import functions.basicfunctions
import serial
from time import sleep
import cv2
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import ndimage as ndi
import pyrealsense2 as rs
import json
from geographiclib.geodesic import Geodesic

import bluetooth

automatic = 1

waypoints = [[51.032981, 3.734168],[51.031186, 3.735625],[51.030953, 3.737267],[51.031307, 3.739161]]
waypointp = 0


for i in range(10):
    functions.basicfunctions.getcurrentgps()

while(1):
    if automatic:
        cp = functions.basicfunctions.getcurrentgps()
        if functions.basicfunctions.calcdistance(cp['lan'],cp['lt'],waypoints[waypointp][0],waypoints[waypointp][1]) < 10:
            waypointp = waypointp + 1
        dir = functions.basicfunctions.calcdirection(cp['lan'],cp['lt'],waypoints[waypointp][0],waypoints[waypointp][1])


        rs = sensors.Realsense.RealSense()
        rsv = rs.getRealSenseValue()
        #ldv = sensors.Lidar.Lidar().getLidarValue()
        ldv = np.full(682,5000)
        #dir, speed = functions.basicfunctions.determinedirection(ldv,rsv,0)
        sleep(0.1)
    #        ser.write(functions.basicfunctions.topwm(dir,speed))
    else:
        k = 2

