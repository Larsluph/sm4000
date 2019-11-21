#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time

import keyboard
import pygame
import pygame.joystick

pygame.init()
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()
i = 0
while not(keyboard.is_pressed('esc')):
    pygame.event.get()
    axes = (
        joy.get_axis(0),
        -joy.get_axis(1),
        joy.get_axis(2),
        joy.get_axis(3),
        joy.get_hat(0)
    )
    buttons = (
        None,
        joy.get_button(0),
        joy.get_button(1),
        joy.get_button(2),
        joy.get_button(3),
        joy.get_button(4),
        joy.get_button(5),
        joy.get_button(6),
        joy.get_button(7),
        joy.get_button(8),
        joy.get_button(9),
        joy.get_button(10),
        joy.get_button(11)
    )
    print(axes,buttons,sep="\n")
    print()
    time.sleep(.5)
