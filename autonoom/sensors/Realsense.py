from singleton_decorator import singleton
import pyrealsense2 as rs
import numpy as np
import cv2
import collections
import _thread
import functions.basicfunctions


@singleton
class RealSense:

    deq = None

    def __init__(self):

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.deq = collections.deque(maxlen=1)
        _thread.start_new_thread(self.updatedata, (self.deq, pipeline, config))

    def updatedata(self,q,pipeline,config):
        try:
            pipeline.start(config)
            while True:

                # Wait for a coherent pair of frames: depth and color
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()

                if not depth_frame :
                    continue

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())


                q.append(functions.basicfunctions.detectShoresFrom3DImage((depth_image)))


        finally:
            # Stop streaming
            pipeline.stop()
            print("realsense stopped")

    def getRealSenseValue(self):
        try:
            return self.deq.popleft()
        except:
            print("realsensque empty")
            return None


