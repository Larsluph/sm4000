#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import math
import os
import socket
import sys
import time

import keyboard

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import ms5837
import smbus
from adafruit_ads1x15.analog_in import AnalogIn

def stop_running():
    global running
    running = False

##################
## MAIN PROGRAM ##
##################

# setup ads
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

water_lvl = AnalogIn(ads, ADS.P0)

#####

# setup ms5837
sensor = ms5837.MS5837_30BA()
if not sensor.init():
    print("Sensor could not be initialized")
    raise SystemExit

if not sensor.read():
    print("Sensor read failed!")
    raise SystemExit

sensor.setFluidDensity(ms5837.DENSITY_FRESHWATER)

try:
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

i = 1
global running
running = True
while running:
    t = (time.perf_counter() - t0) * 1000
    delta_t = t - t_last
    t_last = t

    # niveau d'eau
    lvl = water_lvl.voltage

    # pres / temp
    if sensor.read():
        pressure = sensor.pressure(ms5837.UNITS_mbar)
        temp = sensor.temperature(ms5837.UNITS_Centigrade)
        depth = sensor.depth()
        alti = sensor.altitude()

    data = f"{i},{t},{delta_t} - {lvl} - {pressure},{temp},{depth},{alti}" + chr(13)
    i += 1
    if server_check:
        stream.write(data.encode())
        stream.flush()
        print('data sent')

if server_socket:
    stream.close()
    connection.close()
    server_socket.close()
