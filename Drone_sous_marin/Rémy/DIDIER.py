#!usr/bin/env python
#-*- coding:utf-8 -*-

import time, os, sys, serial, picamera, socket, array

####################
####### FUNCs ######
####################

class servo:
	def move(com_port, id, position, time):
		"Function which moves the servo with id 'id' to the position 'position' and 'time' taken by the servo to reach the given position."
		data_to_send = '#' + str(id) + ' P' + str(position) + ' T' + str(time) + chr(13)     # generate str to send
		com_port.write(data_to_send.encode('ascii'))                                         # send the str to the serial port
	
	def center_all(com_port, time):
		"Function which moves all servos to position 1500."
		for x in range(32):
			servo.move(com_port,x,1500,time)

class didier:
	def init(self):
		serial.Serial('/dev/ttyUSB0', 9600, timeout = 1).close()
		com = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
		idgauche = 0
		iddroite = 3
		idy = 2
		
	def move(com_port,pos,delay):
		servo.center_all(com_port,1000)
		time.sleep(1)
		servo.move(com_port, idgauche, 1500+pos[0], delay)
		servo.move(com_port, iddroite, 1500+pos[1], delay)
		servo.move(com_port, idy, 1500-pos[2], delay)
		
	def test_servo(self,com_port):
		while True:
			data_to_send = 'ver' + chr(13)
			com_port.write(data_to_send.encode('ascii'))
			
			incoming_data = com_port.readline()
			if incoming_data.decode('ascii') == "SSC32-V2.50USB" + chr(13):
				print("servo initialized!")
				return True
				
			else:
				print("servo isn't responding\nRetrying in 5 sec...")
				time.sleep(5)
				SM.test_servo(com_port)
			
	def close(self):
		cmd[1] = [0, 0, 0]
		SM.move(cmd[1], 2000)
##################
## MAIN PROGRAM ##
##################

os.system("clear")
SM = didier()

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
SM.test_servo(com)

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
		cmd = eval(telecommande.recv(20).decode('Utf8'))
		print(cmd)
		print("")
		# DONE : reception telecommande
		if cmd[0] == False:
			SM.close()
		SM.move(cmd[1],2000)
		
	while cmd[0] == False:
		cmd = eval(telecommande.recv(20).decode('Utf8'))
		print(cmd)
		print("")
		
		if cmd[0] == True:
			SM.init()
			if camera_check:
				camera.start_recording(stream, 'mjpeg')
		
		elif cmd == "exit":
			com.close()
			telecommande.close()
			retourvideo.close()
			stream.close()
			server_socket.close()
			sys.exit(0)

