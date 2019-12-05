#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import math
import os
import socket
import sys
import time

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import ms5837
import smbus
from adafruit_ads1x15.analog_in import AnalogIn

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
except:
    print("unable to bind socket\nExiting...")
    time.sleep(1)
    raise SystemExit

t0 = time.perf_counter()
t_last = 0

server_socket.send("i,t,delta_t,lvl_val,lvl_volt,pressure,temp,depth,alti".encode())

i = 1
running = True
while running:
    t = (time.perf_counter() - t0) * 1000
    delta_t = t - t_last
    t_last = t

    # niveau d'eau
    lvl_val  = water_lvl.value
    lvl_volt = water_lvl.voltage

    # pres / temp
    if sensor.read():
        pressure = sensor.pressure(ms5837.UNITS_mbar)
        temp = sensor.temperature(ms5837.UNITS_Centigrade)
        depth = sensor.depth()
        alti = sensor.altitude()
    else:
        print("can't read sensor data")

    # data = f"{i},{t},{delta_t},{lvl_val},{lvl_volt},{pressure},{temp},{depth},{alti}" + chr(13)
    data = ",".join( str(i),str(t),str(delta_t),str(lvl_val),str(lvl_volt),str(pressure),str(temp),str(depth),str(alti) ) + chr(13)
    i += 1

    try:
        server_socket.send(data.encode())
        print(data)
    except:
        print("unable to send data")
        print("check socket connection")
        running = False

receiver.close()
server_socket.close()
raise SystemExit
