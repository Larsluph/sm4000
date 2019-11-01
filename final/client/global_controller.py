#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import sys
import time

import keyboard
import pygame
import pygame.joystick

os.system('title "sm4000 client controller"')

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

def forward():
    dir["left"] += +pos
    dir["right"] += +pos
    send()

def backward():
    dir["left"] += -pos
    dir["right"] += -pos
    send()

def turn_left():
    dir["left"] += +pos
    dir["right"] += -pos
    send()

def turn_right():
    dir["left"] += -pos
    dir["right"] += +pos
    send()

# def left():
#     pass

# def right():
#     pass

def up():
    dir["y"] += +pos
    send()

def down():
    dir["y"] += -pos
    send()

def stop():
    dir["left"] = 0
    dir["right"] = 0
    dir["y"] = 0
    send()

def light_mgmt(operator,reset):
    if not(reset):
        if operator == "+":
            dir["lights"] += light_step
        else:
            dir["lights"] -= light_step
    else:
        dir["light_pow"] = not(dir["light_pow"])
    send()

def toggle_pwr():
    dir['powered'] = not(dir['powered'])
    send()

def send(debug=False):
    cmd = str(dir)
    cmd += " " * (80-len(cmd))

    if debug:
        print(dir,pos)
        print("/"+cmd+"/")
    else:
        print(cmd)

    if server_check:
        client.send(cmd.encode("Utf8"))

##################
## MAIN PROGRAM ##
##################

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

try:
    pygame.init()
    pygame.joystick.init()
    joy = pygame.joystick.Joystick(0)
    joy.init()
    check_joy(joy)

    joytest = True if input("use keyboard ? (y/n)") == "n" else False
except:
    print(sys.exc_info())
    joytest = False

running = True
pwr = 0
dir = {
    "powered" : False,
    "left" : 0,
    "right" : 0,
    "y" : 0,
    "light_pow" : False,
    "lights" : 0
}
pos = 100
threshold = .6
light_step = 100

axes = tuple()
buttons = tuple()

latest = dict()

if joytest:
    """ joy_control """
    print("\njoystick ready")
    print("Waiting for instructions...")
    while running:
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

        pwr = int(abs(axes[2] - 1) * 20) / 10

        # top
        if (-threshold < axes[0] < +threshold) and (axes[1] > +threshold):
            dir["left"] = (+pos) * pwr
            dir["right"] = (+pos) * pwr

        # top right
        elif (axes[0] > +threshold) and (axes[1] > +threshold):
            dir["left"] = (+pos * 1.5) * pwr
            dir["right"] = (+pos * .5) * pwr

        # right
        elif (axes[0] > +threshold) and (-threshold < axes[1] < +threshold):
            dir["left"] = (-pos) * pwr
            dir["right"] = (+pos) * pwr

        # bottom right
        elif (axes[0] > +threshold) and (axes[1] < -threshold):
            dir["left"] = (-pos * 1.5) * pwr
            dir["right"] = (-pos * .5) * pwr

        # bottom
        elif (-threshold < axes[0] < +threshold) and (axes[1] < -threshold):
            dir["left"] = (-pos) * pwr
            dir["right"] = (-pos) * pwr

        # bottom left
        elif (axes[0] < -threshold) and (axes[1] < -threshold):
            dir["left"] = (-pos * .5) * pwr
            dir["right"] = (-pos * 1.5) * pwr

        # left
        elif (axes[0] < -threshold) and (-threshold < axes[1] < +threshold):
            dir["left"] = (+pos) * pwr
            dir["right"] = (-pos) * pwr

        # top left
        elif (axes[0] < -threshold) and (axes[1] > +threshold):
            dir["left"] = (+pos * .5) * pwr
            dir["right"] = (+pos * 1.5) * pwr

        if axes[4][1] == +1:
            dir["y"] = (+pos) * pwr

        elif axes[4][1] == -1:
            dir["y"] = (-pos) * pwr

        elif (-threshold < axes[0] < +threshold) and (-threshold < axes[1] < +threshold) and (axes[4][1] == 0):
            dir["left"] = 0
            dir["right"] = 0
            dir["y"] = 0

        if buttons[9] == 1:
            dir["lights"] += light_step
            time.sleep(0.5)
        
        elif buttons[10] == 1:
            dir["lights"] -= light_step
            time.sleep(0.5)

        elif buttons[4] == 1:
            dir["light_pow"] = not(dir["light_pow"])
            time.sleep(0.5)

        elif buttons[11] == 1:
            dir['powered'] = not(dir['powered'])
            time.sleep(0.5)

        elif buttons[12] == 1:
            print("stopping transmission...")
            dir["powered"] = False
            running = False

        if latest != dir:
            latest = dir.copy()
            send()
else:
    """ key_control """
    keyboard.add_hotkey('z',forward)
    keyboard.add_hotkey('s',backward)
    keyboard.add_hotkey('q',turn_left)
    keyboard.add_hotkey('d',turn_right)
    keyboard.add_hotkey('shift',up)
    keyboard.add_hotkey('ctrl',down)
    keyboard.add_hotkey('space',stop)
    keyboard.add_hotkey('enter',toggle_pwr)
    keyboard.add_hotkey('*',light_mgmt,args=["+",False])
    keyboard.add_hotkey('ù',light_mgmt,args=["-",False])
    keyboard.add_hotkey('$',light_mgmt,args=[0,True])

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
