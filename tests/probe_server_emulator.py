#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import random
import socket
import sys
import time

checks = {
  "networking"    : 1,
  "water_lvl"     : 1,
  "battery_cells" : 1,
  "ext_pres_temp" : 1,
  "oxygen"        : 1,
  "int_pres_temp" : 1
}

try:
  ip = ("192.168.0.31",50001)

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
  print("reading values...")
  values = dict()

  values["i"] = i
  values["t"] = t = round(time.perf_counter() - t0,3)
  values["delta_t"] = round(t - t_last,3)
  t_last = t

  ### niveau d'eau
  if checks["water_lvl"]:
    values["lvl_val"]  = random.randint(0,65656)
    values["lvl_volt"] = random.randint(0,3_000)/1000
    values["lvl_percent"] = round(values["lvl_volt"]/3*100,2)

  ### cellules batterie
  if checks["battery_cells"]:
    # bat_val  = [battery_cells[i].value for i in range(4)]
    # bat_volt = [battery_cells[i].voltage for i in range(4)]
    values["bat_val"]  = random.randint(0,65656)
    values["bat_volt"] = random.randint(3_000,4_200)/1000
    values["bat_percent"] = round(round(values["bat_volt"]-3,3)/1.2*100,2)

  ### pres / temp external
  if checks["ext_pres_temp"]:
    values["ext_pressure"] = random.randint(1000_00,1500_00)
    values["ext_temp"] = random.randint(5_00,25_00)/100
    values["ext_depth"] = round((values["ext_pressure"]*100-101300)/(997*9.80665),2)
    values["ext_alti"] = round((1-pow((values["ext_pressure"]/1013.25),.190284))*145366.45*.3048,2)

  ### dissolved oxygen
  if checks["oxygen"]:
    values["dissolved_oxygen"] = 'Success: 9.09\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

  ### pres / temp internal
  if checks["int_pres_temp"]:
    values["int_temp"] = random.randint(18_00,45_00)/100
    values["int_pressure"] = random.randint(1000_00,1500_00)
    values["int_humidity"] = random.randint(0,100_00)/100

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
  time.sleep(random.randint(3_000,4_000)/1000)

receiver.close()
server_socket.close()
raise SystemExit
