#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard

import picamera

##################
## MAIN PROGRAM ##
##################

os.system("clear")

# DONE : picamera
try:
    print("Initializing camera...")
    camera = picamera.PiCamera(resolution=(1296,730),framerate=30)
    camera.rotation = 180
    camera.start_preview(alpha=0)
    camera.stop_preview()
    print("Camera initialized")
except picamera.exc.PiCameraError:
    print("Camera failed to initialize\nTry rebooting the system")
    raise SystemExit

# DONE : server set up
ip = ('192.168.137.2',50002)

server_socket = socket.socket()
server_socket.bind(ip)
print("server binded to '%s'" % (":".join(map(str,ip))) )
server_socket.listen(0)
print("Waiting for viewer")
viewer, address = server_socket.accept()

print("Connected")

# DONE : stream set up
stream = viewer.makefile('wb')
print("stream initialized")
camera.start_recording(stream, 'mjpeg')

stop_stream = viewer.recv(32).decode()
while stop_stream != "stop":
    stop_stream = viewer.recv(32).decode()

camera.stop_recording()
stream.close()
viewer.close()
server_socket.close()

print("END")
