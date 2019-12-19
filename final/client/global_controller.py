﻿#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import sys
import time

import keyboard
import pygame
import pygame.joystick

os.system('title sm4000 client controller')

############
## CLASSs ##
############

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
        check_joy(self.joy)

        self.boosted = True

        self.latest = self.dir.copy()

        self.axes = tuple()
        self.buttons = tuple()

###########
## FUNCs ##
###########
def check_joy(joy):
    pygame.event.get()
    print(
        f"id       {str(joy.get_id())}",
        f"name     {str(joy.get_name())}",
        f"axes     {str(joy.get_numaxes())}",
        f"buttons  {str(joy.get_numbuttons())}",
        f"hats     {str(joy.get_numhats())}",
        f"balls    {str(joy.get_numballs())}",
    sep='\n')
    time.sleep(1)

def forward(data):
    data.dir["left"] += +data.pos
    data.dir["right"] += +data.pos
    send(data)

def backward(data):
    data.dir["left"] += -data.pos
    data.dir["right"] += -data.pos
    send(data)

def turn_left(data):
    data.dir["left"] += -data.pos
    data.dir["right"] += +data.pos
    send(data)

def turn_right(data):
    data.dir["left"] += +data.pos
    data.dir["right"] += -data.pos
    send(data)

# def left(data):
#     pass

# def right(data):
#     pass

def up(data):
    data.dir["y"] += +data.pos
    send(data)

def down(data):
    data.dir["y"] += -data.pos
    send(data)

def stop(data):
    data.dir["left"] = 0
    data.dir["right"] = 0
    data.dir["y"] = 0
    send(data)

def light_mgmt(data,operator,reset):
    if not(reset):
        if operator == "+":
            data.dir["lights"] += data.light_step
        else:
            data.dir["lights"] -= data.light_step
    else:
        data.dir["light_pow"] = not(data.dir["light_pow"])
    send(data)

def toggle_pwr(data):
    data.dir['powered'] = not(data.dir['powered'])
    send(data)

def send(data):
    cmd = str(data.dir)
    cmd += " " * (128-len(cmd))

    if server_check:
        client.send(cmd.encode("Utf8"))

    print(data.dir)

##################
## MAIN PROGRAM ##
##################

data = Vars()

try:
    ip = ("192.168.137.2",50001)

    print("Connecting to %s..."%(":".join(map(str,ip))))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    print("Connected!")
    server_check = True
except:
    print("unable to connect to host")
    print("ignoring...")
    server_check = False

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() != 0:
    data.joy_vars()
    joytest = True if input("use keyboard ? (y/n)\n") == "n" else False
else:
    joytest = False

if joytest:
    """ joy_control """
    print("\njoystick ready")
    print("Waiting for instructions...")

    while data.running:
        pygame.event.get()
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

        if not(data.boosted):
            for x in ["x","y"]:
                data.pwr[x] /= 2.5

        # top
        if data.buttons[1] == 0:
            if (-data.threshold < data.axes[0] < +data.threshold) and (data.axes[1] > +data.threshold):
                data.dir["left"] = (+data.pos) * data.pwr["y"]
                data.dir["right"] = (+data.pos) * data.pwr["y"]

            # top right
            elif (data.axes[0] > +data.threshold) and (data.axes[1] > +data.threshold):
                data.dir["left"] = (+data.pos * 1.5) * data.pwr["x"]
                data.dir["right"] = (+data.pos * .5) * data.pwr["x"]

            # right
            elif (data.axes[0] > +data.threshold) and (-data.threshold < data.axes[1] < +data.threshold):
                data.dir["left"] = (+data.pos) * data.pwr["x"]
                data.dir["right"] = (-data.pos) * data.pwr["x"]

            # bottom right
            elif (data.axes[0] > +data.threshold) and (data.axes[1] < -data.threshold):
                data.dir["left"] = (-data.pos * 1.5) * data.pwr["x"]
                data.dir["right"] = (-data.pos * .5) * data.pwr["x"]

            # bottom
            elif (-data.threshold < data.axes[0] < +data.threshold) and (data.axes[1] < -data.threshold):
                data.dir["left"] = (-data.pos) * data.pwr["y"]
                data.dir["right"] = (-data.pos) * data.pwr["y"]

            # bottom left
            elif (data.axes[0] < -data.threshold) and (data.axes[1] < -data.threshold):
                data.dir["left"] = (-data.pos * .5) * data.pwr["x"]
                data.dir["right"] = (-data.pos * 1.5) * data.pwr["x"]

            # left
            elif (data.axes[0] < -data.threshold) and (-data.threshold < data.axes[1] < +data.threshold):
                data.dir["left"] = (-data.pos) * data.pwr["x"]
                data.dir["right"] = (+data.pos) * data.pwr["x"]

            # top left
            elif (data.axes[0] < -data.threshold) and (data.axes[1] > +data.threshold):
                data.dir["left"] = (+data.pos * .5) * data.pwr["x"]
                data.dir["right"] = (+data.pos * 1.5) * data.pwr["x"]

            if data.axes[4][1] == +1:
                data.dir["y"] = +data.pos

            elif data.axes[4][1] == -1:
                data.dir["y"] = -data.pos

            elif (-data.threshold < data.axes[0] < +data.threshold) and (-data.threshold < data.axes[1] < +data.threshold) and (data.axes[4][1] == 0):
                data.dir["left"] = 0
                data.dir["right"] = 0
                data.dir["y"] = 0

        if data.buttons[2] == 1:
            data.boosted = not(data.boosted)
            time.sleep(0.5)

        elif data.buttons[4] == 1:
            data.dir["light_pow"] = not(data.dir["light_pow"])
            time.sleep(0.5)

        elif data.buttons[11] == 1:
            data.dir['powered'] = not(data.dir['powered'])
            time.sleep(0.5)

        elif data.buttons[12] == 1:
            print("stopping transmission...")
            data.dir["powered"] = False
            data.running = False

        data.dir["lights"] = data.light_step * data.pwr["lights"]

        if data.latest != data.dir:
            data.latest = data.dir.copy()
            send(data)
else:
    data.key_vars()
    """ key_control """
    keyboard.add_hotkey('z',forward,args=[data],suppress=True)
    keyboard.add_hotkey('s',backward,args=[data],suppress=True)
    keyboard.add_hotkey('q',turn_left,args=[data],suppress=True)
    keyboard.add_hotkey('d',turn_right,args=[data],suppress=True)
    keyboard.add_hotkey('shift',up,args=[data],suppress=True)
    keyboard.add_hotkey('ctrl',down,args=[data],suppress=True)
    keyboard.add_hotkey('space',stop,args=[data],suppress=True)
    keyboard.add_hotkey('enter',toggle_pwr,args=[data],suppress=True)
    keyboard.add_hotkey('*',light_mgmt,args=[data,"+",False],suppress=True)
    keyboard.add_hotkey('ù',light_mgmt,args=[data,"-",False],suppress=True)
    keyboard.add_hotkey('$',light_mgmt,args=[data,0,True],suppress=True)

    print("\nkeyboard ready")
    print("Waiting for instructions...")
    keyboard.wait('esc')

    print("stopping transmission...")
    keyboard.clear_all_hotkeys()

if server_check:
    client.send("'exit'".encode("Utf8"))
    client.close()

print("END OF PROGRAM")
time.sleep(0.5)

raise SystemExit
