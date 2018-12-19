from singleton_decorator import singleton
import numpy as np
import cv2
import collections
import _thread
import serial


@singleton
class Arduino:

    queget = None
    quesend = None


    def __init__(self):
        ser = serial.Serial('COM32', 9600, timeout=0.1)
        self.queget = collections.deque(maxlen=1)
        self.quesend = collections.deque(maxlen=1)
        _thread.start_new_thread(self.updatedata, (self.queget,self.quesend, serial.Serial('COM32', 9600,timeout=0.1)))


    def updatedata(self,qget,qsend,ser):
        try:

            while True:

                k =  ser.readline()
                if k != None:
                    qget.append(k)

                if not qsend.empty():
                    ser.write(qsend.popleft())


        finally:
            # Stop streaming

            print("Arduino stopped")

    def getcompasValue(self):
        try:
            v = self.queget.popleft()
            self.queget.append(v)
            return v
        except:
            print("realsensque empty")
            return None

    def sendmotorValue(self,value):
        try:
            return self.quesend.append(value)
        except:
            print("realsensque empty")
            return None