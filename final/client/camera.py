#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import os
import pathlib
import socket
import time

import cv2
import numpy

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

vidname = time.strftime('..\\sm4000_camera_output_%y:%m:%d_%h:%m:%s.mjpeg')
vid_file = open(vidname,mode='wb')

bytes = bytes(1) # Define a bytes object
while len(bytes) != 0:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a!=-1 and b!=-1:
        image_bytes = bytes[a:b + 2]
        bytes = bytes[b + 2:]
        image = cv2.imdecode(numpy.fromstring(image_bytes, dtype=numpy.uint8), 1)
        vid_file.write(image_bytes)
        vid_file.flush()
        cv2.imshow('Image from piCamera', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

client_socket.send("stop".encode("Utf8"))

cv2.destroyAllWindows()
vid_file.close()
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
