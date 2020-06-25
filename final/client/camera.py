#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time
from typing import Any, ByteString, List, Text, Tuple

import cv2
import keyboard
import numpy as np

# For a stream coming from an url :
# import requests
# stream=requests.get('http://localhost:8080/frame.mjpg').content

os.system("title client_camera")

def var_sync(filepath: Text):
  "get data from probes prgm"
  if not(os.path.exists(filepath)):
    return None

  with open(filepath,"r") as f:
    content = eval(f.readline().rstrip("\n"))

  return content

def disp_overlay(img: "decoded image", data: Any, pos: Tuple, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=2, color: "in (B, G, R) format" =(0, 100, 255), thickness=3):
  "add {data} to the {img} array at position {pos}"
  val1, unit1 = pos[0].split(" ")
  val2, unit2 = pos[1].split(" ")
  if unit1 == "%":
    val1 = round(img.shape[0]*int(val1)/100) # convert % to pixels
  elif unit1 == "px":
    val1 = int(val1) # no need to convert

  # same
  if unit2 == "%":
    val2 = round(img.shape[1]*int(val2)/100)
  elif unit2 == "px":
    val2 = int(val2)

  # add HUD to the img and return it (no need to store it as the image's type is mutable)
  cv2.putText(img, data, (val1,val2), font, font_size, color, thickness=thickness)
  return img

def find_all(string: Union[Text, ByteString], substring: Union[Text, ByteString]) -> List:
  "return all occurences of {substring} in {string}"
  if (type(string) != type(substring)) and not(isinstance(string, (str, bytes))):
    raise TypeError("arguments are not of the same type (either str or bytes-like objects)")

  result = []
  current = string.find(substring)
  while current != -1:
    result.append(current)
    current = string.find(substring, current+1)

  return result


# create socket object and try to connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting...")
ip = ('192.168.137.2', 50002)
client_socket.connect(ip)
print("Connected")

# create data stream with the remote socket in read-only mode
stream = client_socket.makefile('rb')

# create save folder if it doesn't exist
savepath = "sm4000_received_data\\camera_data"
if os.path.exists(savepath):
  os.makedirs(savepath)

# create video object
vidname = time.strftime('sm4000_camera_output_%Y-%m-%d_%H-%M-%S.mp4')
with cv2.VideoWriter(f'sm4000_received_data\\camera_data\\{vidname}', cv2.VideoWriter_fourcc(*'mp4v'), 11, (1296,730)) as vid_file:
  # cv2.VideoWriter(filename, encoding, fps, resolution)
  bytes_var = bytes(1)
  scale = 50

  status = str()
  while status != "stop":
    data_hud = var_sync("var_sync.txt")
    if data_hud == None:
      var_check = False
    else:
      var_check = True

    # fetch camera data from stream socket
    bytes_var += stream.read(4096)

    # find all frame boundaries
    a = find_all(bytes_var, b'\xff\xd8')
    b = find_all(bytes_var, b'\xff\xd9')

    if a and b: # if a and b aren't empty
      # process each img found with HUD and encode it in video
      for i in range( min(len(a), len(b)) ): # select all frames in the buffer
        image_bytes = bytes_var[a[i]:b[i]+2] # extract selected frame in the buffer

        img = cv2.imdecode(numpy.frombuffer(image_bytes, dtype=numpy.uint8), 1) # decode it

        # and add HUD
        if var_check:
          try:
            disp_overlay(img, data_hud['bat_percent'],["5 %","7 %"])
            disp_overlay(img, data_hud['ext_depth'],["70 %","5 %"])
            disp_overlay(img, data_hud['ext_pressure'],["110 %","7 %"])
          except:
            print("HUD Error")

        vid_file.write(img) # then encode the img in video
      else:
        bytes_var = bytes_var[b[-1]+2:] # when all frames are processed crop buffer with the unused data

        # rescale img to decrease lags
        width = int(img.shape[1] * scale / 100)
        height = int(img.shape[0] * scale / 100)
        dsize = (width, height)
        img_post_process = cv2.resize(img, dsize, interpolation=cv2.INTER_AREA)

        cv2.imshow('Image from piCamera', img_post_process) # display it

        if cv2.waitKey(1) & 0xFF == ord('q'): # stop reception with key 'q'
          status = "stop"

vid_file.release() # write end tags and close video file
client_socket.send(status.encode()) # send shutdown status to the socket
cv2.destroyAllWindows() # destroy all remaining cv2's windows
stream.close() # close stream
client_socket.close() # close socket
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
