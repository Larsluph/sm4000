#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard

os.system("title client_sondes")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    ip = ("192.168.137.2",50003)

    print("Connecting to %s..."%(":".join(map(str,ip))))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    print("Connected!")
    server_check = True
except:
    print("unable to connect to host")
    print("ignoring...")
    server_check = False

stream = client_socket.makefile('rb')

try:
    os.system("mkdir sm4000_received_data\\probes_data")
except:
    pass

vidname = time.strftime('probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open("sm4000_received_data\\probes_data\\"+vidname,mode='w') as output_file:
    running = True
    while running:
        try:
            data = stream.readline().decode().split(",")[:-1]
            print(data)
            output_file.write(data)
            output_file.flush()
        except:
            print("can't read incoming data")

        if keyboard.is_pressed('esc'):
            running = False

        time.sleep(2)

stream.close()
client_socket.close()
print("socket closed\nDisconnected")

raise SystemExit
