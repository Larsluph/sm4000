#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os, keyboard

print("Connecting to '172.16.0.156:50000'...")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("172.16.0.156",50000))
print("Connected!")

powered = False

while True:
	while powered:
		# DONE : catch keyboard inputs
		dir = [0, 0, 0]
		if keyboard.is_pressed('z'):
			dir = [+50, +50, 0]
		
		elif keyboard.is_pressed('q'):
			dir = [-50, +50, 0]
			
		elif keyboard.is_pressed('s'):
			dir = [-50, -50, 0]
			
		elif keyboard.is_pressed('d'):
			dir = [+50, -50, 0]
			
		if keyboard.is_pressed('space') and not( keyboard.is_pressed('shift') ):
			dir[2] = +50
			
		elif keyboard.is_pressed('shift') and not( keyboard.is_pressed('space') ):
			dir[2] = -50
			
		# DONE : doser les entrees directionnelle
		if keyboard.is_pressed('3') and not( keyboard.is_pressed('1') or keyboard.is_pressed('2') ):
			for x in range(3):
				dir[x] = dir[x] * 3
				
		elif keyboard.is_pressed('2') and not( keyboard.is_pressed('1') or keyboard.is_pressed('3') ):
			for x in range(3):
				dir[x] = dir[x] * 2
				
		elif keyboard.is_pressed('1') and not( keyboard.is_pressed('2') or keyboard.is_pressed('3') ):
			for x in range(3):
				dir[x] = dir[x] * 1
		else:
			pass
		
		while keyboard.is_pressed('enter'):
			powered = False
			
		cmd = [powered, dir]
		if len(cmd) <= 20:
			print(cmd)
			client.send(str(cmd).encode("Utf8"))
			
		
	# DONE : on/off
	
	while not(powered):
		print(powered)
		while keyboard.is_pressed('enter'):
			powered = True
		if keyboard.is_pressed('echap'):
			client.send("'exit'".encode("Utf8"))
			client.close()
			quit()
