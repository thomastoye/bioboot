from singleton_decorator import singleton
from flask import Flask, request
import collections
from bottle import run, post, request, response, get, route
import _thread

@singleton
class Phone:
    deq = None
    def __init__(self):
        self.deq = collections.deque(maxlen=1)
        _thread.start_new_thread(self.ft,(self.deq,))



    def ft(self,q):
        @route('/push', method='POST')
        def process():
            k = request.json
            v = 5
            self.deq.append(k['location'])
            # return subprocess.check_output(['python',path+'.py'],shell=True)

        run(host='0.0.0.0', port=3000, debug=True, quiet=True)




    def getcoordinates(self):
        try:
            v = self.deq.popleft()
            self.deq.append(v)
            return v
        except Exception as e:
            print("phone not ready")
            print(str(e))
            return None