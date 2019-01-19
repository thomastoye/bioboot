import numpy as np
import sensors.Realsense
import sensors.Arduino
# import sensors.Lidar
import sensors.Phone
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
# from bottle import run, post, request, response, get, route

import ps3

automatic = 0
phone = sensors.Phone.Phone()
waypoints = [[51.032981, 3.734168], [51.031186, 3.735625], [51.030953, 3.737267], [51.031307, 3.739161]]
waypointp = 0

sleep(1)
arduino = sensors.Arduino.Arduino()

# initialization of controller working
controller = ps3.boatcontroller(0)
#controller_prev_dir = 2  # set it to random value that can't be equal to any possible value
controller_prev_m_speed = 1000  # set it to random value that can't be equal to any possible value
controller_turning = False
controller.pollBoatDirection(0)

while (1):
    if automatic:
        try:
            motorSpeed = 0
            p = sensors.Phone.Phone()
            cp = p.getcoordinates()
            k = cp['lat']
            if functions.basicfunctions.calcdistance(cp['lat'], cp['lon'], waypoints[waypointp][0],
                                                     waypoints[waypointp][1]) < 10:
                waypointp = waypointp + 1
            wdir = functions.basicfunctions.calcdirection(cp['lat'], cp['lon'], waypoints[waypointp][0],
                                                          waypoints[waypointp][1])
            arduino = sensors.Arduino.Arduino()
            adir = arduino.getcompasValue()
            dir = wdir - adir
            dir = 0
            print(dir)
            rs = sensors.Realsense.RealSense()
            rsv = rs.getRealSenseValue()

            #ldv = sensors.Lidar.Lidar().getLidarValue()

            ldv = np.full(682, 5000)
            dir, speed = functions.basicfunctions.determinedirection(ldv, rsv, dir)
            int(dir)

            if dir > 360:
                dir = dir - 360
            print(dir)
            arduino.sendmotorValue(functions.basicfunctions.topwm(dir, speed,True))

        except Exception as e:
            print("automation not possible")
            print(str(e))
        sleep(0.1)
    #
    else:
        controller.pollBoatDirection(500)
        controller_dir = controller.getDirection()
        controller_m_speed = controller.getMotorspeed()

        if controller_dir != 0:
            controller_turning = True

            print("Turning")
            pwm_val = functions.basicfunctions.topwm(controller_dir,controller_prev_m_speed,True)
            #print(pwm_val)
            #print(controller_dir)
            #print(controller_m_speed)
            arduino.sendmotorValue(pwm_val)


        elif controller_turning:
            controller_turning = False
            print("Stopped turning")
            pwm_val = functions.basicfunctions.topwm(0, controller_prev_m_speed)
            #print(pwm_val)
            #print(controller_m_speed)
            arduino.sendmotorValue(pwm_val)

        if (controller_m_speed != controller_prev_m_speed):
            controller_prev_m_speed = controller_m_speed

            if (controller_turning == False):
                print("Speed changed")
                pwm_val = functions.basicfunctions.topwm(0, controller_prev_m_speed)
                #print(pwm_val)
                #print(controller_prev_m_speed)
                arduino.sendmotorValue(pwm_val)
            else:
                print("Speed changed while turning")

        sleep(0.15)
