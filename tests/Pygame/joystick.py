#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame.joystick

pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
print("Number of joysticks: ", joystick_count)

joystick = pygame.joystick.Joystick(0)
joystick.init()

name = joystick.get_name()
print(name)

axes = joystick.get_numaxes()
print("Nombre d'axes : ", axes)

buttons = joystick.get_numbuttons()
print("Nombre de boutons : ", buttons)

hats = joystick.get_numhats()
print("Nombres de HAT : ", hats)

running = True
while running:
    pygame.event.get()
    axis_0 = joystick.get_axis(0)
    axis_1 = joystick.get_axis(1)
    axis_2 = joystick.get_axis(2)
    axis_3 = joystick.get_axis(3)
    print(axis_0, axis_1, axis_2, axis_3)

    button_11 = joystick.get_button(11)
    if button_11 == 1:
        running = False

pygame.quit()
