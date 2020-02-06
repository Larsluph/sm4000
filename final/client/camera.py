#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard
import numpy

import cv2

# For a stream coming from an url :
# import requests
# stream=requests.get('http://localhost:8080/frame.mjpg').content

os.system("title client_camera")

def var_sync(filepath):
  with open(filepath,"r") as f:
    content = eval(f.readline().rstrip("\n"))

  return content

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
  bytes_var = bytes(1)

  scale = 50

  status=str()
  while status != "stop":
    try:
      data_hud = var_sync("var_sync.txt")
    except:
      var_check = False
    else:
      var_check = True

    bytes_var += stream.read(4096)
    a = bytes_var.find(b'\xff\xd8')
    b = bytes_var.find(b'\xff\xd9')

    if a!=-1 and b!=-1:
      image_bytes = bytes_var[a:b+2]
      bytes_var = bytes_var[b+2:]

      img = cv2.imdecode(numpy.frombuffer(image_bytes, dtype=numpy.uint8),1)
      img_check = img

      width = int(img.shape[1] * scale / 100)
      height = int(img.shape[0] * scale / 100)
      dsize = (width,height)

      # DONE: implement camera HUD
      if var_check:
        txt_color = (255,100,000)[::-1]
        img_pre_process = cv2.putText(img,f"{data_hud["bat_percent"]}%",(round(img.shape[1]*.05),round(img.shape[0]*.10)),cv2.FONT_HERSHEY_SIMPLEX,2,txt_color,thickness=3) # battery percent left
        img_pre_process = cv2.putText(img,f"{data_hud["ext_pressure"]}mbar",(round(img.shape[1]*.75),round(img.shape[0]*.10)),cv2.FONT_HERSHEY_SIMPLEX,2,txt_color,thickness=3) # external pressure
        img_check = img_pre_process

      img_post_process = cv2.resize(img_check,dsize,interpolation=cv2.INTER_AREA)

      cv2.imshow('Image from piCamera', img_post_process)
      vid_file.write(cv2.imencode(".jpeg",img_pre_process)[1].tostring().encode())
      vid_file.flush()

      if cv2.waitKey(1) & 0xFF == ord('q'):
        status="stop"

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
