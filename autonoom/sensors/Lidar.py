from singleton_decorator import singleton
import numpy as np
import cv2
import collections
import _thread
from breezylidar import URG04LX

@singleton
class Lidar:

    deq = None

    def __init__(self):
        laser = URG04LX(DEVICE)
        self.deq = collections.deque(maxlen=1)
        _thread.start_new_thread(producer, (self.deq,laser))

    def updatedata(self,q,laser):
        try:
            while True:
                data = laser.getScan()

                q.append(data)

        finally:
            print("lidar stopped")

    def getLidarValue(self):
        try:
            return self.deq.popleft()
        except:
            print("lidarque empty")
            return None


