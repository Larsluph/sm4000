#!usr/bin/env python
#-*- coding:utf-8 -*-

import time, os, sys, serial, picamera, socket, array
import module_servos as servo

####################
####### FUNCs ######
####################

def init(com_port):
	com.close()
	com = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
	idgauche = 1
	idy = 2
	iddroite = 3
	
def move(com_port,pos,delay):
	servo.center_all(com_port,1000)
	time.sleep(1)
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
			servo_on == True
			
		else:
			print("servo isn't responding\nRetrying in 5 sec...")
			time.sleep(5)
			test_servo(com_port)
		
def close():
	cmd[1] = [0, 0, 0]
	move(com,cmd[1], 2000)
	
##################
## MAIN PROGRAM ##
##################

os.system("clear")

# DONE : servo set up
serial.Serial('/dev/ttyUSB0', 9600, timeout = 1).close()
com = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
test_servo(com)

# DONE : server set up
ip = os.popen('echo $(hostname -I)').read() #172.16.0.156
ip = ip[:len(ip)-1]

server_socket = socket.socket()
server_socket.bind((ip,50000))
print("server binded to '%s:50000'" % (ip) )
print("Waiting for remote")
server_socket.listen(0)
telecommande, address1 = server_socket.accept()

print("Connected")

print("Waiting for instructions...")

cmd = [False,[0,0,0]]

while True:
	while cmd[0] == True:
		cmd = eval(telecommande.recv(27).decode('Utf8'))
		print(cmd)
		print("")
		# DONE : reception telecommande
		if cmd[0] == False:
			close()
		move(com,cmd[1],2000)
		
	while cmd[0] == False:
		cmd = eval(telecommande.recv(27).decode('Utf8'))
		print(cmd)
		print("")
		
		if cmd[0] == True:
			init()
		
		elif cmd == "exit":
			com.close()
			telecommande.close()
			server_socket.close()
			sys.exit(0)
