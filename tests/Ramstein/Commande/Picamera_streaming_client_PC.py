import socket
import cv2
import numpy

##For a stream coming from an url :
##import urllib
##stream=urllib.urlopen('http://localhost:8080/frame.mjpg')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting...")

client_socket.connect(('172.16.0.156', 50000))

print("Connected")

stream = client_socket.makefile('rb')

bytes = b'' # Define a bytes object
while True:
    bytes = bytes + stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a!=-1 and b!=-1:
        image_bytes = bytes[a:b + 2]
        bytes = bytes[b + 2:]
        image = cv2.imdecode(numpy.fromstring(image_bytes, dtype=numpy.uint8), 1)
        cv2.imshow('Image from piCamera', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

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
##[jpeg data]      |--this part is extracted and decoded
##0xff 0xd9      --|
##...(http)
##0xff 0xd8      --|
##[jpeg data]      |--this part is extracted and decoded
##0xff 0xd9      --|
##...(http)
