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
