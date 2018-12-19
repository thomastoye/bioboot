import numpy as np
import sensors.Realsense
import sensors.Arduino
#import sensors.Lidar
import  sensors.Phone
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

import subprocess
from bottle import run, post, request, response, get, route



automatic = 1

waypoints = [[51.032981, 3.734168],[51.031186, 3.735625],[51.030953, 3.737267],[51.031307, 3.739161]]
waypointp = 0

sleep(1)
#arduino = sensors.Arduino.Arduino()




while(1):
    if automatic:
        try:
            p = sensors.Phone.Phone()
            cp = p.getcoordinates()
            k = cp['lat']
            if functions.basicfunctions.calcdistance(cp['lat'],cp['lon'],waypoints[waypointp][0],waypoints[waypointp][1]) < 10:
                waypointp = waypointp + 1
            wdir = functions.basicfunctions.calcdirection(cp['lat'],cp['lon'],waypoints[waypointp][0],waypoints[waypointp][1])
            arduino = sensors.Arduino.Arduino()
            adir = arduino.getcompasValue()
            dir = wdir - adir
            print(dir)
            rs = sensors.Realsense.RealSense()
            rsv = rs.getRealSenseValue()
            ldv = sensors.Lidar.Lidar().getLidarValue()
            ldv = np.full(682,5000)
            dir, speed = functions.basicfunctions.determinedirection(ldv,rsv,dir)
            arduino.sendmotorValue(functions.basicfunctions.topwm(dir,speed))
        except:
            print("automation not possible")
        sleep(0.1)
    #
    else:
        k = 2

