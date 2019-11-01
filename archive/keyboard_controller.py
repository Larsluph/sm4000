#!/usr/bin/env python
#-*- coding:Utf-8 -*-

import socket, keyboard

ip = ("192.168.137.2",50000)

print("Connecting to %s:%s..."%(ip[0],ip[1]))
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ip)
print("Connected!")

powered = False
dir = [0, 0, 0]
pos = 100
old = str()

while True:
	while powered:
		# DONE : catch keyboard inputs
		if keyboard.is_pressed('z'):
			dir[0] = +pos
			dir[1] = +pos
		
		elif keyboard.is_pressed('s'):
			dir[0] = -pos
			dir[1] = -pos
		
		elif keyboard.is_pressed('q'):
			dir[0] = -pos
			dir[1] = +pos
		
		elif keyboard.is_pressed('d'):
			dir[0] = +pos
			dir[1] = -pos
		
		if keyboard.is_pressed('space'):
			dir[2] = +pos
		
		elif keyboard.is_pressed('shift'):
			dir[2] = -pos
		
		# DONE : doser les entrees directionnelles
		if keyboard.is_pressed('1'):
			for x in range(3):
				dir[x] = dir[x] * 1
		
		elif keyboard.is_pressed('2'):
			for x in range(3):
				dir[x] = dir[x] * 2
		
		elif keyboard.is_pressed('3'):
			for x in range(3):
				dir[x] = dir[x] * 3
				
		elif keyboard.is_pressed('4'):
			for x in range(3):
				dir[x] = dir[x] * 4
				
		elif keyboard.is_pressed('5'):
			for x in range(3):
				dir[x] = dir[x] * 5
		
		elif keyboard.is_pressed('6'):
			for x in range(3):
				dir[x] = dir[x] * 6
				
		elif keyboard.is_pressed('7'):
			for x in range(3):
				dir[x] = dir[x] * 7
				
		elif keyboard.is_pressed('8'):
			for x in range(3):
				dir[x] = dir[x] * 8
				
		elif keyboard.is_pressed('9'):
			for x in range(3):
				dir[x] = dir[x] * 9
				
		while keyboard.is_pressed('enter'):
			powered = False
		
		cmd = str([powered, dir])
		cmd += " " * (27-len(cmd))
		if cmd != old:
			print(len(cmd),cmd)
			client.send(cmd.encode("Utf8"))
			old = cmd
		
	# DONE : on/off
	print(powered)
	
	while not(powered):
		while keyboard.is_pressed('enter'):
			powered = True
		if keyboard.is_pressed('echap'):
			client.send("'exit'".encode("Utf8"))
			client.close()
			quit()
