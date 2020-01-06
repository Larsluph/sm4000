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
ads_water = ADS.ADS1115(i2c,address=0x48)
# ads_battery = ADS.ADS1115(i2c,address=0x49)
# 32768 limite batterie +/-
# cap = [3.00:4.20]

water_lvl = AnalogIn(ads_water, ADS.P0)
# battery_cells = [AnalogIn(ads_battery, i) for i in range(4)]
battery_cells = AnalogIn(ads_water, ADS.P3)

#####

# setup ads
if not(water_lvl.value):
  print("water_lvl ads could not be initialized")

if not(battery_cells.value):
  print("battery_cells ads could not be initialized")

print("ADSs check successful")

# setup ms5837
sensor = ms5837.MS5837_30BA()
if not sensor.init():
  print("Sensor could not be initialized")
  raise SystemExit

if not sensor.read():
  print("Sensor read failed!")
  raise SystemExit

print("Sensor initialized")

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

i = 1
running = True
while running:
  t = (time.perf_counter() - t0) * 1000
  delta_t = t - t_last
  t_last = t

  ### niveau d'eau
  lvl_val  = water_lvl.value
  lvl_volt = water_lvl.voltage

  ### cellules batterie
  # bat_val  = [battery_cells[i].value for i in range(4)]
  # bat_volt = [battery_cells[i].voltage for i in range(4)]
  bat_val  = battery_cells.value
  bat_volt = battery_cells.voltage

  ### pres / temp
  if sensor.read():
    pressure = sensor.pressure(ms5837.UNITS_mbar)
    temp = sensor.temperature(ms5837.UNITS_Centigrade)
    depth = sensor.depth()
    alti = sensor.altitude()
  else:
    pressure=temp=depth=alti=0
    print("can't read sensor data")

  data = ",".join( [ str(x) for x in [i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti] ] ) + "\n"
  i += 1

  try:
    receiver.send(data.encode())
    print("data sent")
  except IOError:
    # broken pipe
    print("unable to send data : broken pipe error")
    print("check socket connection")
    running = False
  except Exception as e:
    print(e)
    print("error while sending data. ignoring...")

  time.sleep(2)

receiver.close()
server_socket.close()
raise SystemExit
