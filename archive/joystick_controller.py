#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import pygame
import pygame.joystick
import keyboard, time

pygame.init()
pygame.joystick.init()

joy = pygame.joystick.Joystick(0)

joy.init()

print(
	"id "		+ str(joy.get_id()),
	"name "		+ str(joy.get_name()),
	"axes "		+ str(joy.get_numaxes()),
	"buttons "	+ str(joy.get_numbuttons()),
	"hats "		+ str(joy.get_numhats()),
	"balls "	+ str(joy.get_numballs()),
	sep='\n'
)

"""
hat(0) = d-pad		[ -1: 1 ] (x,y)
axis(0) = joy x 	[ -1: 1 ] (g,d)
axis(1) = joy y		[  1:-1 ] (b,h)
axis(2) = slider	[  1:-1 ] (low,high)
axis(3) = joy rot	[ -1: 1 ] (indir,dir)
"""

input()

while not(keyboard.is_pressed('p')):
	pygame.event.get()
	print(joy.get_hat(0),joy.get_axis(0),joy.get_axis(1),joy.get_axis(2),joy.get_axis(3))
	print(joy.get_button(0),joy.get_button(1),joy.get_button(2),joy.get_button(3),joy.get_button(4),joy.get_button(5),joy.get_button(6),joy.get_button(7),joy.get_button(8),joy.get_button(9),joy.get_button(10),joy.get_button(11))
	time.sleep(0.25)
	print()