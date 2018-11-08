#!/usr/bin/env python3

from breezylidar import URG04LX

import sys
import json
from time import time

f = open('log.json', 'a+')

DEVICE = '/dev/ttyACM0'
NITER  = 10

laser = URG04LX(DEVICE)

print('===============================================================')
print('Detected lidar')
print(laser)
print('===============================================================')

while True:
    start_sec = time()

    count = 0

    for i in range(1, NITER+1):
        
        sys.stdout.write('Iteration: %3d: ' % i)

        data = laser.getScan()
        
        if data:
            
            print('Got %3d data points' % len(data))

            toWrite = { 'timestamp': time(), 'data': data }
            f.write(json.dumps(toWrite) + '\n')
            
            count += 1
            
        else:
            
            print('=== SCAN FAILED ===')
            
    elapsed_sec = time() - start_sec

    print('%d scans in %f seconds = %f scans/sec' % (count, elapsed_sec, count/elapsed_sec))


