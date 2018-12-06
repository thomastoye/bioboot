import numpy as np
import sensors.RealSense
#import sensors.Lidar
#import functions.basicfunctions
import serial

automatic = 1

ser = serial.Serial('COM3', 9600)
ser.open()

while(1):
    if automatic:
        Rsv = sensors.RealSense.RealSense.getRealSenseValue()
        ldv = sensors.Lidar.Lidar().getLidarValue()
        dir, speed = functions.basicfunctions.determinedirection(ldv,rsv,0)

        ser.write(functions.basicfunctions.topwm(dir,speed))
    else:
        k = 2

