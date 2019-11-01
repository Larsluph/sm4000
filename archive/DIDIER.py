#!usr/bin/env python
#-*- coding:utf-8 -*-

import time, os, sys, serial, picamera, socket
import module_servos as servo

####################
####### FUNCs ######
####################
	
def move(com_port,pos,delay):
	servo.move(com_port, idgauche, 1500+pos[0], delay)
	servo.move(com_port, iddroite, 1500+pos[1], delay)
	servo.move(com_port, idy, 1500-pos[2], delay)
	
def test_servo(com_port):
	servo_on = False
	while not(servo_on):
		data_to_send = 'ver' + chr(13)
		com_port.write(data_to_send.encode('ascii'))
		
		incoming_data = com_port.readline()
		if incoming_data.decode('ascii') == ("SSC32-V2.50USB" + chr(13)):
			print("servo initialized!")
			servo_on = True
			
		else:
			print("servo isn't responding\nRetrying in 5 sec...")
			time.sleep(5)
	
##################
## MAIN PROGRAM ##
##################

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
	camera_check = False

# DONE : servo set up
serial.Serial('/dev/ttyUSB0', 9600, timeout = 1).close()
com = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
idgauche = 1
idy = 2
iddroite = 3
test_servo(com)

# DONE : server set up
ip = os.popen('echo $(hostname -I)').read()
ip = ip[:len(ip)-1]

server_socket = socket.socket()
server_socket.bind((ip,50000))
print("server binded to '%s:50000'" % (ip) )
print("Waiting for remote")
server_socket.listen(0)
telecommande, address1 = server_socket.accept()

if camera_check:
	print("Waiting for remote camera viewer")
	retourvideo, address2 = server_socket.accept()

print("Connected")

if camera_check:
	# DONE : stream set up
	stream = retourvideo.makefile('wb')
	print("stream initialized")
	camera.start_recording(stream, 'mjpeg')

print("Waiting for instructions...")

cmd = [False,[0,0,0]]

while True:
	# DONE : reception telecommande
	cmd = telecommande.recv(5000).decode('Utf8')
	cmd = cmd[len(cmd)-27:]
	print(cmd,end='\n\n')
	
	if cmd[0] == True:
		pass
		
	elif cmd[0] == False:
		cmd[1] = [0, 0, 0]
		
	elif cmd == "exit":
		com.close()
		telecommande.close()
		retourvideo.close()
		stream.close()
		server_socket.close()
		sys.exit(0)
		
	move(com,cmd[1],2000)