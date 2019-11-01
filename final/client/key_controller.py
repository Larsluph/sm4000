#!/usr/bin/env python
#-*- coding:Utf-8 -*-

import socket, keyboard, os

os.system("title client_controller")

###########
## FUNCs ##
###########

def forward():
    global dir, pos
    dir[0] += pos
    dir[1] += pos
    send()

def backward():
    global dir, pos
    dir[0] -= pos
    dir[1] -= pos
    send()

def left():
    global dir, pos
    dir[0] += pos
    dir[1] -= pos
    send()

def right():
    global dir, pos
    dir[0] -= pos
    dir[1] += pos
    send()

def up():
    global dir, pos
    dir[2] += pos
    send()

def down():
    global dir, pos
    dir[2] -= pos
    send()

def stop():
    global dir
    dir = [0, 0, 0]
    send()

def toggle_pwr():
    global powered
    powered = not(powered)
    send()

def send(debug=False):
    global powered, dir, pos, client
    cmd = str([powered, dir])
    cmd += " " * (27-len(cmd))
    print(cmd)
    
    if debug:
        print(dir,pos,powered)
        
    if server_check:
        client.send(cmd.encode("Utf8"))

def stop_running():
    keyboard.clear_all_hotkeys()
    if server_check:
        client.send("'exit'".encode("Utf8"))
        client.close()
    quit()

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
    print("ignoring")
    server_check = False

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
latest = dict()

keyboard.add_hotkey('z',forward)
keyboard.add_hotkey('s',backward)
keyboard.add_hotkey('q',left)
keyboard.add_hotkey('d',right)
keyboard.add_hotkey('shift',up)
keyboard.add_hotkey('ctrl',down)
keyboard.add_hotkey('space',stop)
keyboard.add_hotkey('enter',toggle_pwr)

print("Ready")
keyboard.wait('esc')

stop_running()