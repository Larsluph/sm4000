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
pos = 200

while True:
    key = keyboard.read_key()
	if powered:
		# DONE : catch keyboard inputs
		if key == 'z':
			dir[0] = +pos
			dir[1] = +pos
		
		elif key == 's':
			dir[0] = -pos
			dir[1] = -pos
		
		elif key == 'q':
			dir[0] = -pos
			dir[1] = +pos
		
		elif key == 'd':
			dir[0] = +pos
			dir[1] = -pos
		
		if key == 'space':
			dir[2] = +pos
		
		elif key == 'shift':
			dir[2] = -pos
		
		# DONE : doser les entrees directionnelles
		try:
		    key = int(key)
			for x in range(3):
				dir[x] = dir[x] + 50 * key
		except:
		    pass
		
		if key == 'enter':
			powered = False
		
		cmd = str([powered, dir])
		cmd += " " * (27-len(cmd))
		print(len(cmd),cmd)
		client.send(cmd.encode("Utf8"))
		
	# DONE : on/off
	
	elif not(powered):
		if key == 'enter':
			powered = True
		elif key == 'echap':
			client.send("'exit'".encode("Utf8"))
			client.close()
			quit()
    print(powered)