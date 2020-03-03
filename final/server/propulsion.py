#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import sys
import time

import serial

import module_servos as servo

##############
#### FUNCs ###
##############

def move(com_port,dir,delay):
    servo.move(com_port, pin_id["left"], 1500-dir["left"], delay)
    servo.move(com_port, pin_id["right"], 1500+dir["right"], delay)
    servo.move(com_port, pin_id["y"], 1500+dir["y"], delay)

    return 0

def light_mgmt(com_port,lights,delay):
    servo.move(com_port, pin_id["lights"], 1000+lights, delay)

    return 0

def test_servo(com_port):
    servo_on = False
    while not(servo_on):
        data_to_send = 'ver' + chr(13)
        com_port.write(data_to_send.encode('ascii'))
        
        incoming_data = com_port.readline()
        if incoming_data.decode('ascii') == ("SSC32-V2.50USB" + chr(13)):
            print("servo initialized!")
            servo_on = True

        else:
            print("servo isn't responding\nRetrying in 5 sec...")
            time.sleep(5)

##################
## MAIN PROGRAM ##
##################

os.system("clear")

# DONE : servo set up
with serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) as com:
    pin_id = {
        "left": 0,
        "y": 1,
        "right": 2,
        "lights": 16
    }
    test_servo(com)

    # DONE : server set up
    ip = ('192.168.137.2',50001)

    server_socket = socket.socket()
    server_socket.bind(ip)
    print("server binded to '%s'" % (":".join(map(str,ip))) )
    print("Waiting for remote")
    server_socket.listen(0)
    telecommande, address1 = server_socket.accept()

    print("Connected")

    print("Waiting for instructions...")

    cmd = None
    # dir = {
    #     "powered" : False,
    #     "left" : 0,
    #     "right" : 0,
    #     "y" : 0,
    #     "light_pow" : False,
    #     "lights" : 0
    # }

    while True:
        # DONE : reception telecommande
        cmd = telecommande.recv(128).decode()
        dir = eval(cmd)
        print(dir)

        if dir == "exit":
            move(com,{"left":0,"y":0,"right":0},2000)
            light_mgmt(com,0,2000)
            break

        elif dir["powered"] == 1:
            pass

        elif dir["powered"] == 0:
            for x in ["left","y","right"]:
                dir[x] = 0

        move(com,dir,2000)

        if dir["light_pow"]:
            light_mgmt(com,dir["lights"],2000)
        else:
            light_mgmt(com,0,2000)

    telecommande.close()
    server_socket.close()

raise SystemExit
