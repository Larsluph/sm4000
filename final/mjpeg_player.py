#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import time

import cv2
import numpy


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

try:
  vid_path = sys.argv[1]
except:
  print("invalid arguments")
  raise SystemExit
with open(vid_path,mode='rb') as vid_file:
  bytes_var = vid_file.read()

if len(sys.argv) < 3:
  fps = 30
else:
  fps = sys.argv[2]

frame_counter = 0
scale = 50

while len(bytes_var) != 0:
  try:
    data_hud = var_sync("var_sync.txt")
  except:
    var_check = False
  else:
    var_check = True

  a = bytes_var.find(b'\xff\xd8')
  b = bytes_var.find(b'\xff\xd9')

  if a!=-1 and b!=-1:
    image_bytes = bytes_var[a:b + 2]
    bytes_var = bytes_var[b + 2:]
    frame_counter += 1
    frame_gen_time = time.perf_counter()

    img = cv2.imdecode(numpy.frombuffer(image_bytes, dtype=numpy.uint8),1)

    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dsize = (width,height)

    if var_check:
      disp_overlay(img,f"{data_hud['bat_percent']}%",["5 %","7 %"])
      disp_overlay(img,f"{data_hud['ext_depth']}m",["70 %","5 %"])
      disp_overlay(img,f"{data_hud['ext_pressure']}mbar",["110 %","7 %"])

    img = cv2.resize(img,dsize,interpolation=cv2.INTER_AREA)

    while (time.perf_counter() - frame_gen_time) < 1/fps:
      pass

    cv2.imshow("Image from Picamera",img)
    ms = (time.perf_counter()-frame_gen_time)*100
    frame = 1/(time.perf_counter()-frame_gen_time)
    print(f"{ms:0.2} ms {frame:00.3} fps")

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

print(frame_counter,"frames")
cv2.destroyAllWindows()
print('END')
