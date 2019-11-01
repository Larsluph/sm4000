#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard
import pygame
import pygame.joystick

os.system("title client_controller")

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

def forward():
    dir["left"] = +pos * pwr
    dir["right"] = +pos * pwr

def backward():
    dir["left"] = -pos * pwr
    dir["right"] = -pos * pwr

def turn_left():
    dir["left"] = +pos * pwr
    dir["right"] = -pos * pwr

def turn_right():
    dir["left"] = -pos * pwr
    dir["right"] = +pos * pwr

# def left():
#     pass

# def right():
#     pass

def up():
    dir["y"] = +pos * pwr

def down():
    dir["y"] = -pos * pwr

def stop():
    dir["left"] = 0
    dir["right"] = 0
    dir["y"] = 0

def light_mgmt(operator,reset):
    if not(reset):
        if operator == "+":
            dir["lights"] += light_step
        else:
            dir["lights"] -= light_step
    else:
        dir["lights"] = 1000
    send()

def toggle_pwr():
    dir['powered'] = not(dir['powered'])
    # send()

def send(debug=True):
    cmd = str(dir)
    cmd = cmd + " " * (80-len(cmd))
    print(cmd)

    if debug:
        print(dir)
        print("/"+cmd+"/")

    if server_check:
        client.send(cmd.encode("Utf8"))

def stop_running():
    running = False
    if server_check:
        client.send("'exit'".encode("Utf8"))
        client.close()

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

# DONE : pygame/joystick setup
pygame.init()
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()

print("Ready")

#  hat(0) = d-pad     ( -1, 1 ) (x,y)
# axis(0) = joy x     ( -1, 1 ) (g,d)
# axis(1) = joy y     (  1,-1 ) (b,h)
# axis(2) = slider    (  1,-1 ) (low,high)
# axis(3) = joy rot   ( -1, 1 ) (indir,dir)
# 0 = -3.0517578125e-05

running = True
pwr = 0
dir = {
    "powered" : 0,
    "left" : 0,
    "right" : 0,
    "y" : 0,
    "lights" : 1000
}
pos = 100
threshold = .6
light_step = 100

axes = tuple()
buttons = tuple()

latest = dict()

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

    """if axes[1] > threshold:
        forward()

    elif axes[1] < -threshold:
        backward()

    elif axes[0] < -threshold:
        turn_left()

    elif axes[0] > threshold:
        turn_right()

    else:
        stop()

    if buttons[9] == 1:
        light_mgmt(+100)
        time.sleep(0.5)
    
    elif buttons[10] == 1:
        light_mgmt(-100)
        time.sleep(0.5)

    elif buttons[11] == 1:
        toggle_pwr()
        time.sleep(0.5)

    elif buttons[12] == 1:
        stop_running()

    if latest != dir:
        latest = dir.copy()
        send()"""

    # top
    if (-threshold < axes[0] < +threshold) and (axes[1] > +threshold):
        dir["left"] = (+pos) * pwr
        dir["right"] = (+pos) * pwr

    # top right
    elif (axes[0] > +threshold) and (axes[1] > +threshold):
        dir["left"] = (+pos * .5) * pwr
        dir["right"] = (+pos * 1.5) * pwr

    # right
    elif (axes[0] > +threshold) and (-threshold < axes[1] < +threshold):
        dir["left"] = (-pos) * pwr
        dir["right"] = (+pos) * pwr

    # bottom right
    elif (axes[0] > +threshold) and (axes[1] < -threshold):
        dir["left"] = (-pos * .5) * pwr
        dir["right"] = (-pos * 1.5) * pwr

    # bottom
    elif (-threshold < axes[0] < +threshold) and (axes[1] < -threshold):
        dir["left"] = (-pos) * pwr
        dir["right"] = (-pos) * pwr

    # bottom left
    elif (axes[0] < -threshold) and (axes[1] < -threshold):
        dir["left"] = (-pos * 1.5) * pwr
        dir["right"] = (-pos * .5) * pwr

    # left
    elif (axes[0] < -threshold) and (-threshold < axes[1] < +threshold):
        dir["left"] = (+pos) * pwr
        dir["right"] = (-pos) * pwr

    # top left
    elif (axes[0] < -threshold) and (axes[1] > +threshold):
        dir["left"] = (+pos * 1.5) * pwr
        dir["right"] = (+pos * .5) * pwr

    if axes[4][1] == +1:
        dir["y"] = (+pos) * pwr

    elif axes[4][1] == -1:
        dir["y"] = (-pos) * pwr

    elif (-threshold < axes[0] < +threshold) and (-threshold < axes[1] < +threshold) and (axes[4][1] == 0):
        stop()

    if buttons[9] == 1:
        light_mgmt("+",False)
        time.sleep(0.5)
    
    elif buttons[10] == 1:
        light_mgmt("-",False)
        time.sleep(0.5)

    elif buttons[4] == 1:
        light_mgmt(0,True)
        time.sleep(0.5)

    elif buttons[11] == 1:
        dir['powered'] = not(dir['powered'])
        time.sleep(0.5)

    elif buttons[12] == 1:
        dir["powered"] = False
        running = False

    if latest != dir:
        latest = dir.copy()
        send()
    
print("exiting...")
if server_check:
    client.send("'exit'".encode("Utf8"))
    client.close()

raise SystemExit
