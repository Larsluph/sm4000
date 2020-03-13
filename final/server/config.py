#!/usr/bin/env python3
#-*- coding:utf-8 -*-

class propulsion:
  ip = ('192.168.137.2',50001)

  pin_id = {
    "left": 0,
    "y": 1,
    "right": 2,
    "lights": 16
  }

class camera:
  ip = ('192.168.137.2',50002)

class sondes:
  ip = ('192.168.137.2',50003)

  probes_checks = {
    "networking"    : 1,
    "water_lvl"     : 0,
    "battery_cells" : 1,
    "ext_pres_temp" : 1,
    "oxygen"        : 1,
    "int_pres_temp" : 1
  }

  i2c_address = {
    "ads_water": 0x48,
    "ads_battery": 0x49,
    "oxygen": 0x61,
    "pres_temp_external": 0x76,
    "pres_temp_internal": 0x77
  }
