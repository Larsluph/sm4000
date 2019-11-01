#!/usr/bin/env python
#-*- coding:Utf-8 -*-

import socket, keyboard

powered = False
dir = [0, 0, 0]
old = str()

while True:
	while powered:
		# DONE : catch keyboard inputs
		if keyboard.is_pressed('z'):
			dir[0] = +50
			dir[1] = +50
		
		elif keyboard.is_pressed('s'):
			dir[0] = -50
			dir[1] = -50
		
		elif keyboard.is_pressed('q'):
			dir[0] = -50
			dir[1] = +50
		
		elif keyboard.is_pressed('d'):
			dir[0] = +50
			dir[1] = -50
		
		if keyboard.is_pressed('space'):
			dir[2] = +50
		
		elif keyboard.is_pressed('shift'):
			dir[2] = -50
		
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
				
		while keyboard.is_pressed('enter'):
			powered = False
		
		cmd = str([powered, dir])
		cmd += " " * (27-len(cmd))
		if cmd != old:
			print(len(cmd),cmd)
			old = cmd
		
	# DONE : on/off
	print(powered)
	
	while not(powered):
		while keyboard.is_pressed('enter'):
			powered = True
		if keyboard.is_pressed('echap'):
			quit()
