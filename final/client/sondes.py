#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard

os.system("title client_sondes")

def stop_running():
    global running
    running = False

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

keyboard.add_hotkey('esc',stop_running,suppress=False)

vidname = time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open("sm4000_received_data\\probes_data\\"+vidname,mode='w') as output_file:
    running = True
    while running:
        try:
            # i,lvl_volt,bat_volt,pressure,temp,depth
            data = client.recv(1024).decode().split(",")
            print(data)
            output_file.write(data)
            output_file.flush()
        except:
            print("can't read incoming data")
            running = False

client.close()
print("socket closed\nDisconnected")

raise SystemExit
