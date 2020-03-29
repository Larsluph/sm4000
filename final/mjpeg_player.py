#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import time

import cv2
import numpy


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
