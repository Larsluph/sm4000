#!usr/bin/env python
#-*- coding:utf-8 -*-

import time, os, sys, serial, picamera, socket

####################
### MAIN PROGRAM ###
####################

os.system("clear")

# DONE : picamera
try:
	print("Initializing camera...")
	global camera
	camera = picamera.PiCamera()
	camera.resolution = (640, 480)
	camera.start_preview(alpha=0)
	camera.stop_preview()
	print("Camera initialized")
	camera_check = True
except picamera.exc.PiCameraError:
	print("Camera failed to initialize")
	sys.exit(0)

# DONE : server set up
ip = os.popen('echo $(hostname -I)').read() #172.16.0.156
ip = ip[:len(ip)-1]

server_socket = socket.socket()
server_socket.bind((ip,50000))
print("server binded to '%s:50000'" % (ip) )
print("Waiting for remote")
server_socket.listen(0)
telecommande, address1 = server_socket.accept()

print("Waiting for remote camera viewer")
retourvideo, address2 = server_socket.accept()

print("Connected")

# DONE : stream set up
stream = retourvideo.makefile('wb')
print("stream initialized")

print("Waiting for instructions...")

cmd = [False,[0,0,0]]

while True:
	while cmd[0] == True:
		cmd = eval(telecommande.recv(27).decode('Utf8'))
		print(cmd)
		print("")
		
	while cmd[0] == False:
		cmd = eval(telecommande.recv(27).decode('Utf8'))
		print(cmd)
		print("")
		
		if cmd[0] == True:
			if camera_check:
				camera.start_recording(stream, 'mjpeg')
		
		elif cmd == "exit":
			com.close()
			telecommande.close()
			retourvideo.close()
			stream.close()
			server_socket.close()
			sys.exit(0)
