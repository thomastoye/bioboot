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
#from functions.basicfunctions import topwm
import pygame, sys
from enum import Enum

# controller
if True:

    motorSpeed = 0

    # class Buttons(Enum):
    #     kruis =	0
    #     cirkel = 1
    #     vierkant = 2
    #     driehoek = 3
    #     L1 = 4
    #     R1 = 5
    #     Select = 6
    #     Start =	7
    #     LinkerJoyBut = 8
    #     RechterJoybut =	9

    # setup the pygame window
    pygame.init()
    # window = pygame.display.set_mode((200, 200), 0, 32)

    # how many joysticks connected to computer?
    joystick_count = pygame.joystick.get_count()
    print("There is " + str(joystick_count) + " joystick/s")

    if joystick_count == 0:
        # if no joysticks, quit program safely
        print("Error, I did not find any joysticks")
        pygame.quit()
        sys.exit()
    else:
        # initialise joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    axes = joystick.get_numaxes()
    buttons = joystick.get_numbuttons()
    hats = joystick.get_numhats()

    print("There is " + str(axes) + " axes")
    print("There is " + str(buttons) + " button/s")
    print("There is " + str(hats) + " hat/s")


    def getAxis(number):
        # when nothing is moved on an axis, the VALUE IS NOT EXACTLY ZERO
        # so this is used not "if joystick value not zero"
        if joystick.get_axis(number) < -0.1 or joystick.get_axis(number) > 0.1:
            # value between 1.0 and -1.0
            return number,(joystick.get_axis(number))
        return None,None


    def getButton(number):
        # returns 1 or 0 - pressed or not
        if joystick.get_button(number):
            # just prints id of button
            return number


    def getHat(number):
        if joystick.get_hat(number) != (0, 0):
            # returns tuple with values either 1, 0 or -1
            return (joystick.get_hat(number)[0], joystick.get_hat(number)[1]), number

automatic = 0

waypoints = [[51.032981, 3.734168], [51.031186, 3.735625], [51.030953, 3.737267], [51.031307, 3.739161]]
waypointp = 0

sleep(1)
# arduino = sensors.Arduino.Arduino()




while (1):
    if automatic:
        try:
            motorSpeed = 0
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
            print("nothing")
        except:
            print("automation not possible")
        sleep(0.1)
    #
    else:
        k = 2

        for event in pygame.event.get():
            # loop through events, if window shut down, quit program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if axes != 0:
            for i in range(axes):
                temp_ax, temp_ax_value = getAxis(i)
                if temp_ax == 0:
                    arduino.sendmotorValue(functions.basicfunctions.topwm(temp_ax_value, motorSpeed,True))
                    #print(topwm(temp_ax_value, motorSpeed,True))

        if buttons != 0:
            for i in range(buttons):
                button = (getButton(i))

                if button == 4:
                    if motorSpeed > -255:
                        motorSpeed = motorSpeed - 26
                        arduino.sendmotorValue(functions.basicfunctions.topwm(0, motorSpeed))
                        #print(topwm(0, motorSpeed))
                elif button == 5:
                    if motorSpeed < 255
                        motorSpeed = motorSpeed + 26
                        arduino.sendmotorValue(functions.basicfunctions.topwm(0, motorSpeed))
                        #print(topwm(0, motorSpeed))

        if hats != 0:
            for i in range(hats):
                getHat(i)
        sleep(0.15)
        # Kruis		0
        # cirkel		1
        # vierkant	2
        # driehoek	3
        # L1		4
        # R1		5
        # Select		6
        # Start		7
        # Linkerjoybut	8
        # Rechterjoybut	9
        #
        # d-pad links		id	0 value	-1, 0
        # d-pad rechts		id	0 value	1, 0
        # d-pad omhoog		id	0 value	0, 1
        # d-pad omlaag		id	0 value	0, -1
        #
        # linker stick  axis 0 horizontaal (L -1-> R 1), 1 vertikaal (boven -1 -> onder 1)
        # rechter stick  axis 4 horizontaal (L -1-> R 1), 3 vertikaal (boven -1 -> onder 1)
