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

keyboard.add_hotkey('esc',lambda: exec("running=False"),suppress=True)

vidname = time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open("sm4000_received_data\\probes_data\\"+vidname,mode='w') as output_file:
    datatags = client.recv(1024).decode()
    print(datatags,file=output_file,flush=True)
    running = True
    while running:
        try:
            data = client.recv(1024).decode()
            print(datatags)
            print(data.split(","))
            output_file.write(data)
            output_file.flush()
        except:
            print("can't read incoming data")
            time.sleep(1)

client.close()
print("socket closed\nDisconnected")

raise SystemExit
