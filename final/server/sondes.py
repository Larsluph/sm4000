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
  "networking"    : 1,
  "water_lvl"     : 0,
  "battery_cells" : 0,
  "ext_pres_temp" : 1,
  "oxygen"        : 1,
  "int_pres_temp" : 1
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
  tds_meter = AnalogIn(ads_battery,ADS.P0)
  # battery_cells = [AnalogIn(ads_battery, i) for i in range(4)]
  battery_cells = AnalogIn(ads_battery, ADS.P3)

# cap = [3.00:4.20]
# cap = round(bat,3)-3
# cap = round(cap/1.2*100,2)

if checks["water_lvl"]:
  if not(water_lvl.value):
    print("water_lvl ads could not be initialized")

if checks["battery_cells"]:
  if not(battery_cells.value):
    print("battery_cells couldn't be initialized")
  if not(tds_meter.value):
    print("TDS_meter couldn't be initialized")

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
    print("ext_pres_temp_sensor couldn't be initialized")
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

#DONE: setup dissolved oxygen probe
if checks["oxygen"]:
  oxygen = AtlasI2C(address=0x61)
  oxygen.query("Plock,1") # enable protocol lock (locks device to I2C mode)
  oxygen.query("L,1")
  print(oxygen.query("i")) # ask for probe information
  print("dissolved oxygen probe initialized")
  print("Calibrating...")
  oxygen.query("Cal") # calibrate to atmospheric oxygen levels
  oxygen.query("R") # first read to make sure reading is working
  print("Calibration complete")
else:
  print("ignoring dissolved_oxygen...")

#####
#####

#DONE: setup grove bme280 (pres_temp_internal)
if checks["int_pres_temp"]:
  bme280.setup() # setup probe connection
  bme280.readTempC() # needed to read pressure
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

  values["i"] = i
  values["t"] = t = round(time.perf_counter() - t0,3)
  values["delta_t"] = round(t - t_last,3)
  t_last = t

  ### niveau d'eau
  if checks["water_lvl"]:
    values["lvl_val"]  = water_lvl.value
    values["lvl_volt"] = water_lvl.voltage
    values["lvl_percent"] = round(values["lvl_volt"]/3.0*100,2)

  ### TDS / cellules batterie
  if checks["battery_cells"]:
    values["tds_volt"] = tds_meter.voltage
    # bat_volt = [battery_cells[i].voltage for i in range(4)]
    values["bat_volt"] = battery_cells.voltage
    values["bat_percent"] = round(round(values["bat_volt"],3)-3/1.2*100,2)

  ### pres / temp external
  if checks["ext_pres_temp"]:
    if ext_pres_temp_sensor.read():
      values["ext_pressure"] = round(ext_pres_temp_sensor.pressure(ms5837.UNITS_mbar),2)
      values["ext_temp"] = round(ext_pres_temp_sensor.temperature(ms5837.UNITS_Centigrade),2)
      values["ext_depth"] = round(ext_pres_temp_sensor.depth(),2)
      values["ext_alti"] = round(ext_pres_temp_sensor.altitude(),2)
    else:
      print("can't read ext_pres_temp data")

  ### dissolved oxygen
  if checks["oxygen"]:
    if checks["ext_pres_temp"]:
      oxygen.query( "T," + str(ext_pres_temp_sensor.temperature(ms5837.UNITS_Centigrade)) ) # temperature compensation
      oxygen.query( "P," + str(ext_pres_temp_sensor.pressure(ms5837.UNITS_kPa))) # pressure compensation
    values["dissolved_oxygen"] = oxygen.query("R").rstrip("\x00").lstrip("Suces: ")

  ### pres / temp internal
  if checks["int_pres_temp"]:
    values["int_temp"] = round(bme280.readTempC(),2)
    values["int_pressure"] = round(bme280.readFloatPressure()/100,2)
    values["int_humidity"] = round(bme280.readFloatHumidity(),2)

  data = str(values)
  i += 1

  if checks["networking"]:
    try:
      receiver.send(data.encode())
      print("data sent")
    except IOError:
      # broken pipe
      print("unable to send data : "+str(sys.exc_info()[1]))
      print("check socket connection")
      running = False
    except:
      print(str(sys.exc_info()[0])+" : "+str(sys.exc_info()[1]))
      print("error while sending data. ignoring...")
      receiver.send("can't read probes data (server error)".encode())
  else:
    print(data)
  time.sleep(2)

oxygen.close()

receiver.close()
server_socket.close()
raise SystemExit
