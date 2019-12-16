#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard

os.system("title client_sondes")

try:
    ip = ("192.168.137.2",50003)

    print("Connecting to %s..."%(":".join(map(str,ip))))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    print("Connected!")
except:
    print("unable to connect to host\nExiting...")
    time.sleep(1)
    raise SystemExit

try:
    os.system("mkdir sm4000_received_data\\probes_data")
except:
    pass

keyboard.add_hotkey('esc',lambda: exec("global running;running=False"),suppress=False)

vidname = time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open("sm4000_received_data\\probes_data\\"+vidname,mode='w') as output_file:
    debug = True
    running = True
    while running:
        try:
            if debug:
                print("waiting for data...")
            data = i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti = client.recv(1024).decode().split(",")
            print( i,lvl_volt,bat_volt,temp,depth )
            output_file.write(data)
            output_file.flush()
        except:
            print("can't read incoming data")
            running = False

client.close()
print("socket closed\nDisconnected")

raise SystemExit
