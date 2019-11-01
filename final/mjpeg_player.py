#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import cv2, numpy, time

vid_path = input('absolute path of mjpeg file : ')
vid_file = open(vid_path,mode='rb')
# fps = int(input('enter fps : '))
fps = 25
frame_counter = 0
frame_gen_time = time.perf_counter()

bytes = vid_file.read()
while len(bytes) != 0:
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a!=-1 and b!=-1:
        image_bytes = bytes[a:b + 2]
        bytes = bytes[b + 2:]
        frame_counter += 1
        frame_gen_time = time.perf_counter()
        image = cv2.imdecode(numpy.fromstring(image_bytes, dtype=numpy.uint8), 1)

        while (time.perf_counter() - frame_gen_time) < 1/fps:
            pass

        cv2.imshow("Image from Picamera",image)
        ms = (time.perf_counter()-frame_gen_time)*100
        frame = 1/(time.perf_counter()-frame_gen_time)
        print(f"{ms:0.2} ms {frame:00.3} fps")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

print(frame_counter,"frames")
cv2.destroyAllWindows()
vid_file.close()
print('END')

# I:\sm4000\final\test.mjpeg
