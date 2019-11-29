#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import threading

import pygame

os.system('title sm4000 client controller')

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString, color=(255,255,0)):
        textBitmap = self.font.render(textString, True, color)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

class Vars:
    def __init__(self):
        self.running = True
        self.dir = {
            "powered" : False,
            "left" : 0,
            "right" : 0,
            "y" : 0,
            "light_pow" : False,
            "lights" : 0
        }
        self.pwr = dict()
        self.pos = 100
        self.threshold = .2
        self.light_step = self.pos

        self.key_init = False
        self.joy_init = False

    def key_vars(self):
        self.key_init = True
  
    def joy_vars(self):
        self.joy_init = True
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        self.boosted = True

        self.latest = self.dir.copy()

        self.axes = (0.0,0.0,0.0,0.0)
        self.buttons = (None,0,0,0,0,0,0,0,0,0,0,0,0)

#################

def print_recap(data):

    fg_color = ( 255, 255,   0) # yellow
    bg_color = (   0,   0,   0) # black

    size = [500, 700]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("sm4000 controller recap")

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Get ready to print
    textPrint = TextPrint()

    # -------- Main Program Loop -----------
    while data.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.running = False

        data.axes = (
            data.joy.get_axis(0),
            -data.joy.get_axis(1),
            data.joy.get_axis(2),
            data.joy.get_axis(3),
            data.joy.get_hat(0)
        )

        data.buttons = (
            None,
            data.joy.get_button(0),
            data.joy.get_button(1),
            data.joy.get_button(2),
            data.joy.get_button(3),
            data.joy.get_button(4),
            data.joy.get_button(5),
            data.joy.get_button(6),
            data.joy.get_button(7),
            data.joy.get_button(8),
            data.joy.get_button(9),
            data.joy.get_button(10),
            data.joy.get_button(11)
        )

        data.pwr = {
            "x": int( abs( round(data.axes[0],2) ) * 5),
            "y": int( abs( round(data.axes[1],2) ) * 5),
            "lights": int(abs(data.axes[2] - 1) * 5)
        }

        # DRAWING STEP
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(bg_color)
        textPrint.reset()

        textPrint.print(screen, f"axes:", fg_color)
        textPrint.indent()
        for i in range(len(data.axes)):
            textPrint.print(screen, f"Axe {i} : {data.axes[i]}", fg_color)
        textPrint.unindent()

        textPrint.print(screen, f"buttons:", fg_color)
        textPrint.indent()
        for button in data.buttons[1:]:
            textPrint.print(screen, f"{button}", fg_color)
        textPrint.unindent()

        textPrint.print(screen, f"dir:", fg_color)
        textPrint.indent()
        for x in data.dir:
            textPrint.print(screen, f"{x} : {data.dir[x]}", fg_color)
        textPrint.unindent()

        textPrint.print(screen, f"pwr:", fg_color)
        textPrint.indent()
        for x in data.pwr:
            textPrint.print(screen, f"{x} : {data.pwr[x]}", fg_color)
        textPrint.unindent()

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 20 frames per second
        clock.tick(20)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()

pygame.init()
pygame.joystick.init()

data = Vars()
data.joy_vars()
print_recap(data)
