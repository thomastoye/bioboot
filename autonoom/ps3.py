# import threading
#
# import pygame, sys
# from time import sleep
#
# # setup the pygame window
# pygame.init()
# #window = pygame.display.set_mode((200, 200), 0, 32)
#
# # how many joysticks connected to computer?
# joystick_count = pygame.joystick.get_count()
# print("There is " + str(joystick_count) + " joystick/s")
#
# if joystick_count == 0:
#     # if no joysticks, quit program safely
#     print("Error, I did not find any joysticks")
#     pygame.quit()
#     sys.exit()
# else:
#     # initialise joystick
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#
# axes = joystick.get_numaxes()
# buttons = joystick.get_numbuttons()
# hats = joystick.get_numhats()
#
# print("There is " + str(axes) + " axes")
# print("There is " + str(buttons) + " button/s")
# print("There is " + str(hats) + " hat/s")
#
#
# def getAxis(number):
#     # when nothing is moved on an axis, the VALUE IS NOT EXACTLY ZERO
#     # so this is used not "if joystick value not zero"
#     if joystick.get_axis(number) < -0.1 or joystick.get_axis(number) > 0.1:
#         # value between 1.0 and -1.0
#         print("Axis value is %s" % (joystick.get_axis(number)))
#         print("Axis ID is %s" % (number))
#
#
# def getButton(number):
#     # returns 1 or 0 - pressed or not
#     if joystick.get_button(number):
#         # just prints id of button
#         print("Button ID is %s" % (number))
#
#
# def getHat(number):
#     if joystick.get_hat(number) != (0, 0):
#         # returns tuple with values either 1, 0 or -1
#         print("Hat value is %s, %s" % (joystick.get_hat(number)[0], joystick.get_hat(number)[1]))
#         print("Hat ID is %s" % (number))
#
# def check_events():
#     while True:
#         pygame.event.get()
#
# # thread = threading.Thread(target=check_events())
# # thread.start()
# while True:
#     for event in pygame.event.get():
#         # loop through events, if window shut down, quit program
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
#     if axes != 0:
#         for i in range(axes):
#             getAxis(i)
#     if buttons != 0:
#         for i in range(buttons):
#             getButton(i)
#     if hats != 0:
#         for i in range(hats):
#             getHat(i)
#     left=255
#     right=-255
#     json="{\"left\":\"%i\"," %left +"\"right\":\"%i\"}" %right
#
#     print(json)
#     sleep(1)
#
# #Kruis		0
# #cirkel		1
# #vierkant	2
# #driehoek	3
# #L1		4
# #R1		5
# #Select		6
# #Start		7
# #Linkerjoybut	8
# #Rechterjoybut	9
# #
# #d-pad links		id	0 value	-1, 0
# #d-pad rechts		id	0 value	1, 0
# #d-pad omhoog		id	0 value	0, 1
# #d-pad omlaag		id	0 value	0, -1
# #
# #linker stick  axis 0 horizontaal (L -1-> R 1), 1 vertikaal (boven -1 -> onder 1)
# #rechter stick  axis 4 horizontaal (L -1-> R 1), 3 vertikaal (boven -1 -> onder 1)
import time

from singleton_decorator import singleton
import ctypes
import pygame, sys

class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),("wRightMotorSpeed", ctypes.c_ushort)]

@singleton
class ps3Vibrate:
    XInputSetState = None
    xinput = None

    def __init__(self,controller_id):

        self.xinput = ctypes.windll.xinput1_1

        self.XInputSetState = self.xinput.XInputSetState
        self.XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
        self.XInputSetState.restype = ctypes.c_uint

        vibration = XINPUT_VIBRATION(65535, 32768)
        self.XInputSetState(0, ctypes.byref(vibration))

    def set_vibration(self,controller, left_motor, right_motor):
        vibration = XINPUT_VIBRATION(int(left_motor * 65535), int(right_motor * 65535))
        self.XInputSetState(controller, ctypes.byref(vibration))




