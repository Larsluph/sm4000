#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import math
import os
import socket
import sys
import time

import keyboard

import board
import busio
import ms5837

###########
## FUNCs ##
###########

address = 0x68
bus = smbus.SMBus(1)

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

try:
    # DONE : server set up
    ip = ('192.168.137.2',50003)
    server_socket = socket.socket()
    server_socket.bind(ip)
    print("server binded to '%s'" % (":".join(map(str,ip))) )
    print("Waiting for receiver")
    server_socket.listen(0)
    receiver, address = server_socket.accept()
    print("Connected")
    server_check = True
except:
    server_check = False

if server_check:
    stream = receiver.makefile('wb')

t0 = time.perf_counter()
t_last = 0
keyboard.add_hotkey('esc', stop_running)

i = 0
running = True
while running:
    t = (time.perf_counter() - t0) * 1000
    delta_t = t - t_last
    t_last = t
    data = str(i) + ',' + str(t) + ',' + str(delta_t) + chr(13)
    i = i + 1
    if server_check:
        stream.write(data.encode())
        stream.flush()
        print('data sent')

if server_socket:
    stream.close()
    connection.close()
    server_socket.close()
