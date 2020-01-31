#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import math
import os
import socket
import sys
import time

import board
import busio
import smbus
from modules.AtlasI2C import AtlasI2C
from modules.adafruit_ads1x15 import ads1115 as ADS
from modules import ms5837
from modules.adafruit_ads1x15.analog_in import AnalogIn

###########
## FUNCs ##
###########

def print_oxygen_devices(device_list, device):
    for i in device_list:
        if(i == device):
            print("--> " + i.get_device_info())
        else:
            print(" -- " + i.get_device_info())

def get_oxygen_devices():
  device = AtlasI2C()
  device_address_list = device.list_i2c_devices()
  device_list = []

  for i in device_address_list:
    device.set_i2c_address(i)
    response = device.query("I")
    moduletype = response.split(",")[1] 
    response = device.query("name,?").split(",")[1]
    device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
  return device_list

##################
## MAIN PROGRAM ##
##################

i2c_address = {
  "ads_water": 0x48,
  "ads_battery": 0x49,
  "oxygen": 0x61,
  "pres_temp_external": 0x76,
  "pres_temp_internal": 0x77
}

#####

# DONE: setup ads
i2c = busio.I2C(board.SCL, board.SDA)
ads_water = ADS.ADS1115(i2c,address=i2c_address["ads_water"])
ads_battery = ADS.ADS1115(i2c,address=i2c_address["ads_battery"])
# 32768 limite batterie +/-
# cap = [3.00:4.20]

water_lvl = AnalogIn(ads_water, ADS.P0)
# battery_cells = [AnalogIn(ads_battery, i) for i in range(4)]
battery_cells = AnalogIn(ads_battery, ADS.P3)

if not(water_lvl.value):
  print("water_lvl ads could not be initialized")

if not(battery_cells.value):
  print("battery_cells ads could not be initialized")

print("ADSs check successful")

#####

# DONE: setup ms5837 (pres_temp_external)
ext_pres_temp_sensor = ms5837.MS5837_30BA()
if not ext_pres_temp_sensor.init():
  print("ext_pres_temp_sensor could not be initialized")
  raise SystemExit

if not ext_pres_temp_sensor.read():
  print("ext_pres_temp_sensor read failed!")
  raise SystemExit

print("ext_pres_temp_sensor initialized")

ext_pres_temp_sensor.setFluidDensity(ms5837.DENSITY_FRESHWATER)

#####

#TO_CHECK: setup dissolved oxygen probe
oxygen = AtlasI2C(address=0x61,name="dissolved oxygen probe")
print(oxygen.query("i")) # ask for probe information
print("dissolved oxygen probe initialized")

#####

#TO_DO: setup grove bme280 (pres_temp_internal)
# int_pres_temp_sensor = 

#####

# DONE: setup server
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
  if ext_pres_temp_sensor.read():
    pressure = ext_pres_temp_sensor.pressure(ms5837.UNITS_mbar)
    temp = ext_pres_temp_sensor.temperature(ms5837.UNITS_Centigrade)
    depth = ext_pres_temp_sensor.depth()
    alti = ext_pres_temp_sensor.altitude()
  else:
    print("can't read sensor data")
    pressure=temp=depth=alti = 0

  data = ",".join( [ str(x) for x in [i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti] ] ) + "\n"
  i += 1

  try:
    receiver.send(data.encode())
    print("data sent")
  except IOError:
    # broken pipe
    print(f"unable to send data : {sys.exc_info()[1]}")
    print("check socket connection")
    running = False
  except:
    print(f"{sys.exc_info()[0]} : {sys.exc_info()[1]}")
    print("error while sending data. ignoring...")
    receiver.send("can't read probes data (server error)".encode())

  time.sleep(2)

receiver.close()
server_socket.close()
raise SystemExit