#ps3vibrate.set_vibration(0, 0.5, 0.5)
#time.sleep(5)



from enum import Enum

# controller
@singleton
class boatcontroller:
    motorSpeed = 0
    direction = 0

    axes = None
    buttons = None
    hats = None
    joystick = None
    ps3vibrate = None
    polltime = None

    def __init__(self,controller_id):

        pygame.init()
        self.polltime = int(round(time.time() * 1000))
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:

            print("Error, I did not find any joysticks")
            pygame.quit()
            sys.exit()
        else:
            self.joystick = pygame.joystick.Joystick(controller_id)
            self.joystick.init()

        self.axes = self.joystick.get_numaxes()
        self.buttons = self.joystick.get_numbuttons()
        self.hats = self.joystick.get_numhats()

        self.ps3vibrate = ps3Vibrate(controller_id)

    # def setMotorspeed(self,speed):
    #     self.motorSpeed = speed

    def getMotorspeed(self):
        if self.motorSpeed > 255:
            return 255
        elif self.motorSpeed < -255:
            return -255
        else:
            return self.motorSpeed
    def getDirection(self):
        if self.direction > 1:
            return 1
        elif self.direction < -1:
            return -1
        else:
            return self.direction

    def getAxis(self,number):
        if self.joystick.get_axis(number) < -0.05 or self.joystick.get_axis(number) > 0.05:
            return number,(self.joystick.get_axis(number))
        else:
            #return number, 0
            self.direction = 0

        return None,None

    # def getAxes(self):
    #     return self.axes

    def getButton(self,number):
        if self.joystick.get_button(number):
            return number

    # def getButtons(self):
    #     return self.buttons

    def getHat(self,number):
        if self.joystick.get_hat(number) != (0, 0):
            # returns tuple with values either 1, 0 or -1
            return (self.joystick.get_hat(number)[0], self.joystick.get_hat(number)[1]), number

    # def getHats(self):
    #     return self.hats

    def pollBoatDirection(self,polltime):
        currenttime = int(round(time.time() * 1000))
        if (self.polltime + polltime) < currenttime:
            pygame.event.get()

            self.ps3vibrate.set_vibration(0, 0, 0)

            if self.axes != 0:
                temp_ax, temp_ax_value = self.getAxis(0)
                if temp_ax == 0:
                    #print('tempax')
                    direction_abs = abs(temp_ax_value)
                    mapped_dir = (0.636997 * (direction_abs ** 3)) - (1.74796 * (direction_abs ** 2)) + (
                    2.11798 * direction_abs) + 0.00619418

                    if temp_ax_value > 0:
                        self.direction = mapped_dir
                    else:
                        self.direction = -mapped_dir
                    #print(self.getDirection())
                    # arduino.sendmotorValue(functions.basicfunctions.topwm(temp_ax_value, motorSpeed,True))
                    # print(functions.basicfunctions.topwm(temp_ax_value, motorSpeed,True))
            if self.buttons != 0:
                for i in range(self.buttons):
                    button = (self.getButton(i))
                    if button == 4:
                        if self.motorSpeed > -255:
                            self.motorSpeed = self.motorSpeed - 26
                            self.ps3vibrate.set_vibration(0, 0.4, 0.4)
                            # arduino.sendmotorValue(functions.basicfunctions.topwm(0, motorSpeed))
                            # print(functions.basicfunctions.topwm(0, motorSpeed))
                    elif button == 5:
                        if self.motorSpeed < 255:
                            self.motorSpeed = self.motorSpeed + 26
                            self.ps3vibrate.set_vibration(0, 0.4, 0.4)
                            # arduino.sendmotorValue(functions.basicfunctions.topwm(0, motorSpeed))
                            # print(functions.basicfunctions.topwm(0, motorSpeed))
            if self.hats != 0:
                for i in range(self.hats):
                    self.getHat(i)
            #print(self.getMotorspeed())


#controller=boatcontroller(0)

#while 1:
 #   controller.pollBoatDirection(150)
  #  time.sleep(0.15)