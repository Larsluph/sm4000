#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import pathlib
import socket
import time

import keyboard
import numpy

import cv2

##For a stream coming from an url :
##import urllib
##stream=urllib.urlopen('http://localhost:8080/frame.mjpg')

os.system("title client_camera")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting...")
ip = ('192.168.137.2', 50002)
client_socket.connect(ip)
print("Connected")

stream = client_socket.makefile('rb')
try:
    os.system("mkdir sm4000_received_data\\camera_data")
except:
    pass

vidname = time.strftime('sm4000_camera_output_%Y-%m-%d_%H-%M-%S.mjpeg')
with open("sm4000_received_data\\camera_data\\"+vidname,mode='wb') as vid_file:
    bytes = bytes(1) # Define a bytes object

    scale = 50

    running = True
    while running:
        bytes += stream.read(4096)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')

        if a!=-1 and b!=-1:
            image_bytes = bytes[a:b + 2]
            bytes = bytes[b + 2:]
            vid_file.write(image_bytes)
            vid_file.flush()

            src = numpy.frombuffer(image_bytes, dtype=numpy.uint8)

            w = int( img.shape[1] * scale / 100)
            h = int( img.shape[0] * scale / 100)
            dsize = ( w, h)

            src = cv2.resize(src,dsize)
            image = cv2.imdecode(src, 1)
            cv2.imshow('Image from piCamera', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False

client_socket.send(status.encode())
cv2.destroyAllWindows()
time.sleep(1)
stream.close()
client_socket.close()
print('client socket closed')

##Mjpeg over http is multipart/x-mixed-replace with boundary frame info and jpeg data is just sent in binary.
##So you don't really need to care about http protocol headers.
##All jpeg frames start with marker 0xff 0xd8 and end with 0xff 0xd9.
##So the code above extracts such frames from the http stream and decodes them one by one. like below.
##
##...(http)
##0xff 0xd8      --|
##[jpeg data]    |--this part is extracted and decoded
##0xff 0xd9      --|
##...(http)
##0xff 0xd8      --|
##[jpeg data]    |--this part is extracted and decoded
##0xff 0xd9      --|
##...(http)
