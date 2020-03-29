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

def disp_overlay(img,data,pos,font=cv2.FONT_HERSHEY_SIMPLEX,font_size=2,color=(0,100,255),thickness=3):
  val1,unit1 = pos[0].split(" ")
  val2,unit2 = pos[1].split(" ")
  if unit1 == "%":
    val1 = round(img.shape[0]*int(val1)/100)
  elif unit1 == "px":
    val1 = int(val1)

  if unit2 == "%":
    val2 = round(img.shape[1]*int(val2)/100)
  elif unit2 == "px":
    val2 = int(val2)
  cv2.putText(img,data,(val1,val2),font,font_size,color,thickness=thickness)

def find_all(string,substring):
  if (type(string) != type(substring)) and not(isinstance(string,(str,bytes))):
    raise TypeError("arguments are not of the same type (either str or bytes-like objects)")

  result = []
  current = string.find(substring)
  while current != -1:
    result.append(current)
    current = string.find(substring,current+1)

  return result


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

vidname = time.strftime('sm4000_camera_output_%Y-%m-%d_%H-%M-%S.mp4')
with cv2.VideoWriter(f'sm4000_received_data\\camera_data\\{vidname}', cv2.VideoWriter_fourcc(*'mp4v'), 11, (1296,730)) as vid_file:
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
    a = find_all(bytes_var,b'\xff\xd8')
    b = find_all(bytes_var,b'\xff\xd9')

    if bool(a) and bool(b):
      for i in range( min(len(a),len(b)) ):
        image_bytes = bytes_var[a[i]:b[i]+2]
        bytes_var = bytes_var[b[i]+2:]

        img = cv2.imdecode(numpy.frombuffer(image_bytes, dtype=numpy.uint8),1)

        # DONE: implement camera HUD
        if var_check:
          disp_overlay(img,data_hud['bat_percent'],["5 %","7 %"])
          disp_overlay(img,data_hud['ext_depth'],["70 %","5 %"])
          disp_overlay(img,data_hud['ext_pressure'],["110 %","7 %"])

        vid_file.write(img)
      else:
        width = int(img.shape[1] * scale / 100)
        height = int(img.shape[0] * scale / 100)
        dsize = (width,height)

        img_post_process = cv2.resize(img,dsize,interpolation=cv2.INTER_AREA)

        cv2.imshow('Image from piCamera', img_post_process)

        if cv2.waitKey(1) & 0xFF == ord('q'):
          status = "stop"

vid_file.release()
client_socket.send(status.encode())
cv2.destroyAllWindows()
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
