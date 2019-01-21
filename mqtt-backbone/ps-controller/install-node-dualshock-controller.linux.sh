#!/bin/bash

# Pre-req: sudo apt-get install libudev-dev libusb-1.0-0 libusb-1.0-0-dev build-essential git
# Pre-req: npm install -g node-gyp node-pre-gyp

cd node-dualshock-controller
npm install
npm install node-hid --driver=hidraw --build-from-source

