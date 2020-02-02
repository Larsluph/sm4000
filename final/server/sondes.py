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
from modules import bme280, ms5837
from modules.adafruit_ads1x15 import ads1115 as ADS
from modules.adafruit_ads1x15.analog_in import AnalogIn
from modules.AtlasI2C import AtlasI2C

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

checks = {
  "networking"    : True,
  "water_lvl"     : True,
  "battery_cells" : True,
  "ext_pres_temp" : True,
  "oxygen"        : True,
  "int_pres_temp" : True
}

#####
#####

# DONE: setup ads
i2c = busio.I2C(board.SCL, board.SDA)
if checks["water_lvl"]:
  ads_water = ADS.ADS1115(i2c,address=i2c_address["ads_water"])
  water_lvl = AnalogIn(ads_water, ADS.P0)

if checks["battery_cells"]:
  ads_battery = ADS.ADS1115(i2c,address=i2c_address["ads_battery"])
  # battery_cells = [AnalogIn(ads_battery, i) for i in range(4)]
  battery_cells = AnalogIn(ads_battery, ADS.P3)

# 32768 limite batterie +/-
# cap = [3.00:4.20]
# cap = round(bat,3)-3
# cap = round(cap/1.2*100,2)

if checks["water_lvl"]:
  if not(water_lvl.value):
    print("water_lvl ads could not be initialized")

if checks["battery_cells"]:
  if not(battery_cells.value):
    print("battery_cells ads could not be initialized")

if checks["water_lvl"] or checks["battery_cells"]:
  print("ADS check successful")
else:
  print("ignoring ADSs...")

#####
#####

# DONE: setup ms5837 (pres_temp_external)
if checks["ext_pres_temp"]:
  ext_pres_temp_sensor = ms5837.MS5837_30BA()
  if not ext_pres_temp_sensor.init():
    print("ext_pres_temp_sensor could not be initialized")
    raise SystemExit

  if not ext_pres_temp_sensor.read():
    print("ext_pres_temp_sensor read failed!")
    raise SystemExit

  print("ext_pres_temp_sensor initialized")

  ext_pres_temp_sensor.setFluidDensity(ms5837.DENSITY_FRESHWATER)
else:
  print("ignoring ext_pres_temp...")

#####
#####

#TO_CHECK: setup dissolved oxygen probe
if checks["oxygen"]:
  oxygen = AtlasI2C(address=0x61,name="dissolved oxygen probe")
  oxygen.query("Plock,1") # enable protocol lock (locks device to I2C mode)
  oxygen.query("L,1")
  print(oxygen.query("i")) # ask for probe information
  print("dissolved oxygen probe initialized")
  print("Calibrating...")
  oxygen.query("Cal") # calibrate to atmospheric oxygen levels
  print("Calibration complete")
else:
  print("ignoring dissolved_oxygen...")

#####
#####

#TO_CHECK: setup grove bme280 (pres_temp_internal)
if checks["int_pres_temp"]:
  bme280.setup() # setup probe connection
  bme280.setReferencePressure(bme280.readFloatPressure()) # set reference for altitude calculation
  
  # °C temp     : bme280.readTempC()
  # °F temp     : bme280.readTempF()
  # % humidity  : bme280.readFloatHumidity()
  # Pa pressure : bme280.readFloatPressure()
  # m alti      : bme280.readFloatAltitudeMeters()
  # feet alti   : bme280.readFloatAltitudeFeet()
else:
  print("ignoring int_pres_temp...")

#####
#####

# DONE: setup server
if checks["networking"]:
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
else:
  print("ignoring socket connection...")

t0 = time.perf_counter()
t_last = 0

i = 1
running = True
while running:
  values = dict()
  """
  values = {
    "i":0,
    "t":0,
    "delta_t":0,
    "lvl_val":0,
    "lvl_volt":0,
    "lvl_percent":0,
    "bat_val":0,
    "bat_volt":0,
    "bat_percent":0,
    "ext_pressure":0,
    "ext_temp":0,
    "ext_depth":0,
    "ext_alti":0,
    "dissolved_oxygen":0,
    "int_pressure":0,
    "int_temp":0,
    "int_humidity":0
  }
  """

  values["i"] = i
  values["t"] = t = (time.perf_counter() - t0) * 1000
  values["delta_t"] = t - t_last
  t_last = t

  ### niveau d'eau
  if checks["water_lvl"]:
    values["lvl_val"]  = water_lvl.value
    values["lvl_volt"] = water_lvl.voltage
    values["lvl_percent"] = round(round(values["lvl_volt"],3)/3.0*100,2)

  ### cellules batterie
  if checks["battery_cells"]:
    # bat_val  = [battery_cells[i].value for i in range(4)]
    # bat_volt = [battery_cells[i].voltage for i in range(4)]
    values["bat_val"]  = battery_cells.value
    values["bat_volt"] = battery_cells.voltage
    values["bat_percent"] = round(round(values["bat_volt"],3)-3/1.2*100,2)

  ### pres / temp external
  if checks["ext_pres_temp"]:
    if ext_pres_temp_sensor.read():
      values["ext_pressure"] = ext_pres_temp_sensor.pressure(ms5837.UNITS_mbar)
      values["ext_temp"] = ext_pres_temp_sensor.temperature(ms5837.UNITS_Centigrade)
      values["ext_depth"] = ext_pres_temp_sensor.depth()
      values["ext_alti"] = ext_pres_temp_sensor.altitude()
    else:
      print("can't read sensor data")
      values["ext_pressure"]=values["ext_pressure"]=values["ext_temp"]=values["ext_depth"]=values["ext_alti"] = 0

  ### dissolved oxygen
  if checks["oxygen"]:
    oxygen.query(f"T,{values["ext_temp"]}") # temperature compensation
    oxygen.query(f"P,{ext_pres_temp_sensor.pressure(ms5837.UNITS_kPa)}") # pressure compensation
    values["dissolved_oxygen"] = oxygen.query("R")

  ### pres / temp internal
  if checks["int_pres_temp"]:
    values["int_pressure"] = bme280.readFloatPressure()
    values["int_temp"] = bme280.readTempC()
    values["int_humidity"] = bme280.readFloatHumidity()
    values["int_alti"] = bme280.readFloatAltitudeMeters()

  data = str(values)
  i += 1

  if checks["networking"]:
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
  else:
    print(data)
  time.sleep(2)

oxygen.close()

receiver.close()
server_socket.close()
raise SystemExit
