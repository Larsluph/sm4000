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
        # DRAWING STEP
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(bg_color)
        textPrint.reset()

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        textPrint.print(screen, "Number of joysticks: {}".format(joystick_count), fg_color )
        textPrint.indent()

        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            textPrint.print(screen, "Joystick {}".format(i), fg_color )
            textPrint.indent()

            # Get the name from the OS for the controller/joystick
            name = joystick.get_name()
            textPrint.print(screen, "Joystick name: {}".format(name), fg_color )

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
            textPrint.print(screen, "Number of axes: {}".format(axes), fg_color )
            textPrint.indent()

            for i in range( axes ):
                axis = joystick.get_axis( i )
                textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis), fg_color )
            textPrint.unindent()

            buttons = joystick.get_numbuttons()
            textPrint.print(screen, "Number of buttons: {}".format(buttons), fg_color )
            textPrint.indent()

            for i in range( buttons ):
                button = joystick.get_button( i )
                textPrint.print(screen, "Button {:>2} value: {}".format(i,button), fg_color )
            textPrint.unindent()

            # Hat switch. All or nothing for direction, not like joysticks.
            # Value comes back in an array.
            hats = joystick.get_numhats()
            textPrint.print(screen, "Number of hats: {}".format(hats), fg_color )
            textPrint.indent()

            for i in range( hats ):
                hat = joystick.get_hat( i )
                textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)), fg_color )
            textPrint.unindent()

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

data = Vars()

print_recap(data)
