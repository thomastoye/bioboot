from singleton_decorator import singleton
import collections
from bottle import run, post, request, response, get, route
import _thread
import sensors.Arduino

@singleton
class Phone:
    deq = None
    qav = None
    def __init__(self):
        self.deq = collections.deque(maxlen=1)
        _thread.start_new_thread(self.ft,(self.deq,))
        _thread.start_new_thread(self.rms, (self.deq,))
        ard = sensors.Arduino.Arduino()
        self.qav = ard.getquephone()



    def ft(self,q):
        @route('/push', method='POST')
        def process():
            k = request.json
            v = 5
            self.deq.append(k['location'])
            # return subprocess.check_output(['python',path+'.py'],shell=True)

        run(host='0.0.0.0', port=3000, debug=True, quiet=True)


    def rms(self,q):
        @route('/pull', method='GET')
        def process():
            try:
                v = self.qav.popleft()
                self.qav.append(v)
                return v
            except:
                return 'error no value available'


    def getcoordinates(self):
        try:
            v = self.deq.popleft()
            self.deq.append(v)
            return v
        except Exception as e:
            print("phone not ready")
            print(str(e))
            return None