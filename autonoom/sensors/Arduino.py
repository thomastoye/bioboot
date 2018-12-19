from singleton_decorator import singleton
import numpy as np
import cv2
import collections
import _thread
import serial
from time import sleep
import json
import math


@singleton
class Arduino:

    queget = None
    quesend = None


    def __init__(self):
        self.queget = collections.deque(maxlen=1)
        self.quesend = collections.deque(maxlen=1)
        _thread.start_new_thread(self.updatedata, (self.queget,self.quesend, serial.Serial('COM32', 9600,timeout=0.1)))


    def updatedata(self,qget,qsend,ser):
        try:

            while True:

                k = ser.readline()
                if k != b'':
                    qget.append(k)

                if qsend:
                    ser.write(qsend.popleft())
                sleep(0.1)

        finally:
            # Stop streaming

            print("Arduino stopped")

    def getcompasValue(self):
        try:
            v = self.queget.popleft()
            self.queget.append(v)
            d = json.loads(str(v,'ascii'))
            dir = math.atan2(d['my'],d['mx'])
            dir = dir*180/math.pi
            if dir < 0:
                dir = dir + 360
            return dir
        except Exception as e:
            print("arduino not ready")
            print(str(e))
            return None

    def sendmotorValue(self,value):
        try:
            return self.quesend.append(value)
        except:
            print("arduino crashed")
            return None