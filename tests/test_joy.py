#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pygame
import pygame.joystick
import keyboard

pygame.init()
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()
i = 0
while not(keyboard.is_pressed('esc')):
    pygame.event.wait()
    print(pygame.event.get('JOYBUTTONDOWN'))
    print(pygame.event.get('JOYBUTTONUP'))
    print(i)
    i += 1
